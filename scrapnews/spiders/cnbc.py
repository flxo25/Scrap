# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.markup import remove_tags
import w3lib.html as w3
from nltk.tokenize import sent_tokenize
import re

class CnbcSpider(scrapy.Spider):
    name = 'cnbc'
    start_urls = ['https://www.cnbcindonesia.com/indeks?date=2020/06/{:02d}'.format(page) for page in range(1,3)]

    def parse(self, response):
        urls = response.xpath('//article/a/@href').getall()

        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)
        
        url = response.url[:36] + '/'
        url_date = response.url[36:]

        next_indeks = int(response.xpath('//a[@class="active"]/text()').get()) + 1        
        
        next_indeks_url = url + str(next_indeks) + url_date
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)

    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="detail_text"]/p').extract()])
        konten = re.sub(r'[\n\r\t\xa0]','',konten)

        yield{
            'Judul' : response.xpath('//div[@class="container"]/h1/text()').get(),
            'Konten' : konten, 
            'Source' : 'cnbc',
            'Tanggal' : response.xpath('//div[@class="date"]/text()').get(),
            'Kategori' : response.xpath('//ul[@class="breadcrumb"]/li/text()').extract()[-1],
            'Konten_pisah' : "||".join(sent_tokenize(konten))
        }
