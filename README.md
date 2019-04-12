
# /yarraplanning
Geospatial Analysis and display of City of Yarra Heritage Register and Planning Applications 

## Install & Config
Run setup.sh in local shell
Refer to setup instructions in each folder.

# /yarraheritagemaps
Web Application to query BigQuery and display maps of the heritage overlays

## /overlay
Scripts to import offical GIS overlays from the Victorian Government, filter and conveert to Big Query
- Planning Zones
- Heritage Overlays
- Properties (Title boundary)
- Addresses

## /heritage_register 
- Scan and clean the heritage register (pdf) into a CSV that can be imported to BigQuery
- Normalise the addresses
- Fix some minor errors.
Depends of Tablula-win-1.2.1

## /geolocate
Python script to convert addresses in the planning applications to coordinates and merge back into the list of applications.
This also converts the column names to be BQ compatible.
- geolocation may be suprflous if can match with geolocated addresses from in the overlay data.

## /yarra_scrape
Elements of a scrapy project to scrap the Yarra's Planning Applications Search to a CSV file
Output is run through the geolocate/mergegeocode.py to clean up.

## /vhd_scrape
Elements of a scrapy project to scrap the Victorian Heritage Register to a CSV file.

