import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize

class SindonewsSpider(scrapy.Spider):
    name = 'sindonews'
    start_urls = ['https://index.sindonews.com/index/?t=2020-05-{:02d}'.format(page) for page in range(1,2)]

    def parse(self, response):
        urls = response.xpath('//div[@class="indeks-title"]//a/@href').getall()        
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)
        
        next_indeks_url = response.xpath('//a[@rel="next"]/@href').get()
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)
 
    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@id="content"]').extract()])

        yield{
            'Judul' : response.xpath('//div[@class="article"]/h1/text()').get(),
            'Konten' : konten, 
            'Source' : 'Sindonews',
            'Tanggal' : response.xpath('//time/text()').get(),
            'Kategori' : response.xpath('//ul[@class="breadcrumb"]/li/a/text()').extract()[-1],
            'Konten_pisah' : "||".join(sent_tokenize(konten))
        }

