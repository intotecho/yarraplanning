# Scrape Yarra Planning Applications

## Configure
 
Install scrapy using pip --user scrapy

Create a scrapy project called yarra.

Copy the spider in this repo into the scrapy project.
Edit as required.

Setup google cloud project in  
project=YOUR_PROJEcT_ID. Stored in ~/scrapy/yarra.

## Run
 cd yarra/
 rm yarra.csv
 ~/.local/bin/scrapy crawl yarra -o yarra.csv --loglevel=INFO
 gsutil cp home/intotecho/scrapy/yarra/yarra.csv gs://MY_BUCKET_NAME

