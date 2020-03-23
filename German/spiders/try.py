# -*- coding:utf-8 -*-
import scrapy
import re
import jsonlines
import datetime
import json

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
#from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request

from German.items import GermanItem
#from German.utils import get_first
comments={}
num=0
    name = 'try'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }
    start_urls = [
        'http://to.welt.de/6ngZF0Y',
        'https://www.welt.de/politik/deutschland/article205666551/Thueringen-CDU-Schaeuble-lobt-AKK-fuer-entschiedene-Haltung.html'
    # Comments
    ]
    comment_initial_url="https://api-co.la.welt.de/api/comments?document-id=%s&sort=NEWEST&limit=100"
    comment_base_url='https://api-co.la.welt.de/api/comments?document-id=%s&created-cursor=%s&sort=NEWEST&limit=100'
    def parse(self, response):
        """Scrapes information from pages into items"""
        item = GermanItem()
 #       item['url'] = response.url.encode('utf-8')
        #item['time_published'] = datetime.datetime.now().isoformat().encode('utf-8')
        #item['published'] = get_first(response.selector.xpath('//meta[@name="date"]/@content').extract())
        item['title'] = response.xpath('//*[@id="top"]/main/article/div[1]/header/div[*]/div/h2/text()').extract()[0].encode('utf-8')
        item['published_time']=response.xpath('//*[@id="top"]/main/article/div[1]/header/div[2]/time/@datetime').extract()[0].encode('utf-8')
        item['description']=response.xpath('//*[@id="top"]/main/article/div[1]/header/div[5]/div/div/text()').extract()[0].encode('utf-8')
        item['text'] = response.xpath('//*[@id="top"]/main/article/div[1]/div[2]/p[1]/span/text()').extract()[0].encode('utf-8')
        for i in range(100):
            try:
                text =response.xpath('//*[@id="top"]/main/article/div[1]/div[2]/p['+str(i)+']/text()').extract()[0].encode('utf-8')
                item['text']+=text
                try:
                    for j in range(0,200):
                        text = response.xpath('//*[@id="top"]/main/article/div[1]/div[2]/p[' + str(i) + ']/a/text()').extract()[j].encode('utf-8')
                        item['text'] += text
                        text = response.xpath('//*[@id="top"]/main/article/div[1]/div[2]/p[' + str(i) + ']/text()').extract()[j+1].encode('utf-8')
                        item['text'] += text
                except:
                    item['text']+='\n'
                    pass
            except:
                pass
        document_id=self.extract_article_id(response.url)
        print document_id
        item['comments_num']=response.xpath('//*[@id="top"]/main/article/div[1]/div[1]/div/div[1]/span/a/span[2]/text()').extract()[0].encode('utf-8')
        print(item['comments_num'])
        item['comments_num']="10"
        url=self.comment_initial_url % document_id
        yield Request(url, self.parse_comments, method="GET", priority=1,dont_filter=True)
        with open('article.json','a') as wf:
            wf.write(json.dumps(item['comments']))
        #response.xpath().extract()

        for i in item:
            print i,item[i]
        #item['description'] = get_first(response.selector.xpath('//meta[@name="description"]/@content').extract())
        #item['text'] = "".join([s.strip().encode('utf-8') for s in response.selector.css('.artContent').xpath('.//text()').extract()])
        #item['author'] = [s.encode('utf-8') for s in response.selector.xpath('//meta[@name="author"]/@content').extract()]
        #item['keywords'] = [s.encode('utf-8') for s in response.selector.xpath('//meta[@name="keywords"]/@content').extract()]
        #return item

    def extract_article_id(self, url):
        article = re.search('article(\d+)', url).group(1)
        return re.search('(\d+)', article).group(1)
    def parse_comments(self,response):
        global num
        item = GermanItem()
        item['comments']={}
        print response.url+'\n'
        comments_json = json.loads(response.body)
        comments_raw = comments_json['comments']
        comments_raw
        d_id=0
        num+=1
        print num
        print(len(comments))
        for comment in comments_raw:
            new = {}
            new['text'] = comment['contents'].encode('utf-8')
            new['time'] = comment['created']
            new['id'] = comment['id']
            new['like']=comment['likes']
            new['child_count']=comment['childCount']
            new['child_comments']=[]
            item['comments'][comment['id']] = new
            try:
                parent_id = comment['parentId']
                item['comments'][parent_id]['child_comments'].append(new)
            except:
                d_id=comment['documentId']
                d_time=comment['created']
                pass
        if d_id==0:
            return
        url=self.comment_base_url %(d_id,d_time)
        yield Request(url, self.parse_comments, method="GET", priority=10,dont_filter=True)
