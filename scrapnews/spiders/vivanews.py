import scrapy
import w3lib.html as w3
import spacy
import re
from nltk.tokenize import sent_tokenize


class VivanewsSpider(scrapy.Spider):
    name = 'vivanews'
    start_urls = ['https://www.vivanews.com/indeks/all/all/2020/05/{:02d}'.format(page) for page in range(1,2)]

    def parse(self, response):
        urls = response.xpath('//a[@class="al-title"]/@href').getall()        
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)
    
    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@id="article-detail-content"]/p').extract()])
        konten = re.sub(r'[\n\r\t\xa04]','',konten)

        yield{
            'Judul' : response.xpath('//li[@class="dtb-title"]/h1/text()').get(),
            'Konten' : konten, 
            'Source' : 'vivanews',
            'Tanggal' : response.xpath('//li[@class="dtb-date"]/h6/text()').get(),
            'Kategori' : response.xpath('//a[@class="breadcrumb-step content_center"]/h4/text()').extract()[-1],
            'Konten_pisah' : "||".join(sent_tokenize(konten))
        }
