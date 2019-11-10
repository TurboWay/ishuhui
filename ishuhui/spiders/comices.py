# -*- coding: utf-8 -*-
import scrapy
import requests
import json
from ..items import IshuhuiItem

class ComicesSpider(scrapy.Spider):
    name = 'comices'
    allowed_domains = ['www.ishuhui.com']

    def start_requests(self):
        lt = get_comices()
        num = getattr(self, 'num', None) # 下载第N话
        new = getattr(self, 'new', None) # 下载最新几话
        if new:
            lt = lt[-1*int(new):]
        if num:
            lt = [i for i in lt if i[0] == num]
        for id in lt:
            url = 'https://prod-api.ishuhui.com/comics/detail?id={0}'.format(id[1])
            yield scrapy.Request(url)

    def parse(self, response):
        dt = json.loads(response.text)
        item = IshuhuiItem()
        item.update(animeName = dt['data']['animeName'])
        item.update(num = dt['data']['numberStart'])
        item.update(title = dt['data']['title'])
        for img in dt['data']['contentImg']:
            item.update(img_url = img.get('url'))
            item.update(img_name = img.get('name'))
            yield item

def get_comices():
    listapi = 'https://prod-api.ishuhui.com/ver/4e198319/anime/detail?id=1&type=comics&.json'
    dt = json.loads(requests.get(listapi).text)
    nums = dt['data']['comicsIndexes']['1']['nums']
    lt = []
    for range_index, range in nums.items():
        for page_index, page in range.items():
            for row in page:
                if row.get('sourceID') == 1:
                    i = (page_index, row.get('id'))
                    lt.append(i)
    return lt
