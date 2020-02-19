# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import os
import re

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request


class IshuhuiImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        meta= {}
        meta['title'] = item['title']
        meta['num'] = item['num']
        meta['img_name'] = item['img_name']
        yield Request(item['img_url'],meta=meta)

    def file_path(self, request, response=None, info=None):
        num = request.meta['num']
        img_name = request.meta['img_name']
        title = re.sub(r'[\\/:*?"<>|\r\n]+', '', request.meta['title'])
        filename = f'海賊王\第 {num} 话 {title}\{img_name}'
        return filename

    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]
        if not image_path:
            raise DropItem('Item contains no images')
        item['image_paths'] = image_path
        return item