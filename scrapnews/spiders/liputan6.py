import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize
import re

class Liputan6Spider(scrapy.Spider):
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'liputan6.csv'
    }
    
    name = 'liputan6'
    start_urls = ['https://www.liputan6.com/news/indeks/2020/05/{:02d}'.format(page) for page in range(1,31)]

    def parse(self, response):
        urls = response.xpath('//a[@class="articles--rows--item__title-link"]/@href').getall()        
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)
        
        next_indeks_url = response.xpath('//a[@id="next"]/@href').get()
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)
 
    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="article-content-body__item-content"]/p').extract()])
        konten = re.sub(r'[\n\r\t\xa0]','',konten)

        yield{
            'Judul' : response.xpath('//h1[@itemprop="headline"]/text()').get(),
            'Konten' : konten, 
            'Sumber' : 'liputan6',
            'Tanggal' : response.xpath('//time[@itemprop="datePublished"]/text()').get(),
            'Kategori' : response.xpath('//a[@class="read-page--breadcrumb--item__title"]/span/text()').extract()[-1],
            'Konten_pisah' : "||".join(sent_tokenize(konten)),
            'Url' : response.url
        }

