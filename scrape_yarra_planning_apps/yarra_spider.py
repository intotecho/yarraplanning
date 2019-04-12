# Scrap  all Planning Applications from Yarra's web site.
# project=appbfw. Stored in ~/scrapy/yarra.
# 
# Install scrapy using pip --user scrapy
# Create a scrapy project called yarra.
# Edit the yarra-spider to be this file.
# cd ~/scrapy/yarra/
# rm yarra.csv
# ~/.local/bin/scrapy crawl yarra -o yarra.csv --loglevel=INFO
# gsutil cp home/intotecho/scrapy/yarra/yarra.csv gs://MY_BUCKET_NAME

import scrapy
def getval(app, item):
    return app.css('tr td:nth-child({item})::text'.format(item=item)).extract_first()

class YarraSpider(scrapy.Spider):
    name = "yarra"
    custom_settings = {
    # specifies exported fields and order
    'CONCURRENT_REQUESTS': 3,
    'DOWNLOAD_TIMEOUT' : 360,
    'FEED_EXPORT_FIELDS': [
           'Application Number',
                'Date Received',
                'Property Address',
                'Description',
                'Advert Date',
                'Determination',
                'Decision',
                'Estimated Cost',
                'Status',
                'Ward',
                'Responsible Officer',
                'Results Page'
    ]
  }

    def start_requests(self):
        pages = [
            35	,
            175	,
            233	,
            234	,
            237	,
            238	,
            240	,
            246	,
            248	,
            249	,
            255	,
            256	,
            258	,
            260	,
            262	,
            263	,
            269	,
            270	,
            272	,
            273	,
            274	,
            276	,
            278	,
            290	,
            291	,
            297	,
            298	,
            299	,
            300	,
            301	,
            302	,
            303	,
            307	,
            310	,
            311	,
            312	,
            313	,
            315	,
            318	,
            320	,
            321	,
            322	,
            323	,
            324	,
            325	,
            329	,
            331	,
            332	,
            333	,
            334	,
            335	,
            337	,
            340	,
            341	,
            342	,
            345	,
            348	,
            350	,
            351	,
            352	,
            353	,
            355	,
            357	,
            359	,
            360	,
            361	,
            363	,
            365	,
            367	,
            370	,
            371	,
            373	,
            374	,
            382	,
            383	,
            384	,
            387	,
            388	,
            389	,
            390	,
            393	,
            394	,
            395	,
            396	,
            397	,
            400	,
            402	,
            403	,
            404	,
            407	,
            408	,
            412	,
            413	,
            414	,
            415	,
            416	,
            417	,
            419	,
            420	,
            423	,
            424	,
            426	,
            427	,
            430	,
            431	,
            432	,
            433	,
            434	,
            435	,
            436	
        ]

        oldpages = [
            53	,
            55	,
            84	,
            87	,
            93	,
            94	,
            120	,
            127	,
            137	,
            150	,
            153	,
            157	,
            159	,
            163	,
            170	,
            173	,
            178	,
            181	,
            186	,
            190	,
            194	,
            196	,
            199	,
            205	,
            207	,
            210	,
            216	,
            218	,
            219	,
            220	,
            222	,
            223	
        ]
        #pages.extend([8001,8003,8010])
        pages = range(0, 513)
        for  p in pages: # range(0,513)
	    url = 'https://www.yarracity.vic.gov.au/planning-application-search?status=(All)&ward=(All)&page=%s' %p
            yield  scrapy.Request(url=url,  callback=self.parse)

    
    def parse(self, response):
        page = response.url.split("page=")[1]
        filename = 'apps-page-%s.html' % page
        print ( filename)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        apps = response.css('table.search').css('tbody').css('tr')
        for app in apps:
           yield {
                'Application Number': getval(app,1),
                'Date Received': getval(app,2),
                'Property Address': getval(app,3),
                'Description':  getval(app,4),
                'Advert Date':  getval(app,5),
                'Determination':  getval(app,6),
                'Decision':  getval(app,7),
                'Estimated Cost':  getval(app,8),
                'Status':  getval(app,9),
                'Ward':  getval(app,10),
                'Responsible Officer':  getval(app,11),
                'Results Page': page
           }
