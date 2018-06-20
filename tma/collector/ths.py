# -*- coding: UTF-8 -*-

"""
collector.ths - 采集同花顺数据

官网：http://www.10jqka.com.cn
数据中心：http://data.10jqka.com.cn/
====================================================================
"""

import requests
from bs4 import BeautifulSoup



def get_market_level():
    url = "http://q.10jqka.com.cn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ '
                      '(KHTML, like Gecko, Safari/419.3) Arora/0.6'
    }
    html = requests.get(url, headers=headers)
    html = BeautifulSoup(html.text, 'lxml')
    rate = html.find('div', {'class': "hcharts-right"})
    res = html.find('p', {'id': "hcharts-right"})
    pass
