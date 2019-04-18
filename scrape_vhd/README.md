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

## USAGE:
1. Install scrapy 
2. Creating a scrapy project called scrape_vhd
3. Copy this file to to spiders folder.

## SAMPLE COMMANDS

>cd ~/yarraplanning/scrape_vhd
>rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl scrapevhd -a buildindex="True" -o yarra_vhd-$DATE.csv  > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)

>scrapy crawl scrapevhd -a buildindex="True" first to build the index file. Then False to get the place details.

## Output
The file yarra_vhd-$DATE.csv can be uploaded to BigQuery
