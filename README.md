# yarraplanning
Contains the App for Geospatial analysis and display of City of Yarra Heritage Register and Planning Applications 

Summary of Data preparation tools. Each has its own details readme

## geolocate
Python script to convert addresses in the planning applications to coordinates and merge back into the list of applications.
May be suprflous if can match with geolocated addresses from in the overlay data.

## scrape_yarra_planning_apps
Scrape the Yarra Planning Search Page to get all applications between 2000 and 2018.

## overlay
Scripts to import offical GIS overlays from the Victorian Government, filter and conveert to Big Query
- Planning Zones
- Heritage Overlays
- Properties (Title boundary)
- Addresses

## heritage_register 
- clean_register.py: 
   - Scans and cleand the heritage register (pdf) into a CSV.
   - Normalise the addresses to a format similar to VICMAP (GNAF)
   - Fix some minor errors like missing suburb, or moving sites from Burnley to Richmond.
- register-2gnaf.py: 
   - Uses an RNN to decompose the addresses output by clean_register.py into components.(Slow)
- match_addresses.py
   - uses complex logic to match addresses output by clean_register.py with adresses in the vicmap address data.

## overlay_schedule
 - Convert and clean the PDF schedule to the Yarra Heritage Overlays.

## scrape_vhd
 - Scrape the Victorian Heritage Register into an index and detail csv files. 
   This is a two pass process. The first builds a CSV containing just the VHD placeId 
   for heritage places in Yarra. 
   The second pass scrapes each placeId and places summary info into the output file
   and also builds a directory of StatementOfSignificance HTML files. 
   Each line in the summary CSV has a SOsHash that is the name of the file containing the statement in HTML format.
   These can be linked together by a web app.
   Depends of Tablula-win-1.2.1
