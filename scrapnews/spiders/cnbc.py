# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.markup import remove_tags

class CnbcSpider(scrapy.Spider):
    name = 'cnbc_test'
    allowed_domains = ['cnbcindonesia.com']
    start_urls = ['https://www.cnbcindonesia.com/news/indeks/3/{}?date='.format(page) for page in range(1,50)]

    def parse(self, response):
        urls = response.xpath('//ul[@class="list media_rows middle thumb terbaru gtm_indeks_feed"]//a/@href').getall()
        print(urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parseNews)

    def parseNews(self, response):

        data = dict()
        #judul
        #konten
        data['konten'] = [item.strip() for item in response.xpath('//div[@class="detail_text"]/text()').extract()]
        #tanggal
        data['tanggal'] = response.xpath('//div[@class="date"]/text()').extract()
        data['judul'] = response.xpath('//div[@class="container"]/h1/text()').extract()
        data['sumber'] = 'CNBC INDONESIA'

        yield data
