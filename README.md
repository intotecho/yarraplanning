# yarraplanning
Geospatial Analysis and display of City of Yarra Heritage Register and Planning Applications 

## geolocate
Python script to convert addresses in the planning applications to coordinates and merge back into the list of applications.
May be suprflous if can match with geolocated addresses from in the overlay data.
## overlay
Scripts to import offical GIS overlays from the Victorian Government, filter and conveert to Big Query
- Planning Zones
- Heritage Overlays
- Properties (Title boundary)
- Addresses

## heritage_register 
- Scan and clean the heritage register (pdf) into a CSV that can be imported to BigQuery
- Normalise the addresses
- Fix some minor errors.

Depends of Tablula-win-1.2.1
