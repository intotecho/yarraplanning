# -*- coding: utf-8 -*-
import os.path

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapeVhdPipeline(object):

    def process_item(self, item, spider):
        try:
            id = item['SoSHash']
            filename = './/sos//{}.html'.format(id)
            sospath = os.path.abspath(filename)
            if not os.path.isfile(sospath) or os.path.getsize(sospath) == 0L:
                print('Saving new SOS: {}'.format(id))
                self.file = open(sospath, 'w')
                self.file.write(item['StatementContent'])
                self.file.close()
            else:
                print('Skipping duplicate SOS: {}'.format(id))
            try:
                del item['Summary']
                del item['StatementContent']
                del item['download_timeout']
                del item['depth']
                del item['download_slot']
                del item['download_latency']
            except KeyError, k:
                print('EXCEPTION Deleting Key {}'.format(str(k)))
                pass
        except Exception, e:
            print('EXCEPTION Saving new SOS: {} hash {} {}'.format(item['vhdplaceid'], id, str(e)))
            exit()
        return item
