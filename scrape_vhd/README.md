# Crawl the Victorian Heritage Database for sites in Municipality of Yarra
Extract key reference info into the output CSV
Using a scrapy spider, crawl all the search results for the CITU OF YARRA
For each result, visit the place page and scrape key data such as 
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

## USAGE:
2. Creating a scrapy project called scrape_vhd
3. Copy this file to to spiders folder.

## SAMPLE COMMANDS

>cd ~/yarraplanning/scrape_vhd
> screen 
>rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl scrapevhd -o yarra_vhd-$DATE.csv  > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)

## Output
The file yarra_vhd-$DATE.csv can be uploaded to BigQuery
