import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize

class OkezoneSpider(scrapy.Spider):
    name = 'okezone'
    start_urls = ['https://index.okezone.com/bydate/index/2020/05/{:02d}'.format(page) for page in range(1,2)]

    def parse(self, response):
        urls = response.xpath('//h4[@class="f17"]//a/@href').getall()        
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)

        first_indeks = response.xpath('//div[@class="time r1 fl bg1 b1"]/a/@href').extract()[-1][:50]
        last_indeks = int(response.xpath('//div[@class="time r1 fl bg1 b1"]/a/@href').extract()[-1][50:-1])+1 
        
        for i in range(15,last_indeks,15):
            next_indeks_url = first_indeks + str(i)
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)

 
    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="read"]/p').extract()])
        konten = konten.replace('\n','')

        yield{
            'Judul' : w3.remove_tags(response.xpath('//div[@class="title"]/h1').extract_first()),
            'Konten' : konten, 
            'Source' : 'Okezone',
            'Tanggal' : response.xpath('//div[@class="namerep"]/b/text()').get(),
            'Kategori' : response.xpath('//div[@class="breadcrumb"]/ul/li/a/text()').extract()[-1],
            'Konten_pisah' : "||".join(sent_tokenize(konten))
        }

