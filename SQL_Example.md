# Specifying JSON Properties

The following is an example JSON payload that might be published by a device:

```json
{
    "deviceid" : "iot123",
    "temp" : 54.98,
    "humidity" : 32.43,
    "coords" : {
        "latitude" : 47.615694,
        "longitude" : -122.3359976
    }
}
```

The following example combines properties:

```sql
SELECT temp, deviceid AS dev_id, { "lat": coords.latitude, "long": coords.longitude, "src":"device" } FROM <TOPIC> WHERE <CONDITION>
```

Resulting in:

```json
{
    "temp" : 54.98,
    "dev_id" : "iot123",
    "lat" : 47.615694,
    "long" : -122.3359976,
    "src" : "device"
}
```

