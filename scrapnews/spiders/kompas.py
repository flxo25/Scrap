import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize


class KompasSpider(scrapy.Spider):
    name = 'kompas'  
    start_urls = ['https://news.kompas.com/search/2020-05-{}'.format(page) for page in range(1,2)]

    def parse(self, response):
        urls = response.xpath('//h3[@class="article__title article__title--medium"]//a/@href').getall()        
        for url in urls:
            if url:
                url = url + '?page=all'
                yield scrapy.Request(url=url, callback=self.parseNews)

        next_indeks_url = response.xpath('//a[@rel="next"]/@href').get()
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)
    

    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="read__content"]/p').extract()])

        yield{
            'Judul' : response.xpath('//h1[@class="read__title"]/text()').get(),
            'Konten' : konten, 
            'Source' : 'Kompas',
            'Tanggal' : response.xpath('//div[@class="read__time"]/text()').get()[13:],
            'Kategori' : response.xpath('//span[@itemprop="name"]/text()')[-1].get(),
            'Konten_pisah' : "||".join(sent_tokenize(konten))
        }

