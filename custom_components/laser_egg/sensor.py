from logging import getLogger
from datetime import timedelta

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.util import Throttle

_LOGGER = getLogger(__name__)

CONF_DEVICE_ID = "device_id"
CONF_AQI_STANDARD = "aqi_standard"

AQI_SCALE = {
    "CN": [0, 50, 100, 150, 200, 300, 400, 500],
    "IN": [0, 50, 100, 200, 300, 400, 500],
    "US": [0, 50, 100, 150, 200, 300, 500],
    "EU": [0, 25, 50, 75, 100, 500]
}

AQI_LEVEL = {
    "CN": [
        {"label": "Good", "icon": "mdi:emoticon-excited"},
        {"label": "Satisfactory", "icon": "mdi:emoticon-cool"},
        {"label": "Moderate", "icon": "mdi:emoticon-happy"},
        {"label": "Unhealthy for sensitive groups", "icon": "mdi:emoticon-neutral"},
        {"label": "Unhealthy", "icon": "mdi:emoticon-sad"},
        {"label": "Very unhealthy", "icon": "mdi:emoticon-dead"},
        {"label": "Hazardous", "icon": "mdi:biohazard"}
    ],
    "IN": [
        {"label": "Good", "icon": "mdi:emoticon-excited"},
        {"label": "Satisfactory", "icon": "mdi:emoticon-happy"},
        {"label": "Moderately polluted", "icon": "mdi:emoticon-neutral"},
        {"label": "Poor", "icon": "mdi:emoticon-sad"},
        {"label": "Very poor", "icon": "mdi:emoticon-dead"},
        {"label": "Severe", "icon": "mdi:biohazard"}
    ],
    "US": [
        {"label": "Good", "icon": "mdi:emoticon-excited"},
        {"label": "Moderate", "icon": "mdi:emoticon-happy"},
        {"label": "Unhealthy for sensitive groups", "icon": "mdi:emoticon-neutral"},
        {"label": "Unhealthy", "icon": "mdi:emoticon-sad"},
        {"label": "Very unhealthy", "icon": "mdi:emoticon-dead"},
        {"label": "Hazardous", "icon": "mdi:biohazard"}
    ],
    "EU": [
        {"label": "Good", "icon": "mdi:emoticon-excited"},
        {"label": "Fair", "icon": "mdi:emoticon-happy"},
        {"label": "Moderate", "icon": "mdi:emoticon-neutral"},
        {"label": "Poor", "icon": "mdi:emoticon-sad"},
        {"label": "Very poor", "icon": "mdi:emoticon-dead"}
    ]
}

PM10_SCALE = {
  "CN": [0, 50, 150, 250, 350, 420, 500, 600],
  "IN": [0, 50, 100, 250, 350, 430, 600],
  "US": [0, 54, 154, 254, 354, 424, 604],
  "EU": [0, 20, 35, 50, 100, 1200]
}

PM25_SCALE = {
  "CN": [0, 35, 75, 115, 150, 250, 350, 500],
  "IN": [0, 30, 60,  90, 120, 250, 500],
  "US": [0, 12, 35.4, 55.4, 150.4, 250.4, 500.4],
  "EU": [0, 10, 20, 25, 50, 800]
}

TVOC_SCALE = {
    "CN": [125, 200, 300, 450, 600, 1000, 1500, 2000]
}

DEFAULT_DEVICE_NAME = "Laser Egg"
SENSORS = [
    ("pm25", "PM2.5", "mdi:weather-windy", "µg/m3"),
    ("pm10", "PM10", "mdi:weather-windy", "µg/m3"),
    ("rtvoc", "TVOC", "mdi:weather-windy", "ppb"),
    ("aqi_level", "Air Quality Level", "mdi:gauge", None),
    ("aqi", "Air Quality Index", "mdi:chart-line", "AQI"),
    ("aqi_pollutant", "Main Pollutant", "mdi:chemical-weapon", None),
    ("temp", "Temperature", "mdi:temperature-celsius", "°C"),
    ("humidity", "Humidity", "mdi:water", "%"),
]

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_DEVICE_NAME): cv.string,
        vol.Optional(CONF_AQI_STANDARD, default="US"): vol.In(["US", "CN", "IN", "EU"]),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the air_quality Laser Egg sensor."""
    device_name = config.get(CONF_NAME)
    api_key = config.get(CONF_API_KEY)
    device_id = config.get(CONF_DEVICE_ID)
    aqi_standard = config.get(CONF_AQI_STANDARD)
    scan_interval = config.get(CONF_SCAN_INTERVAL)

    session = aiohttp_client.async_get_clientsession(hass)
    api = LasserEggData(device_id, api_key, aqi_standard, scan_interval, session)

    await api.async_update()

    sensors = []
    for kind, name, icon, unit in SENSORS:
        sensors.append(
            LasserEggSensor(api, kind, f"{device_name} {name}", icon, unit, device_id)
        )

    async_add_entities(sensors, True)


class LasserEggSensor(Entity):
    """Implementation of a Laser Egg sensor."""

    def __init__(self, api, kind, name, icon, unit, device_id):
        """Initialize the sensor."""
        self._name = name
        self._api = api
        self._device_id = device_id
        self._icon = icon
        self._state = None
        self._type = kind
        self._unit = unit

    @property
    def available(self):
        """Return True if entity is available."""
        return bool(self._api.data)

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique, HASS-friendly identifier for this entity."""
        return f"{self._device_id}_{self._type}"

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit

    async def async_update(self):
        """Update the sensor."""
        await self._api.async_update()
        data = self._api.data

        if not data:
            return

        if self._type == "aqi_level":
            level = data.get(self._type)
            if level:
                self._state = level["label"]
                self._icon = level["icon"]
        else:
            self._state = data.get(self._type)


def constrain(min, max):
    return lambda x: min if x < min else (max if x > max else x)

AQI_CONSTRAIN = constrain(0, 500)

class LasserEggData:
    """Get data from Laser Egg API."""

    def __init__(self, device_id, api_key, aqi_standard, throttle, session=None):
        """Initialize the data object."""
        self._aqi_standard = aqi_standard
        self._params = {"key": api_key}
        self._url = "https://api.origins-china.cn/v1/lasereggs/" + device_id
        self._session = aiohttp.ClientSession() if session is None else session

        self.data = {}
        self.async_update = Throttle(throttle)(self._async_update)

    async def _async_update(self) -> None:
        """Get the data from Lasser egg API."""
        from numpy import interp

        try:
            with async_timeout.timeout(10):
                resp = await self._session.get(self._url, params=self._params)
                if resp.status != 200:
                    _LOGGER.error('API returned %s', resp.status)
                    self.data = {}
                    return False

                data = await resp.json()
                _LOGGER.debug("New data retrieved: %s", data)
                self.data = data["info.aqi"]["data"]
        except:
            _LOGGER.debug("Couldn't fetch data")
            self.data = {}
            return False

        try:
            # Based on https://github.com/kaiterra/aqicalc-js
            scale = AQI_SCALE[self._aqi_standard]
            aqis = [
                {"aqi": interp(self.data.get("pm25"), PM25_SCALE[self._aqi_standard], scale), "pollutant": "PM2.5"},
                {"aqi": interp(self.data.get("pm10"), PM10_SCALE[self._aqi_standard], scale), "pollutant": "PM10"},
                # Same for every scale standard
                {"aqi": interp(self.data.get("rtvoc"), TVOC_SCALE["CN"], AQI_SCALE["CN"]), "pollutant": "TVOC"}
            ]

            for aqi in aqis:
                aqi["aqi"] = AQI_CONSTRAIN(aqi["aqi"])
            
            aqis =  [aqi for aqi in aqis if aqi["aqi"] > 0]

            if len(aqis) > 0:
                primary_aqi = aqis[0]
                for i in range(1, len(aqis)):
                    if primary_aqi["aqi"] < aqis[i]["aqi"]:
                        primary_aqi = aqis[i]

                level = None
                for i in range(1, len(scale)):
                    if primary_aqi["aqi"] <= scale[i]:
                        level = AQI_LEVEL[self._aqi_standard][i-1]
                        break

                self.data["aqi"] = round(primary_aqi["aqi"], 2)
                self.data["aqi_pollutant"] = primary_aqi["pollutant"]
                self.data["aqi_level"] = level
        except IndexError as err:
            _LOGGER.error('API returned %s', err)
            return False
        return True