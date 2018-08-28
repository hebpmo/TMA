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


def http_requests(url):
    response = requests.get(url, headers=get_header())
    if response.status_code == 200:
        html = BeautifulSoup(response.text, 'lxml')
        return html
    else:
        raise ValueError("返回状态码（%s）不是200，url采集失败"
                         % str(response.status_code))


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


# 板块数据
# --------------------------------------------------------------------
def get_ths_plates():
    """获取同花顺所有概念列表

    :return: pd.DataFrame
        ['code', 'kind', 'name', 'url']
    """
    plate_kinds = {
        'gn': "概念板块",
        'dy': "地域板块",
        'thshy': "同花顺行业",
        'zjhhy': "证监会行业"
    }
    plates = []
    for kind in plate_kinds.keys():
        url = "http://q.10jqka.com.cn/%s/" % kind
        response = requests.get(url, headers=get_header())
        html = BeautifulSoup(response.text, "lxml")

        results = html.find("div", {"class": "category boxShadow m_links"}).find_all("a")

        for a in results:
            url = a['href']
            plate = {
                "name": a.text,
                "code": url.strip("/").split('/')[-1],
                "url": url,
                "kind": plate_kinds[kind]
            }
            plates.append(plate)

    return pd.DataFrame(plates)


def get_plate_fund_flow(kind):
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


def get_plate_shares(plate_code, kind='gn'):
    """从同花顺网站获取板块中所有股票的行情

    :param plate_code: str
        板块代码，可以在这里查找对应的板块代码：http://q.10jqka.com.cn/gn/
    :param kind: str
        板块类型，可选值：['gn', 'thshy']
        gn      概念板块
        thshy   同花顺行业板块
    :return: pd.DataFrame
        ['序号', '代码', '名称', '现价', '涨跌幅(%)', '涨跌', '涨速(%)',
        '换手(%)', '量比', '振幅(%)', '成交额', '流通股', '流通市值', '市盈率']
    """
    url_template = "http://q.10jqka.com.cn/{kind}/detail/order/desc/" \
                   "page/{page}/ajax/1/code/{code}"

    kind_values = ['gn', 'thshy']
    if kind not in kind_values:
        raise ValueError("kind参数的取值必须在 %s 中" % kind_values)

    i = 1
    results = []
    while 1:
        url = url_template.format(kind=kind, page=i, code=plate_code)
        response = requests.get(url, headers=get_header())
        html = BeautifulSoup(response.text, 'lxml')

        table = html.find('table', {'class': "m-table m-pager-table"}).text.strip()
        cells = table.split("\n")
        col_nums = 17
        row_nums = int(len(cells) / col_nums)
        col_names = [x.strip() for x in cells[0: 14]]
        for x in range(1, row_nums + 1):
            results.append(cells[x * col_nums + 2: (x + 1) * col_nums - 1])

        # 判断是否是尾页
        is_last_page = "尾页" not in html.find('div', {'class': "m-pager"}).text
        if is_last_page:
            break
        else:
            i += 1
    return pd.DataFrame(results, columns=col_names)


# 个股F10
# --------------------------------------------------------------------

class ThsF10(object):
    def __init__(self, code):
        self.code = code
        self.base_url = "http://basic.10jqka.com.cn/" \
                        "{code}/".format(code=code)

    def get_company_info(self):
        """

        页面案例：http://basic.10jqka.com.cn/600682/company.html

        :return:
        """
        base_url = self.base_url
        url = base_url + "company.html"
        html = http_requests(url)

        # 公司基本资料
        table1 = html.find('table', {"class": "m_table"})
        table1_info = [x for x in table1.text.strip().split('\n')
                       if x != ""]
        table2 = html.find('table', {"class": "m_table ggintro"})
        table2_info = [re.sub("[\t\u3000 &nbsp▼▲]", '', x) for x
                       in table2.text.strip().split('\n')
                       if x != ""]
        detail_info = table1_info + table2_info

        # 董、监、高
        m_tab_content = html.find_all('div', {'class': "m_tab_content"})
        m_tab_content_infos = []
        for table in m_tab_content:
            info = [re.sub("[ ]", '', x) for x
                    in table.text.strip().split('\n') if x != ""]
            m_tab_content_infos.append(info)

        # 发行相关
        bd_pr = html.find('div', {'class': "bd pr"}).table
        pr_info = [x for x in bd_pr.text.strip().split('\n')
                   if x != '' and x != " "]
        del pr_info[-2]
        pr_info[-1] = pr_info[-1].replace("收起▲", "")

        return {
            "详细情况": detail_info,
            "董监高": m_tab_content_infos,
            "发行相关": pr_info
        }

    def get_concept_info(self):
        base_url = self.base_url
        url = base_url + "concept.html"
        html = http_requests(url)

        def _clear(data):
            # 清理多余的数据
            while 1:
                try:
                    i = data.index('展开')
                except ValueError:
                    break
                del data[i - 1:i + 1]
            return data

        # 概念
        gn_tables = html.find_all('table', {'class': "gnContent"})
        gn_infos = []
        for table in gn_tables:
            gn = [x.strip() for x in table.text.strip().split("\n")
                  if x.strip() != ""]
            gn = _clear(gn)
            gn_infos.append(gn)

        # 题材要点
        tcyd = html.find_all('div', {'class': "gntc"})[2]
        tcyd_info = [x.strip(" \t \xa0>") for x in tcyd.text.strip().split("\n")
                     if x.strip(" \t \xa0>") != ""]
        tcyd_info = _clear(tcyd_info)

        return {
            "概念题材": gn_infos,
            "题材要点": tcyd_info
        }
