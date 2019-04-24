# -*- coding: utf-8 -*-
'''
Crawl the Victorian Heritage Database for sites in Municipality of Yarra
Extract some key reference info into the output CSV

USAGE:
Refer to README.md in parent folder.

cd yarraplanning/scrape_vhd
TO BUILD INDEX
>scrpay crawl scraevhd buildindex='True'
>rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl scrapevhd -a index="True" -o yarra_vhd_index-$DATE.csv  > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)

TO READ INDEX
rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl  -a index="yarra_vhd_index-$DATE.csv" -o yarra_vhd-$DATE.csv scrapevhd > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)
'''

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re
import pandas as pd
# https://vhd.heritagecouncil.vic.gov.au/search?kw=YARRA&aut_off=1&collapse=true&spage=1&tab=places&view=detailed&rpp=25&ppage=946

def placeToURL(place_id):
    return 'https://vhd.heritagecouncil.vic.gov.au/places/{}'.format(place_id)

class ScrapevhdSpider(CrawlSpider):
    name = 'scrapevhd'
    allowed_domains = ['vhd.heritagecouncil.vic.gov.au']
    start_urls = []
    details_filename = 'yarra_vhd-20190423.csv'
    buildindex = 'True'  # Replaced by index attribute on command line -a index="True"
    # specifies exported fields and order
    ITEM_PIPELINES = {
       'myproject.pipelines.ScrapeVhdPipeline': 300
    }
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_TIMEOUT': 360
    }
    #

    '''
                restrict_xpaths=([
                    '//ul[@class="search-results-listings"]',
                    '//ul[@class="display-control-places"]',
                    '//div[@class="listings-container detailed-view"]',
                    '//div[@class="individual-listing-content"]',
                    '//div[@id="record-details"]',
                    '//div[@id="additional-info"]',
                    '//div[@class="listing-sidebar-map"]']
                ),
    rules = (
        # Extract links matching search or place and parse them.

        Rule(
            LinkExtractor(
                allow=('places.*',),
                deny=('shipwreck.*',
                      'search.*',
                      'img.*',)
            ),
            callback='parse_placedetails',
            follow=False
        ),
    )
   '''
    def __init__(self, index='',  **kwargs):
        pages = range(0, 824)
        #pages = range(0, 824)
        #pages = range(30, 34) For testing a small number of pages...
        if index == u'True':
            self.buildindex = u'True'
            self.logger.info( "\n\n BUILDING INDEX")
            for p in pages:
                #url = 'https://vhd.heritagecouncil.vic.gov.au/search?kw=&kwt=exact&kwe=&aut_off=1&aut%%5B0%%5D=&cp=0&mun%%5B0%%5D=77&str=&sub=&pre=&arcs=0&arc=&tp=0&nme=&nmf=&his=&yt=0&yc=&idnt=hermes&idn=&do=s&collapse=true&type=place&spage=1&tab=places&view=detailed&rpp=25&ppage={}'.format(p)
                #url = 'https://vhd.heritagecouncil.vic.gov.au/search?kw=&kwt=exact&kwe=&aut_off=1&aut[]=&cp=0&mun[]=77&str=&sub=&pre=&arcs=0&arc=&tp=0&nme=&nmf=&his=&yt=0&yc=&idnt=hermes&idn=&do=s&collapse=true&type=place'
                url = 'https://vhd.heritagecouncil.vic.gov.au/search?kw=&kwt=exact&kwe=&aut_off=1&aut[0]=&cp=0&mun[0]=77&str=&sub=&pre=&arcs=0&arc=&tp=0&nme=&nmf=&his=&yt=0&yc=&idnt=hermes&idn=&do=s&collapse=true&type=place&spage=1&tab=places&view=detailed&rpp=25&ppage={}'.format(p)
                self.start_urls.append(url)
            self.custom_settings['FEED_EXPORT_FIELDS'] = [
                'page',
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                20, 21, 22, 23, 24
                ]
        else:
            self.logger.info( "\n\n SCRAPING PLACE DETAILS")
            self.custom_settings['FEED_EXPORT_FIELDS'] = [
                'Summary',
                'vhdplaceid',
                'VHR',
                'Overlay',
                'Name',
                'Location',
                'Description',
                'Statement',
                'Authority',
                'href',
                'Image',
                'Thumbnail',
                'VHRlat',
                'VHRlng'
            ]
            self.buildindex = index
            df_index = self.readIndex()
            df_index = df_index.applymap(lambda p : 'https://vhd.heritagecouncil.vic.gov.au/places/{}'.format(p))
            self.start_urls = df_index.values.tolist()[0]
        super(ScrapevhdSpider, self).__init__(**kwargs)
        self.logger.info(u'=== INIT ====')
        # self.logger.info(self.start_urls)

    def readIndex(self):
        # Read the index data to a Pandas Dataframe
        index_filename = self.buildindex
        try:
            index_df = pd.read_csv(index_filename, encoding='utf8')
        except Exception as e:
            self.logger.error("Error Reading Index File. Exception {} ".format(e))
            exit()
        return index_df

    def readDetails(self):
        # Read the details data and only scrape pages we don't have already.
        try:
            details = pd.read_csv(self.details_filename, encoding='utf8')
        except Exception as e:
            self.logger.error("Error Reading Details File. Exception {} ".format(e))
            exit()
        return details_df

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
        item['href'] = response.url
        item['Name'] = self.stripif(response.css('div.col-place-title::text').get())
        item['Location'] = self.stripif(response.xpath('//h5[contains(text(),"Location")]/following-sibling::text()').get())
        item['Overlay'] = self.stripif(response.xpath('//h5[contains(text(),"Heritage Overlay Numbers")]/following-sibling::text()').get())
        item['VHR'] = self.stripif(response.xpath("//*[contains(text(), 'Victorian Heritage Register (VHR) Number')]/following-sibling::text()").get())
        item['Image'] = self.stripif(response.css('img.gallery-image::attr(src)').get())
        item['Summary'] = False
        item['Statement'] = self.stripif(response.xpath('//h2[contains(@id,"statement-significance")]/following-sibling::p/text()').get())
        item['Authority'] = self.stripif(response.xpath('//h5[contains(text(),"Heritage Listing")]/following-sibling::text()').get())
        try:
            item['VHRlat'] = re.search(r'q=([+-]?(\d*\.)?\d+),([+-]?(\d*\.))',
                                       mapLocation).group(1)
            item['VHRlng'] = re.search(r',([+-]?(\d*\.)?\d+)',
                                       mapLocation).group(1)
        except:
            item['VHRlat'] = u'0'
            item['VHRlng'] = u'0'
        self.logger.info("\n\n\n === YIELDING PLACE DETAILS {} {} ===\n\n\n".format(item['vhdplaceid'], item['VHRlng']  ))
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
