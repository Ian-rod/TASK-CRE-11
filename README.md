# TASK-CRE-11 | Ingest BORIS Berlin Standard Land Value Zones (FIS-Broker WFS)
- I used `https://gdi.berlin.de/services/wfs/brw2026` instead of `https://gdi.berlin.de/services/wfs/boris`. Since the URL endpoint provided did not work and I did some research to find the new URL for boris

## How to run
### Docker Database setup
1. Ensure you are on the root folder of the application and run `docker compose up -d` .This will create a container named 'iris-local-postgis'
2. run `docker ps` to ensure the container is up and running
### Python setup 
1. run `pip install requirements.txt`. This installs all required python dependencies
2. run `python -m app.main` to run the main application
### Confirming results
1. Connect to the database using the username `iris_user` and password `iris_password` using a suitable client and use the host as `localhost` and port as `5433`
2. check the `berlin_land_value_zones` table for rows of data

## Further Documentation
- further documentation can be found at  `/submission` folder