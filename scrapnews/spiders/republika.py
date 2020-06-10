import scrapy
import w3lib.html as w3
import spacy
import re
from nltk.tokenize import sent_tokenize

class RepublikaSpider(scrapy.Spider):
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'republika.csv'
    }

    name = 'republika'
    start_urls = ['https://www.republika.co.id/index/2020/05/{:02d}'.format(page) for page in range(1,31)]

    def parse(self, response):
        urls = response.xpath('//div[@class="txt_subkanal txt_index"]/h2/a/@href').getall()        
        if urls:
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parseNews)
        else:
            exit(0)

        next_indeks_url = response.xpath('//nav[@role="navigation"]/a/@href').extract()[-1]
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)

    def parseNews(self, response):
        konten = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="artikel"]/p').extract()])
        konten = re.sub(r'[\n\r\t\xa0]','',konten)
        
        kategori = re.sub(r'\s+','',response.xpath('//div[@class="breadcome"]/ul/li/a/text()').extract()[-1])
        
        not_kategori = ['Inpicture','Video','Infografis','']

        if kategori not in not_kategori:
            yield{
                'Judul' : w3.remove_tags(response.xpath('//div[@class="wrap_detail_set"]/h1').get()),
                'Konten' : konten, 
                'Sumber' : 'republika',
                'Tanggal' : response.xpath('//div[@class="date_detail"]/p/text()').get(),
                'Kategori' : kategori,
                'Konten_pisah' : "||".join(sent_tokenize(konten)),
                'Url' : response.url
            }
