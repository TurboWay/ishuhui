# -*- coding: utf-8 -*-
import scrapy
import requests
import re
from ishuhui.items import IshuhuiItem
from bs4 import BeautifulSoup

class ComicesSpider(scrapy.Spider):
    name = 'comices'
    allowed_domains = ['www.hanhande.net']

    def start_requests(self):
        num = getattr(self, 'num', None)  # 下载第N话
        new = getattr(self, 'new', None)  # 下载最新几话
        details = get_comices()
        if new:
            details = details[:int(new)]
        if num:
            details = [i for i in details if i[0] == num]
        for detail in details:
            num, title, url = detail
            meta = {
                'num': num,
                'title': title
            }
            yield scrapy.Request(url, meta=meta)

    def parse(self, response):
        # 一个页面包含所有图片 eg: 971话 http://www.hanhande.net/manhua/op/1158056.shtml
        # 一个页面只有一张图片 eg: 834话 http://www.hanhande.net/manhua/op/1153995.shtml
        # 判断页面类型，是否需要逐页请求
        select = BeautifulSoup(response.text, 'lxml').find('select', id="p__select")
        if select:
            rows = select.find_all('option')
            for px, row in enumerate(rows, 1):
                url = row.get('value')
                meta = {
                    'num': response.meta.get('num'),
                    'title': response.meta.get('title'),
                    'img_px': str(px)
                }
                yield scrapy.Request(url, meta=meta)  # 逐页请求

        # 解析图片地址
        rows = BeautifulSoup(response.text, 'lxml').find('div', id="pictureContent").find_all('img')
        for px, row in enumerate(rows, 1):
            item = IshuhuiItem()
            item['num'] = response.meta.get('num')
            item['title'] = response.meta.get('title')
            item['img_url'] = row.get('src')
            img_px = response.meta.get('img_px')
            px = img_px if img_px else str(px)
            item['img_name'] = f"{px}.{item['img_url'].split('.')[-1]}"
            yield item

# 获取漫画目录
def get_comices():
    list_url = 'http://www.hanhande.net/manhua/op/'
    headers = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
    }
    response = requests.get(list_url, headers=headers)
    response.encoding = 'gb2312'
    rows = BeautifulSoup(response.text, 'lxml').find('ul', id="g1").find_all('li')
    details = []
    for row in rows:
        url = row.find('a').get('href')
        title = re.sub('海贼王\d+话[ |:|：]', '', row.find('a').get('title'))
        title = title.split('话：')[-1]
        num = re.sub('[话|集]', '', row.find('a').text)
        details.append((num, title, url))
    return details