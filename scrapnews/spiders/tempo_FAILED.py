import scrapy
import w3lib.html as w3
import spacy
import re
from nltk.tokenize import sent_tokenize


class TempoSpider(scrapy.Spider):
    name = 'tempo'
    start_urls = ['https://www.tempo.co/indeks/2020/04/{:02d}'.format(page) for page in range(1,2)]

    def parse(self, response):
        urls = response.xpath('//div[@class="wrapper clearfix"]/a/@href').getall()        
    
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)
    
    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@id="isi"]/p').extract()])
        konten = re.sub(r'[\n\r\t\xa04]','',konten)

        yield{
            'Judul' : re.sub(r'[\n\r\t]','',response.xpath('//h1[@itemprop="headline"]/text()').get()),
            'Konten' : konten, 
            'Source' : 'Tempo',
            'Tanggal' : response.xpath('//span[@itemprop="datePublished"]/text()').get(),
            'Kategori' : response.xpath('//span[@itemprop="name"]/text()').extract()[-1],
            'Konten_pisah' : "||".join(sent_tokenize(konten))
        }
