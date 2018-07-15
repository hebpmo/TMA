# coding: utf-8

"""
collector.xhn - 新华网数据采集

官网：http://www.xinhuanet.com/

接口分析：
1. 获取文章列表
http://qc.wa.news.cn/nodeart/list?nid=115093&pgnum=1&cnt=10000

新华全媒体头条
http://www.xinhuanet.com/politics/qmtt/index.htm
====================================================================
"""

import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from zb.crawlers.utils import get_header
import traceback
import pandas as pd

import tma

home_url = "http://www.xinhuanet.com/"


def get_website_map():
    wzdt_url = "http://www.xinhuanet.com/wzdt2014.htm"
    html = requests.get(wzdt_url, headers=get_header())
    bsobj = BeautifulSoup(html.content.decode('utf-8'), 'lxml')
    map_raw = bsobj.find('div', {'class': "content_left"})
    raise NotImplementedError


def get_special_topics(pgnum=1):
    """获取专题列表"""
    url = "http://qc.wa.news.cn/nodeart/list?" \
          "nid=115093&pgnum=%s&cnt=200" % str(pgnum)
    res = requests.get(url).text
    res = res.replace("null", "\'\'")
    res = eval(res)
    assert res['status'] == 0, "获取文章列表失败"
    data = res['data']['list']
    specials = []
    for a in data:
        special = {
            "Abstract": a['Abstract'],
            "Author": a['Author'],
            "LinkUrl": a['LinkUrl'],
            "PubTime": a['PubTime'],
            "Title": a['Title'],
            "allPics": a['allPics'],
        }
        specials.append(special)
    return specials


def get_article_detail(article_url):
    """获取新华网article_url中的文章内容

    :param article_url: 文章url
    :return:
        {
        "url": article_url,
        "title": title,
        "pub_time": pub_time,
        "source": source,
        "content": content
        }
    """
    # article_url = "http://www.xinhuanet.com/fortune/2018-06/20/c_129897476.htm"
    html = requests.get(article_url, headers=get_header())
    bsobj = BeautifulSoup(html.content.decode('utf-8'), 'lxml')

    # 解析标题
    cols = bsobj.find('div', {"class": "h-news"}).text.strip().split("\r\n")
    title = cols[0].strip()
    pub_time = cols[1].strip()
    source = cols[-1].strip()

    # 解析内容
    content = bsobj.find('div', {"id": "p-detail"}).text.strip()
    content = content.replace("\u3000\u3000", "")
    content = [x.strip() for x in content.split("\n")]
    content = [x for x in content if x != ""]
    content = "\n".join(content)

    return {
        "url": article_url,
        "title": title,
        "pub_time": pub_time,
        "source": source,
        "content": content
    }


class HomePage(object):
    """新华网首页"""

    def __init__(self):
        self.home_url = "http://www.xinhuanet.com/"

    @staticmethod
    def _get_date_from_url(url):
        pat = re.compile("(\d{4}-\d{2}[/-]\d{2})")
        res = pat.findall(url)
        if res is not None and len(res) == 1:
            return res[0].replace('/', "-")
        else:
            return None

    def get_article_list(self):
        """获取首页的头条文章列表"""
        html = requests.get(self.home_url, headers=get_header())
        bsobj = BeautifulSoup(html.content.decode('utf-8'), 'lxml')

        a_list = []
        for a in bsobj.find_all("a"):
            try:
                url = a['href']
                title = a.text.strip()
                d = self._get_date_from_url(url)
                a_list.append([url, title, d])
            except:
                if tma.DEBUG:
                    traceback.print_exc()
                continue

        a_list = [a for a in a_list if
                  a[0] != ""
                  and a[0].strip("/") != "http://xhgy.xinhuanet.com"
                  and a[0].startswith("http")
                  and a[1] != ""
                  and a[1] != "视频MP4地址"
                  and "c_" in a[0]
                  and 'photo' not in a[0]
                  and 'video' not in a[0]
                  ]

        # 根据url去重
        df = pd.DataFrame(a_list, columns=['url', 'title', 'date'])
        df.drop_duplicates('url', inplace=True)
        res = [list(x) for x in list(df.values)]
        return res

    def get_articles(self, d=None):
        """获取首页文章内容

        :param d: list
            限定获取文章的日期，默认是当日日期，可以指定多个离散的日期
        :return: list
        """
        if d is None:
            d = [datetime.now().date().__str__()]

        # 获取首页文章列表URL、按发布日期过滤、按URL去重
        a_list = self.get_article_list()
        a_list = [a[0] for a in a_list if a[2] in d]
        a_list = list(set(a_list))

        articles = []
        for a in a_list:
            try:
                article = get_article_detail(a)
                articles.append(article)
            except:
                if tma.DEBUG:
                    traceback.print_exc()
                continue
        return articles


class Fortune(object):
    def __init__(self):
        self.url1 = "http://www.xinhuanet.com/fortune/"
        self.url2 = "http://www.xinhuanet.com/fortune/caiyan.htm"
        self.url3 = "http://www.xinhuanet.com/fortune/cfx.htm"
        self.url4 = "http://www.xinhuanet.com/fortune/bcxc.htm"
