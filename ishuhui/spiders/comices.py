# -*- coding: utf-8 -*-
import scrapy
import requests
import re
from ishuhui.items import IshuhuiItem
from bs4 import BeautifulSoup

def get_zww_comices():
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
        num = re.findall('(\d+)', row.find('a').text)
        num = num[0] if num else '0'
        if title == '如龙添翼':
            num = '954'  # 站点话数bug修正
        title = f"第 {num} 话 {title.split('话：')[-1]}"
        title = re.sub(r'[\\/:*?"<>|\r\n]+', '', title)  # 去掉特殊字符
        details.append((num, title, url))
    return details


def get_fzdm_comices():
    list_url = 'https://manhua.fzdm.com/002/'
    headers = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
    }
    response = requests.get(list_url, headers=headers)
    rows = BeautifulSoup(response.text, 'lxml').find('div', id="content").find_all('li')
    details = []
    for row in rows:
        url = f"https://manhua.fzdm.com/002/{row.find('a').get('href')}"
        title = row.find('a').get('title')
        if '英文' in title:
            continue
        num = re.findall('(\d+)', title)
        num = num[0] if num else '0'
        title = re.sub(r'[\\/:*?"<>|\r\n]+', '', title)  # 去掉特殊字符
        if re.findall('[海贼王第|海贼王]\d+话|海贼王\d+', title) and '周年' not in title:
            title = re.findall('\[.*\]', title)
            title = f"第 {num} 话 {title[0]}" if title else f"第 {num} 话"
        elif re.findall('海贼王第\d+卷', title):
            title = f"第 {num} 卷"
        else:
            title = f"特别篇/{title}"
        details.append((num, title, url))
    return details


class ComicesSpider(scrapy.Spider):
    name = 'comices'
    allowed_domains = ['www.hanhande.net', 'manhua.fzdm.com']

    def start_requests(self):
        num = getattr(self, 'num', None)  # 下载第N话
        new = getattr(self, 'new', None)  # 下载最新几话
        tp = getattr(self, 'tp', 'fzdm')  # 选择下载类型 zww，fzdm
        details = get_zww_comices() if tp == 'zww' else get_fzdm_comices()
        callback = self.zww_parse if tp == 'zww' else self.fzdm_parse
        if new == 'all' or num == 'all':
            details = details
        elif new:
            details = details[:int(new)]
        elif num:
            details = [i for i in details if i[0] == num]
        for detail in details:
            num, title, url = detail
            yield scrapy.Request(url, meta={'title':title}, callback=callback)


    def zww_parse(self, response):
        # 一个页面包含所有图片 eg: 971话 http://www.hanhande.net/manhua/op/1158056.shtml
        # 一个页面只有一张图片 eg: 834话 http://www.hanhande.net/manhua/op/1153995.shtml
        # 判断页面类型，是否需要逐页请求
        select = BeautifulSoup(response.text, 'lxml').find('select', id="p__select")
        if select:
            rows = select.find_all('option')
            for px, row in enumerate(rows, 1):
                url = row.get('value')
                meta = {
                    'title': response.meta.get('title'),
                    'img_px': str(px)
                }
                yield scrapy.Request(url, meta=meta, callback=self.zww_parse)  # 逐页请求

        # 解析图片地址
        rows = BeautifulSoup(response.text, 'lxml').find('div', id="pictureContent").find_all('img')
        for px, row in enumerate(rows, 1):
            item = IshuhuiItem()
            item['title'] = response.meta.get('title')
            item['img_url'] = row.get('src')
            img_px = response.meta.get('img_px')
            px = img_px if img_px else str(px)
            item['img_name'] = f"{px}.{item['img_url'].split('.')[-1]}"
            yield item


    def fzdm_parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        # 解析图片地址
        item = IshuhuiItem()
        mhurl = re.findall('mhurl="(.*?)"', response.text, re.S)[0]
        mhurl = f"http://www-mipengine-org.mipcdn.com/i/p2.manhuapan.com/{mhurl}"
        # if mhurl .split('/')[0] in ('2016', '2017', '2018', '2019', '2020'):
        #     mhurl = f"http://www-mipengine-org.mipcdn.com/i/p2.manhuapan.com/{mhurl}"
        # else:
        #     mhurl = f"http://www-mipengine-org.mipcdn.com/i/p1.manhuapan.com/{mhurl}"
        item['title'] = response.meta.get('title')
        item['img_url'] = mhurl
        px = response.meta.get('img_px', 1)
        item['img_name'] = f"{px}.{item['img_url'].split('.')[-1]}"
        yield item

        # 请求下一页
        next = soup.find('a', text='下一页')
        if next:
            url = response.urljoin(next.get('href'))
            meta = {
                'title': response.meta.get('title'),
                'img_px': str(int(px)+1)
            }
            yield scrapy.Request(url, meta=meta, callback=self.fzdm_parse)