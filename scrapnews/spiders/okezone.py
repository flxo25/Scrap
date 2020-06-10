import scrapy
import w3lib.html as w3
import spacy
from nltk.tokenize import sent_tokenize

class OkezoneSpider(scrapy.Spider):
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'okezone2.csv'
    }
    
    name = 'okezone'
    start_urls = ['https://index.okezone.com/bydate/index/2020/05/{:02d}'.format(page) for page in range(1,2)]

    def parse(self, response):
        urls = response.xpath('//h4[@class="f17"]/a/@href').getall()        
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parseNews)

        first_url = response.xpath('//div[@class="time r1 fl bg1 b1"]/a/@href').extract()[-1][:50]
        next_indeks = int(response.xpath('//div[@class="time r1 fl bg1 b1"]/strong/text()').get()[1:]) 
        
        next_indeks_url = first_url + str(next_indeks*15)
        if next_indeks_url:
            yield scrapy.Request(url=next_indeks_url, callback=self.parse)

    def parseNews(self, response):
        data = dict()

        #judul
        data['Judul'] = w3.remove_tags(response.xpath('//div[@class="title"]/h1').extract_first())

        #konten
        konten_kotor = " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="read"]/p').extract()])

        if len(response.xpath('//div[@class="read"]/p/strong').extract()) != 1:
            noise1 = [w3.remove_tags(item) for item in response.xpath('//div[@class="read"]/p/strong').extract()][1:]
        else:
            noise1 = ''

        if noise1:
            if len(noise1) == 1:
                konten_kotor = konten_kotor.replace(noise1[0],'')
            else:
                for noise in noise1:
                    konten_kotor = konten_kotor.replace(noise,'')
        
        data['Konten'] = konten_kotor.replace('\n','')

        #sumber
        data['Source'] = 'Okezone'

        #tanggal
        data['Tanggal'] = response.xpath('//div[@class="namerep"]/b/text()').get()

        #kategori
        data['Kategori'] = response.xpath('//div[@class="breadcrumb"]/ul/li/a/text()').extract()[-1]

        # #konten pisah
        data['Konten_pisah'] = "||".join(sent_tokenize(data['Konten']))

        #Url
        data['URL'] = response.url

        #next page
        if response.xpath('//div[@class="second-paging"]/text()').get() != '1':
            next_page = response.xpath('//div[@class="next"]/a/@href').get()
        else:
            next_page = ''

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.next,meta=data)
        
        yield data

    def next(self, response):
        response.meta['Konten'] = response.meta['Konten'] + " ".join([w3.remove_tags(item) for item in response.xpath('//div[@class="read"]/p').extract()])
        response.meta['Konten'] = response.meta['Konten'].replace('\n','')
        response.meta['Konten_pisah'] = "||".join(sent_tokenize(response.meta['Konten']))

        yield response.meta