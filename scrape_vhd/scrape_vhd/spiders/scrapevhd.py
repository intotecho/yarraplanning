# -*- coding: utf-8 -*-
'''
Crawl the Victorian Heritage Database for sites in Municipality of Yarra
Extract some key reference info into the output CSV

USAGE:
Refer to README.md in parent folder.

cd yarraplanning/scrape_vhd
TO SCRAPE INDEX
>scrpay crawl scraevhd buildindex='True'
>rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl scrapevhd -a index="True" -o yarra_vhd_index-$DATE.csv  > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)

TO READ INDEX AND SCRAPE PLACE DETAILS
rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl  -a index="yarra_vhd_index-$DATE.csv" -o yarra_vhd-$DATE.csv scrapevhd > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)
'''

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re
import pandas as pd
import numpy as np
import os.path
# https://vhd.heritagecouncil.vic.gov.au/search?kw=YARRA&aut_off=1&collapse=true&spage=1&tab=places&view=detailed&rpp=25&ppage=946

def placeToURL(place_id):
    return 'https://vhd.heritagecouncil.vic.gov.au/places/{}'.format(place_id)

class ScrapevhdSpider(CrawlSpider):
    name = 'scrapevhd'
    allowed_domains = ['vhd.heritagecouncil.vic.gov.au']
    start_urls = []
    details_filename = 'yarra_vhd-20190423.csv'
    buildindex = 'True'  # Replaced by index attribute on command line -a index="True"
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_TIMEOUT': 360
    }


    def __init__(self, index='',  **kwargs):
        pages = range(0, 824)
        #pages = range(0, 824)
        #pages = range(30, 34) For testing a small number of pages...
        if index == u'True':
            self.buildindex = u'True'
            self.logger.info( "\n\n BUILDING INDEX")
            for p in pages:
                url = 'https://vhd.heritagecouncil.vic.gov.au/search?kw=&kwt=exact&kwe=&aut_off=1&aut[0]=&cp=0&mun[0]=77&str=&sub=&pre=&arcs=0&arc=&tp=0&nme=&nmf=&his=&yt=0&yc=&idnt=hermes&idn=&do=s&collapse=true&type=place&spage=1&tab=places&view=detailed&rpp=25&ppage={}'.format(p)
                self.start_urls.append(url)
            # specifies exported fields and order
            self.custom_settings['FEED_EXPORT_FIELDS'] = [
                'page',
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                20, 21, 22, 23, 24
                ]
        else:
            self.logger.info("\n\n SCRAPING PLACE DETAILS")
            # specifies exported fields and order
            self.custom_settings['FEED_EXPORT_FIELDS'] = [
                # NOT USED - ITEMS NOW DEFINED IN pipeline.py
                'Summary',
                'vhdplaceid',
                'VHR',
                'Overlay',
                'Name',
                'Location',
                'Municipality',
                'Description',
                'Authority',
                'href',
                'Image',
                'Thumbnail',
                'VHRlat',
                'VHRlng'
                'SoSHash'
            ]
            self.buildindex = index
            df_index = self.readIndex()
            total_pages = df_index.size
            df_index = df_index.applymap(lambda p : 'https://vhd.heritagecouncil.vic.gov.au/places/{}'.format(p))
            self.logger.debug("\n\n INDEX CONTAINS {} DETAIL PAGES TO SCRAPE \n\n".format(df_index.size))

            pages = df_index.to_numpy().copy()
            pages = np.resize(pages, total_pages)
            # self.logger.debug("\n\n PAGES {} \n\n".format(pages))

            self.start_urls = pages[0:].tolist()
            self.logger.debug("\n\n START URLS {} \n\n".format(self.start_urls))

        super(ScrapevhdSpider, self).__init__(**kwargs)
        self.logger.info(u'=== INIT ====')
        # self.logger.info(self.start_urls)

    def readIndex(self):
        # Read the index data to a Pandas Dataframe
        index_filename = self.buildindex
        pathname = os.path.abspath(index_filename)
        if os.path.isfile(pathname):
            try:
                index_df = pd.read_csv(index_filename, encoding='utf8')
            except Exception as e:
                self.logger.error("Error Reading Index File. Exception {} ".format(e))
                exit()
            return index_df
        else:
            return pd.DataFrame() # Empty
    '''
    def readDetails(self):
        # Read the details data and only scrape pages we don't have already.
        try:
            details = pd.read_csv(self.details_filename, encoding='utf8')
        except Exception as e:
            self.logger.error("Error Reading Details File. Exception {} ".format(e))
            exit()
        return details_df
    '''

    def parse_start_url(self, response):
        if self.buildindex == u'True':
            self.logger.info("\n\n BUILDING INDEX OF PLACES")
            return self.parse_search_results_page(response)
        else:
            self.logger.info("\n\n SCRAPING PLACE DETAILS")
            return self.parse_placedetails(response)

    def stripif(self, string):
        if string:
            return string.strip()
        else:
            return 'none'

    '''
    Remove commas and municipality
    Returns:
        normal: address sans commas and sans municipality in upper
        municipality - everything after the last comma  in upper
    '''

    def normaliseaddress(self, locn):
        substring = ","
        municipality = locn[locn.rfind(substring)+1:].upper().strip()  # Everything after the last comma.

        # commacount = locn.count(substring)

        # first remove last comma and everything after it.
        normal = locn[:locn.rfind(substring)]

        # replace first comma (otpioonally followed by a space) with a single space and make upper case.
        normal = normal.replace(substring, ' ').upper()
        normal = re.sub(' +', ' ', normal).strip()  # remove multiple spaces
        return normal, municipality

    '''
    parse detail place page
    '''

    def parse_placedetails(self, response):
        item = response.meta
        match = re.search(r'/(search)\?', response.url)
        if match and match.group(1) == u'search':
            pagematch = re.search(r'ppage=(\d*)',  response.url)
            if pagematch is not None:
                page = pagematch.group(1)
                sites = response.css("li.row")
                self.logger.error('\n\n === PARSING SEARCH RESULTS PAGE {} HAS  {}\n\n'.format(page, len(sites)))
            return

        mapLocation = response.css('div .listing-sidebar-map').css('iframe::attr(src)').get()
        # self.logger.debug(mapLocation)
        item['vhdplaceid'] = response.url.rsplit('/', 1)[-1]

        location = self.stripif(response.xpath('//h5[contains(text(),"Location")]/following-sibling::text()').get())
        item['Location'], item['Municipality'] = self.normaliseaddress(location)
        item['href'] = response.url
        item['Name'] = self.stripif(response.css('div.col-place-title::text').get())
        item['Overlay'] = self.stripif(response.xpath('//h5[contains(text(),"Heritage Overlay Numbers")]/following-sibling::text()').get())
        item['VHR'] = self.stripif(response.xpath("//*[contains(text(), 'Victorian Heritage Register (VHR) Number')]/following-sibling::text()").get())
        item['Image'] = self.stripif(response.css('img.gallery-image::attr(src)').get())
        item['Summary'] = False
        item['Authority'] = self.stripif(response.xpath('//h5[contains(text(),"Heritage Listing")]/following-sibling::text()').get())
        sosElement = response.xpath('//*[preceding-sibling::h2[1][.="Statement of Significance"]]')
        sos = sosElement.getall() # a list
        separator = ' '
        item['StatementContent'] = separator.join(sos).encode('utf-8')

        # To avoid storing duplicate SOS, we will only store each unique SOS once and store the hash in each site that includes it.
        item['SoSHash'] = '{}'.format(hash(item['StatementContent'])) # Convert hash to a string here.
        try:
            item['VHRlat'] = re.search(r'q=([+-]?(\d*\.)?\d+),([+-]?(\d*\.))',
                                       mapLocation).group(1)
            item['VHRlng'] = re.search(r',([+-]?(\d*\.)?\d+)',
                                       mapLocation).group(1)
        except:
            item['VHRlat'] = u'0'
            item['VHRlng'] = u'0'
        self.logger.info("\n\n\n === YIELDING PLACE DETAILS id:{} hash:{} ===\n\n\n".format(item['vhdplaceid'], item['SoSHash']  ))
        yield item

    '''
    parse search results page
    '''

    def store_site(self, response, site):
        item = {}
        href = site.css("div.col-name-details").css("p.name") \
                   .css("a.red-link::attr(href)").get()
        item['href'] = href
        item['vhdplaceid'] = href.rsplit('/', 1)[-1]
        item['Name'] = site.css("div.col-name-details") \
                           .css("p.name") \
                           .css("a.red-link::text").get().strip()

        item['Description'] = site.css("p.description::text").get()
        item['Authority'] = site.css("span.authority-name::text").get()
        item['href'] = site.css("div.col-name-details").css("p.name") \
                           .css("a.red-link::attr(href)").get()

        item['Thumbnail'] = site.css("div.col-thumbnail") \
                                .css("img::attr(src)").get()
        item['Summary'] = True
        item['Overlay'] = u''
        item['VHR'] = u''
        # self.logger.info("\n\n\n === FINISH SITE  {} ===\n\n\n".format(item['vhdplaceid']))
        return item

    def parse_search_results_page(self, response):
        pagematch = re.search(r'ppage=(\d*)',  response.url)
        if pagematch is not None:
            page = pagematch.group(1)

        items = {}
        result = 0
        sites = response.css("li.row")
        self.log('\n\n === RESULTS PAGE {} HAS  {} SITES TO SCRAPE\n\n'.format(page, len(sites)))
        items['page'] = page
        for site in sites:
            # self.logger.info(
            #    "\n\n\n === APPENDING SITE  {} ===\n\n\n".format(result))
            item = self.store_site(response, site)
            items[result] = item['vhdplaceid']
            result = result+1
        self.logger.info("\n=== SEARCH FINISHED PAGE  ===\n")
        yield items
