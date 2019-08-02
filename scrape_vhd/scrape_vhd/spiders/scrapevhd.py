# -*- coding: utf-8 -*-
'''
Crawl the Victorian Heritage Database for sites in Municipality of Yarra
Extract some key reference info into the output CSV

USAGE:
Refer to README.md in parent folder.
#cd yarraplanning/scrape_vhd/scrape_vhd
'''

from scrapy.spiders import CrawlSpider
import re
import pandas as pd
import numpy as np
import os.path
# https://vhd.heritagecouncil.vic.gov.au/search?kw=YARRA&aut_off=1&collapse=true&spage=1&tab=places&view=detailed&rpp=25&ppage=946


def placeToURL(place_id):
    return 'https://vhd.heritagecouncil.vic.gov.au/places/{}'.format(place_id)


class ScrapeVhdSpider(CrawlSpider):
    name = 'scrapevhd'
    allowed_domains = ['vhd.heritagecouncil.vic.gov.au']
    start_urls = []
    vhr_list = 'vhr_overlay_index.csv'
    buildindex = 'True'  # Replaced by index attribute on command line -a index="True"
    mode = 'True'
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_TIMEOUT': 360
    }

    def __init__(self, index='',  **kwargs):
        pages = range(0, 824)
        # pages = range(0, 824)
        # pages = range(30, 34) For testing a small number of pages...
        self.mode = index
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
        if index == u'VHR':
            self.buildindex = u'True'
            self.logger.info( "\n\n BUILDING VHR INDEX")

            vhrOverlayList = self.readVHRList()
            vhrOverlayList.head()
            vhrlist = vhrOverlayList['VHR'].tolist()

            for p in vhrlist:
                p = int(p[1:])
                x = 'H' + format(p, '04') # pad with leading zeroes
                url='https://vhd.heritagecouncil.vic.gov.au/search?idnt=vhr&idn={}&type=place'.format(x)
                self.start_urls.append(url)
            print self.start_urls
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
            if df_index.empty:
                print 'ERROR: Index file is not found or empty!'
                exit(0)

            df_index = df_index.drop("page", axis=1)
            total_pages = df_index.size
            allsites  = df_index.to_numpy().copy()
            sites = allsites[allsites != 0].tolist()
            for p in sites:
                self.start_urls.append('https://vhd.heritagecouncil.vic.gov.au/places/{}'.format(p))
            self.logger.debug("\n\n INDEX CONTAINS {} DETAIL PAGES TO SCRAPE \n\n".format(len(sites)))
            self.logger.debug("\n\n START URLS {} \n\n".format(self.start_urls))

        super(ScrapeVhdSpider, self).__init__(**kwargs)
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
            return pd.DataFrame()  # Empty

    def readVHRList(self):
        # Read the details data and only scrape pages we don't have already.
        try:
            details = pd.read_csv(self.vhr_list, encoding='utf8')
        except Exception as e:
            self.logger.error("Error Reading VHR List. Exception {} ".format(e))
            exit()
        return details

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
        # if 'YARRA' in item['Municipality'].upper(): # Looking  for outliers
        #     return
        self.logger.info("\n\n\n === YIELDING PLACE DETAILS id:{} hash:{} ===\n\n\n".format(item['vhdplaceid'], item['SoSHash']  ))
        yield item

    '''
    parse search results page
    '''

    def store_site_result(self, response, site):
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
        vhrStr = site.css("span.vhr-hi-number-container::text").get()
        if vhrStr.startswith("VHR "):
            item['VHR'] = vhrStr[4:]
        else:
            item['VHR'] = vhrStr

        # self.logger.info("\n\n\n === FINISH SITE  {} ===\n\n\n".format(item['vhdplaceid']))
        # print item
        return item

    def parse_search_results_page(self, response):

        #   pagematch = re.search(r'page=(\d*)',  response.url)
        #   if pagematch is not None:
        #       page = pagematch.group(1)

        items = {
            0: '0',
            1: '0',
            2: '0',
            3: '0',
            4: '0',
            5: '0',
            6: '0',
            7: '0',
            8: '0',
            9: '0',
            10: '0',
            11: '0',
            12: '0',
            13: '0',
            14: '0',
            15: '0',
            16: '0',
            17: '0',
            18: '0',
            19: '0',
            20: '0',
            21: '0',
            22: '0',
            23: '0',
            24: '0',
            'page': '1'
        }
        result = 0
        sites = response.css("li.row")
        self.log('\n\n === RESULTS PAGE  HAS  {} SITES TO SCRAPE\n\n'.format(len(sites)))

        if not sites:
            items['page'] = response.request.url

        for site in sites:
            self.logger.info(
                "\n\n\n === APPENDING SITE  {} ===\n\n\n".format(result))
            item = self.store_site_result(response, site)
            items[result] = item['vhdplaceid']
            result = result+1
            if self.mode == u'VHR':
                items['page'] = item['VHR']

        self.logger.info("\n=== SEARCH FINISHED PAGE  ===\n")
        yield items
