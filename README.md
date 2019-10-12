# THE GENERAL KAITERRA INTEGRATION HAS BEEN OFFICALY ADDED TO [HOME ASSISTANT](https://www.home-assistant.io/integrations/kaiterra)

# Home Assistant Laser Egg sensor component
Home Assistant custom component for the Kaiterra's LaserEgg

## Installation

### Getting the Kaiterra's API key
First you need to get the device id and api key from kaiterra site.
1. Register on https://dashboard.kaiterra.cn
2. Add device to dashbord using "+" sign on the bottom and write down device uuid
3. Open [Profile/Developer](https://dashboard.kaiterra.cn/me/account/developer), generate new key and write it down

### Manual installation
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called `laser_egg`.
4. Download all the files from the `custom_components/laser_egg/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) `custom_components/laser_egg/` you created.
6. Add the following to your _configuration.yaml_ using your device id and api key from the Kaiterra's dashboard. You can adjust/remove optional parameters.

```yaml
sensor:
  - platform: laser_egg
    device_id: xxxxx
    api_key: xxxxx
```

7. Restart home-assistant

### HACS installation
1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the "Laser Egg" integration.
3. Configure the `laser_egg` sensor.

```yaml
sensor:
  - platform: laser_egg
    device_id: xxxxx
    api_key: xxxxx
```

4. Restart Home Assistant.


## Configuration options

Key | Type | Required | Description
-- | -- | -- | --
`device_id` | `string` | `True` | The device id from Kaiterra's dashboard
`api_key` | `string` | `True` | The api key from Kaiterra's dashboard
`name` | `string` | `False` | Name of the integration
`aqi_standard` | `string` | `False` | The Air Quality Index standard, available options: ["CN", "IN", "US", "EU"], default: "US"
`scan_interval` | `string` | `False` | The api communication interval

## Contribution
PRs and help welcomed ;)
