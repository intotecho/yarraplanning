# -*- coding: utf-8 -*-
'''
Crawl the Victorian Heritage Database for sites in Municipality of Yarra
Extract some key reference info into the output CSV

USAGE:
1. Install scrapy 
2. Creating a scrapy project called scrape_vhd
3. Copy this file to to spiders folder.

4. SAMPLE COMMANDS

>cd ~/yarraplanning/scrape_vhd
>rm yarra_vhd-$DATE.csv stderr-$DATE.log; scrapy crawl scrapevhd -o yarra_vhd-$DATE.csv  > >(tee -a stdout.log) 2> >(tee -a stderr-$DATE.log >&2)

'''

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re

# https://vhd.heritagecouncil.vic.gov.au/search?kw=YARRA&aut_off=1&collapse=true&spage=1&tab=places&view=detailed&rpp=25&ppage=946


class ScrapevhdSpider(CrawlSpider):
    name = 'scrapevhd'
    allowed_domains = ['vhd.heritagecouncil.vic.gov.au']
    start_urls = []

    # specifies exported fields and order
    ITEM_PIPELINES = {
       'myproject.pipelines.ScrapeVhdPipeline': 300
    }
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_TIMEOUT': 360,
        'FEED_EXPORT_FIELDS': [
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
            'VHRlng',
            ]
    }
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
    '''
    rules = (
        # Extract links matching search or place and parse them with the spider's method parse_item
       
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

    def __init__(self, *args, **kwargs):
        pages = range(0, 824)
        #pages = range(30, 34)
        for p in pages:
            url = 'https://vhd.heritagecouncil.vic.gov.au/search?kw=&kwt=exact&kwe=&aut_off=1&aut%%5B0%%5D=&cp=0&mun%%5B0%%5D=77&str=&sub=&pre=&arcs=0&arc=&tp=0&nme=&nmf=&his=&yt=0&yc=&idnt=hermes&idn=&do=s&collapse=true&type=place&spage=1&tab=places&view=detailed&rpp=25&ppage={}'.format(p)
            self.start_urls.append(url)
        super(ScrapevhdSpider, self).__init__(*args, **kwargs)
        print(u'=== INIT ====')
        print(self.start_urls)

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
            pagematch = re.search(r'page=(\d*)',  response.url)
            if pagematch is not None:
                page = pagematch.group(1)
                sites = response.css("li.row")
                self.logger.error('\n\n === PARSING SEARCH RESULTS PAGE {} HAS  {}\n\n'.format(page, len(sites)))
            return

        mapLocation = response.css('div .listing-sidebar-map').css('iframe::attr(src)').get()
        self.logger.debug(mapLocation)
        try:
            item['VHRlat'] = re.search(r'q=([+-]?(\d*\.)?\d+),([+-]?(\d*\.))',
                                       mapLocation).group(1)
            item['VHRlng'] = re.search(r',([+-]?(\d*\.)?\d+)',
                                       mapLocation).group(1)
        except:
            item['VHRlat'] = u'0'
            item['VHRlng'] = u'0'
        item['Overlay'] = self.stripif(response.xpath('//h5[contains(text(),"Heritage Overlay Numbers")]/following-sibling::text()').get())
        item['VHR'] = self.stripif(response.xpath("//*[contains(text(), 'Victorian Heritage Register (VHR) Number')]/following-sibling::text()").get())
        item['Image'] = self.stripif(response.css('img.gallery-image::attr(src)').get())
        item['Summary'] = False
        item['Name'] = self.stripif(response.css('div.col-place-title::text').get())
        item['Location'] = self.stripif(response.xpath('//h5[contains(text(),"Location")]/following-sibling::text()').get())
        item['Statement'] = self.stripif(response.xpath('//h2[contains(@id,"statement-significance")]/following-sibling::p/text()').get())
        item['vhdplaceid'] = response.url.rsplit('/', 1)[-1]
        item['href'] = response.url
        item['Authority'] = self.stripif(response.xpath('//h5[contains(text(),"Heritage Listing")]/following-sibling::text()').get())
        self.logger.info("\n\n\n === YIELDING PLACE DETAILS {} {} ===\n\n\n".format(item['vhdplaceid'], item['VHRlng']  ))
        yield item

    '''
    parse search results page
    '''

    def parse_start_url(self, response):
        page = re.search(r'page=(\d*)',  response.url).group(1)
        sites = response.css("li.row")
        self.log('\n\n === PAGE {} HAS  {} SITES TO SCRAPE\n\n'.format(page, len(sites)))
        for site in sites:
            items = {}
            href = site.css("div.col-name-details").css("p.name") \
                       .css("a.red-link::attr(href)").get()
            items['href'] = href
            items['vhdplaceid'] = href.rsplit('/', 1)[-1]
            items['Name'] = site.css("div.col-name-details").css("p.name").css("a.red-link::text").get().strip()

            items['Description'] = site.css("p.description::text").get()
            items['Authority'] = site.css("span.authority-name::text").get()
            items['href'] = site.css("div.col-name-details").css("p.name") \
                                .css("a.red-link::attr(href)").get()

            items['Thumbnail'] = site.css("div.col-thumbnail") \
                                     .css("img::attr(src)").get()
            items['Summary'] = True
            items['Overlay'] = u''
            items['VHR'] = u''

            if len(href) > 0:
                self.logger.info("\n\n\n === SEARCH FOUND ITEM {} on PAGE {} === \n\n\n".format(items['vhdplaceid'], page))
                yield scrapy.Request(
                    href,
                    meta=items,
                    callback=self.parse_placedetails)
            else:
                self.logger.error('\n\n === SITE {} on PAGE {} HAS NO DETAIL LINK!\n\n'.format(len(sites), page))

        self.logger.info("\n\n\n === SEARCH FINISHED PAGE  ===\n\n\n")