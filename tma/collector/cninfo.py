# -*- coding: UTF-8 -*-

"""
collector.cninfo - 采集巨潮咨询网的数据

官网：http://www.sse.com.cn/
====================================================================
"""

import requests
from datetime import datetime
from datetime import timedelta


# 获取上交所、深交所所有股票的最新公告
# --------------------------------------------------------------------

def _parse_latest(url, params):
    announcements = []
    while True:
        params['pageNum'] += 1
        res = requests.post(url, data=params).json()
        for items in res['classifiedAnnouncements']:
            # print(item)
            for item in items:
                announcement = {
                    "url": "http://www.cninfo.com.cn/" + item['adjunctUrl'],
                    "title": item['announcementTitle'],
                    "date": datetime.fromtimestamp(
                        item['announcementTime'] / 1000).date().__str__(),
                    "code": item['secCode'],
                    "name": item['secName']
                }
                announcements.append(announcement)
        if not res['hasMore']:
            break
    return announcements


def get_sh_latest():
    """获取上交所的最新公告列表"""
    url = "http://www.cninfo.com.cn/cninfo-new/disclosure/sse_latest"
    params = {
        "column": "sse",
        "columnTitle": "沪市公告",
        "pageNum": 0,
        "pageSize": 30,
        "tabName": "latest"
    }
    announcements = _parse_latest(url, params)
    return announcements


def get_sz_latest():
    """获取深交所的最新公告列表"""
    url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse_latest'
    params = {
        "column": "szse",
        "columnTitle": "深市公告",
        "pageNum": 0,
        "pageSize": 30,
        "tabName": "latest"
    }
    announcements = _parse_latest(url, params)
    return announcements


# 获取指定股票一段时间内的所有公告
# --------------------------------------------------------------------
def get_announcements(code, start_date=None, end_date=None):
    """获取公告列表

    :param code: str
        股票代码，如：600122
    :param start_date: str
        开始时间，如："2017-08-10"，默认值为今日想前推三十天的日期
    :param end_date: str
        结束时间，如："2018-08-10"，默认值为今日日期
    :return: announcements
    """
    if not start_date:
        start_date = datetime.now().date() - timedelta(days=30)
        start_date = str(start_date)
    if not end_date:
        end_date = datetime.now().date().__str__()

    url = "http://www.cninfo.com.cn/cninfo-new/announcement/query"

    params = {
        "stock": code,
        "searchkey": None,
        "category": None,
        "pageNum": 0,
        "pageSize": 30,
        "column": "szse_gem",
        "tabName": "fulltext",
        "sortName": None,
        "sortType": None,
        "limit": None,
        "seDate": "%s ~ %s" % (start_date, end_date)
    }

    announcements = []

    while True:
        params['pageNum'] += 1
        res = requests.post(url, data=params).json()
        for item in res['announcements']:
            announcement = {
                "url": "http://www.cninfo.com.cn/" + item['adjunctUrl'],
                "title": item['announcementTitle'],
                "date": datetime.fromtimestamp(
                    item['announcementTime'] / 1000).date().__str__(),
                "code": item['secCode'],
                "name": item['secName']
            }
            announcements.append(announcement)
        if not res['hasMore']:
            break

    return announcements
