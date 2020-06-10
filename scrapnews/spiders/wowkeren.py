import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize
import re

class WowkerenSpider(scrapy.Spider):
    name = 'wowkeren'
    start_urls = ['https://www.wowkeren.com/berita/page/{}/'.format(page) for page in range(60,283)]

    def parse(self, response):
        urls = response.xpath('//h3[@class="title-semibold-dark size-lg mb-15"]/a/@href').getall()        
        for url in urls:
            if url:
                yield scrapy.Request(url="https://www.wowkeren.com"+url, callback=self.parseNews)
 
    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//p').extract()])
        pat1 = r"var.+;"
        pat2 = r"You can.+"
        pat3 = r"[\n\r\t\xa0]"
        pat = "|".join([pat1,pat2,pat3])
        
        konten = re.sub(pat,'',konten)
        # w3.remove_tags(response.xpath('//h2[@class="title-semibold-dark size-c30"]').get())

        yield{
            'Judul' : w3.remove_tags(response.xpath('//h2[@class="title-semibold-dark size-c30"]').get()),
            'Konten' : konten, 
            'Sumber' : "wowkeren",
            'Tanggal' : response.xpath('//ul[@class="post-info-dark mb-30"]/li/text()').extract()[-1],
            'Kategori' : response.xpath('//div[@class="topic-box-sm color-cinnabar mb-20"]/text()').get(),
            'Konten_pisah' : "||".join(sent_tokenize(konten)),
            'URL' : response.url
        }

