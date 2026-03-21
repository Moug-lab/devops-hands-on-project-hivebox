# SenseBox IDs

These are the openSenseMap senseBox IDs used by HiveBox to fetch
real temperature data from IoT sensor stations.

## Station IDs

| Station | ID |
|---------|----|
| Station 1 | 5eba5fbad46fb8001b799786 |
| Station 2 | 5c21ff8f919bf8001adf2488 |
| Station 3 | 5ade1acf223bd80019a1011c |

## API Endpoint

Each station is queried via:
```
GET https://api.opensensemap.org/boxes/{senseBoxId}
```

## Why these stations?

Three stations close to each other are used so HiveBox can
calculate an average temperature reading for better accuracy.
