# Home Assistant Laser Egg sensor component
Home Assistant custom component for the Kaiterra's LaserEgg

## Getting the Kaiterra's API key
First you need to get the device id and api key from kaiterra site.
1. Register on https://dashboard.kaiterra.cn
2. Add device to dashbord using "+" sign on the bottom and write down device uuid
3. Open [Profile/Developer](https://dashboard.kaiterra.cn/me/account/developer), generate new key and write it down

## Usage

```yaml
sensor:
  - platform: laser_egg
    device_id: xxxxx
    api_key: xxxxx
```

## Configuration options

Key | Type | Required | Description
-- | -- | -- | --
`device_id` | `string` | `True` | The device id from Kaiterra's dashboard
`api_key` | `string` | `True` | The api key from Kaiterra's dashboard
`name` | `string` | `False` | Name of the integration
`aqi_standard` | `string` | `False` | The Air Quality Index standard, available options: ["CN", "IN", "US", "EU"], default: "US"
`scan_interval` | `string` | `False` | The api communication interval
