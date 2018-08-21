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
import pandas as pd


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


def get_fund_flow(kind):
    """获取同花顺最新的行业/概念资金流

    :param kind: str
        指明需要获取的资金流类型，可选值 ['hyzjl', 'gnzjl']
        hyzjl - 行业资金流
        gnzil - 概念资金流
    :return: pd.DataFrame
        ['序号', '行业', '行业指数', '涨跌幅', '流入资金(亿)', '流出资金(亿)',
        '净额(亿)', '公司家数', '领涨股', '涨跌幅', '当前价(元)']
    """
    if kind not in ['hyzjl', 'gnzjl']:
        raise ValueError("kind 必须是 ['hyzjl', 'gnzjl'] 中的一个值")

    url_template = "http://data.10jqka.com.cn/funds/{kind}/field/" \
                   "tradezdf/order/desc/page/{page}/ajax/1/"

    i = 1
    results = []
    while 1:
        url = url_template.format(page=i, kind=kind)
        response = requests.get(url, headers=get_header())
        html = BeautifulSoup(response.text, 'lxml')

        table = html.find('table', {'class': "m-table J-ajax-table"}).text.strip()
        cells = table.split("\n")
        col_nums = 13
        row_nums = int(len(cells) / col_nums)
        col_names = cells[0: 11]
        for x in range(1, row_nums):
            results.append(cells[x * col_nums + 2: (x + 1) * col_nums])

        # 判断是否是尾页
        is_last_page = "尾页" not in html.find('div', {'class': "m-page J-ajax-page"}).text
        if is_last_page:
            break
        else:
            i += 1
    return pd.DataFrame(results, columns=col_names)
