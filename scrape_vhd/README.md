# Crawl the Victorian Heritage Database for sites in Municipality of Yarra

Extract key reference info into the output CSV
Using a scrapy spider, crawl all the search results for the CITY OF YARRA
For each result, visit the place page and scrape key data such as:

- Placeid
- VHR reference id.
- Overlay id,
- Name',
- Location (Address),
- Position (Coordinates)
- Description (Summary of Statement of Significance)
- Statement of Significiance (First few lines only)
- Authority (Should be either Yarra or Victorian Heritage Register
- href  Links to the VHD place page,
- Image Links to one image of the place on the VHD place page,
- Thumbnail Links to a small image of the place on the VHD place page,

## Install

Depending on your environment, some or all of the following steps my be required.
to install python and scrapy.

- Create a Micro Google Compute Engine with Ubunto 18 image, and HTTP/HTTPS access
- Follow the setup guide  https://cloud.google.com/python/setup

```bash
sudo apt update
sudo apt install python python-dev python3 python3-dev
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo apt install virtualenv
mkdir vhd
cd vhd
virtualenv --python python3 env
source env/bin/activate
sudo apt-get install python-dev
sudo apt-get install libxml2-dev libxslt1-dev
pip install scrapy
git clone https://github.com/intotecho/yarraplanning.git
cd yarraplanning/scrape_vhd
```

## USAGE

1. _Creating a scrapy project called scrape_vhd (not needed if checkout of repo)_
2. _Copy this file to to spiders folder._

cd yarraplanning/scrape_vhd/scrape_vhd

### FIRST BUILD THE INDEX

Use [screen](https://gist.github.com/jctosta/af918e1618682638aa82) for long running processes; in case the session is interrupted midway.

First run scrapy crawl with  *-a index="True"* and -o indexfile.csv to build the index of placeids and store in filename.csv. This will search for all places in the CITY OF YARRA and record their placeid in the index.

If you want to build an index based on an input list of VHR's then use instead  -a index='VHR'.

```bash

>cd ~/yarraplanning/scrape_vhd/scrape_vhd
>rm vhd_index_$DATE.csv scrapy crawl scrapevhd -a index="True" -o vhd_index_$DATE.csv

```

If you want to build an index based on an input list of VHR's then use instead  -a index='VHR'. This will read vhr_overlay_index.csv as input, and read the VHR column, using it to search for VHRs. It builds an index of vhdplaceids in the same format as Index='True'

```bash

 rm vhr_index_$DATE.csv; scrapy crawl scrapevhd -a index="VHR" -o vhr_index_$DATE.csv

```

### THEN SCRAPE DETAILS FOR EACH PLACE IN THE INDEX

Run with command  *-a index="indexfile.csv"* to scrape the place details. Where filename is the index build in the first step. If index was saved to  vhr_index_$DATE.csv (and created on the same date)

```bash

rm yarra_vhr_$DATE.csv; scrapy crawl scrapevhd -a index="vhr_index_$DATE.csv" -o yarra_vhr_$DATE.csv

```

### Important

Each time the output file is appended. So delete it before rerunning.

```

> rm yarra_vhd_index_$DATE.csv stderr-$DATE.log; scrapy crawl scrapevhd -a index="True" -o yarra_vhd_index_$DATE.csv  > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)

```

## Output

The details file yarra_vhd-$DATE.csv can be uploaded to BigQuery and used by YarraHeritageMaps.
