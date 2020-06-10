# -*- coding: utf-8 -*-
import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize
import re

class DetiknewsSpider(scrapy.Spider):
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'detiknews.csv'
    }

    name = 'detiknews'  
    start_urls = ['https://news.detik.com/indeks/?date=05/{:02d}/2020'.format(page) for page in range(1,31)]

    def parse(self, response):        
        urls = response.xpath('//h3[@class="media__title"]//a/@href').getall()
        for url in urls:    
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)

        next_indeks = response.xpath('//div[@class="pagination text-center mgt-16 mgb-16"]/a').extract()[-1]
        next_indeks_url = re.findall(r'https.+0',next_indeks)
        
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url[0], callback=self.parse)

    def parseNews(self, response):
        data = dict()

        #judul
        data['Judul'] = response.xpath('//h1[@class="detail__title"]/text()').get().strip()

        #konten
        data['Konten'] = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="detail__body-text"]/p').extract()])

        #sumber
        data['Sumber'] = 'DETIK NEWS'

        #tanggal
        data['Tanggal'] = response.xpath('//div[@class="detail__date"]/text()').get()

        #konten pisah
        data['Konten_pisah'] = "||".join(sent_tokenize(data['Konten']))

        #Url
        data['URL'] = response.url
        
        #next page
        next_page = response.xpath('//a[@class="btn btn--blue-base btn--sm mgb-24"]/@href').get() 

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.next,meta=data)
        
        yield data

    def next(self, response):
        response.meta['Konten'] = response.meta['Konten'] + " " + " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="detail__body-text"]/p').extract()])
        response.meta['Konten_pisah'] = "||".join(sent_tokenize(response.meta['Konten']))

        next_page = response.xpath('//a[@class="btn btn--blue-base btn--sm mgb-24"]/@href').extract_first()

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.next,meta=response.meta)
        else:
            yield response.meta