# -*- coding: utf-8 -*-
import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize

class DetiknewsSpider(scrapy.Spider):
    name = 'detiknews'
    allowed_domains = ['news.detik.com'] 
    start_urls = ['https://news.detik.com/indeks/?date=02/{}/2020'.format(page) for page in range(10,29)]

    def parse(self, response):        
        urls = response.xpath('//h3[@class="media__title"]//a/@href').getall()
        next_indeks_url = response.xpath('//div[@class="pagination text-center mgt-16 mgb-16"]/a/@href').extract()[-1]

        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)
        
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)

    def parseNews(self, response):
        data = dict()

        #next page
        data['next_page'] = response.xpath('//a[@class="btn btn--blue-base btn--sm mgb-24"]/@href').extract_first() 
        #judul
        data['judul'] = response.xpath('//h1[@class="detail__title"]/text()').extract_first().strip()
        #konten
        data['konten'] = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="detail__body-text"]/p').extract()])
        #tanggal
        data['tanggal'] = response.xpath('//div[@class="detail__date"]/text()').extract_first()
        #sumber
        data['sumber'] = 'DETIK NEWS'
        #konten pisah
        data['konten_pisah'] = "||".join(sent_tokenize(data['konten']))

        while data['next_page']:
            yield scrapy.Request(url=data['next_page'], callback=self.next,meta=data)
        
        yield data

    def next(self, response):
        response.meta['konten'] = response.meta['konten'] + " " + " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="detail__body-text"]/p').extract()])
        response.meta['next_page'] = response.xpath('//a[@class="btn btn--blue-base btn--sm mgb-24"]/@href').extract_first()
        response.meta['konten_pisah'] = "||".join(sent_tokenize(response.meta['konten']))

        if response.meta['next_page']:
            yield scrapy.Request(url=response.meta['next_page'], callback=self.next,meta=response.meta)
        else:
            yield response.meta