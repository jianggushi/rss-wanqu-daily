#!/usr/bin/python3
import feedparser
import re
from lxml import etree
import logging
import os
import requests

rss_url = 'https://wanqu.co/feed/'
ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
referer = 'https://wanqu.co/'

LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(filename='rss.log', level=logging.INFO, format=LOG_FORMAT)

logging.info('start fetch rss 湾区日报')

# 上一次获取的 rss title，避免重复获取
try:
    with open ('rss.last', 'r') as f:
        rss_last = f.read()
except:
    rss_last = ''
logging.info('last fetched ' + rss_last)

rss = {}
# 获取 rss 数据
resp = feedparser.parse(rss_url, agent=ua, referrer=referer)
# print(resp)

# 解析 title
title = re.search(r'湾区日报第\d+期', resp['feed']['title']).group()
if title == rss_last:
    logging.info('not new rss')
    os._exit(1)
rss['title'] = title

# 解析 link
link = resp['feed']['link']
rss['link'] = link

# 解析 item
items = []
for i in range(5):
    item = resp['entries'][i]
    item_title = item['title']
    html = etree.HTML(item['summary'])
    item_summary = ''.join(html.xpath('//p//text()'))
    items.append({'title': item_title, 'summary': item_summary})
rss['items'] = items

# 保存 rss-md
try:
    os.mkdir('rss-md')
except:
    pass
with open(os.path.join('rss-md', title+'.md'), 'w') as f:
    f.write('#### ')
    f.write(rss['title'])
    f.write('\n\n')
    for item in rss['items']:
        f.write('##### ')
        f.write(item['title'])
        f.write('\n\n')
        f.write(item['summary'])
        f.write('\n\n')
    f.write('------')
    f.write('\n\n')
    f.write('来自『湾区日报』（ <https://wanqu.co> ）')
    f.write('\n\n')
    f.write('相关推荐')
    f.write('\n\n')
    f.write('更多详细内容 ↓↓↓')
    f.write('\n\n')
    f.write(rss['link'])
    f.write('\n')

# 保存 rss-data
try:
    os.mkdir('rss-data')
except:
    pass
with open(os.path.join('rss-data', title+'.rss'), 'w') as f:
    resp = requests.get(rss_url).text
    f.write(resp)

# 上一次获取的 rss title，避免重复获取
with open ('rss.last', 'w') as f:
    f.write(title)

logging.info('end fetch ' + title)