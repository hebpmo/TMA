# -*- coding: UTF-8 -*-

"""
collector.ths - 采集同花顺数据

官网：http://www.10jqka.com.cn
数据中心：http://data.10jqka.com.cn/
====================================================================
"""

import requests
from bs4 import BeautifulSoup
from zb.crawlers.utils import get_header
import re


def zao_pan():
    """获取同花顺早盘必读信息"""
    url = "http://stock.10jqka.com.cn/zaopan/"
    response = requests.get(url, headers=get_header())
    html = BeautifulSoup(response.text, 'lxml')

    # 名人名言
    wisdom = html.find('div', {'class': "select-content"}).text.strip()

    # 昨日收盘
    yesterday = html.find('div', {'class': 'yestoday'}).text.strip()
    yesterday = yesterday.replace("&nbsp&nbsp", "|")

    # 今日关注
    content = html.find('div', {'class': "content-main-fl fl"}).text.strip()
    content = re.sub('[ \u3000]', "\n", content)

    res = [wisdom, yesterday, content]

    return "\n\n".join(res)
