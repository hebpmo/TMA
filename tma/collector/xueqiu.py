# -*- coding: UTF-8 -*-

"""
collector.xueqiu - 采集雪球数据

官网：https://xueqiu.com/
====================================================================
"""

import requests
import time
import json
from collections import OrderedDict
from bs4 import BeautifulSoup
import webbrowser
from zb.crawlers.utils import get_header
import traceback

XUEQIU_HOME = "https://xueqiu.com/"


def make_symbol(code):
    if code.startswith("6"):
        symbol = "SH" + code
    elif code.startswith("3") or code.startswith("0"):
        symbol = "SZ" + code
    else:
        raise ValueError("构造雪球symbol失败，code应当以0/3/6开头")
    return symbol


def open_xueqiu(code):
    """打开code在雪球的页面

    :param code: 股票代码，如 603655
    :return:
    """
    symbol = make_symbol(code)
    url = "https://xueqiu.com/S/" + symbol
    webbrowser.open(url)


def get_raw_response(raw):
    """从浏览器访问雪球的原始请求中获取数据

    :param raw: str
        从浏览器复制的访问雪球的原始请求，包含cookies等信息，如：
        raw =
            GET /stock/screener/screen.json?category=SH&exchange=&areacode=&indcode=&orderby=symbol&order=desc&current=ALL&pct=ALL&page=1&mc=0_30&eps.20180331=0.2_6.77&_=1532157090470 HTTP/1.1
            Host: xueqiu.com
            Connection: keep-alive
            Accept: application/json, text/javascript, */*; q=0.01
            cache-control: no-cache
            DNT: 1
            X-Requested-With: XMLHttpRequest
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36
            Referer: https://xueqiu.com/hq/screener
            Accept-Encoding: gzip, deflate, br
            Accept-Language: en-US,en;q=0.9
            Cookie: device_id=93f4ed2cb55c692c95f053da19015b52; s=fq11y14kj3; bid=e0902c871217c79df259eb5d83f46eae_j950845q; _ga=GA1.2.1448042712.1508812875; __utmz=1.1527436687.45.17.utmcsr=sogou.com|utmccn=(referral)|utmcmd=referral|utmcct=/link; __utma=1.1448042712.1508812875.1528039186.1529730232.49; remember=1; remember.sig=K4F3faYzmVuqC0iXIERCQf55g2Y; xq_a_token=6ff26751fa685eb1ceab508fcb1c6b0556ef650a; xq_a_token.sig=wSoXzThiLbzH4mXexFY2U11fUzM; xq_r_token=5a288141cd3742deacc30e09eda6d0de65501ced; xq_r_token.sig=Hp0vJJ_CRQXm_3ATbMMnyspaIBA; xq_is_login=1; xq_is_login.sig=J3LxgPVPUzbBg3Kee_PquUfih7Q; u=3987902339; u.sig=wHo1L73HiVC2HlUxrHqBNa63rVo; aliyungf_tc=AQAAAO0MKVFvPwIAyD88OjvS/B9ge3BR; Hm_lvt_1db88642e346389874251b5a1eded6e3=1531897634,1531985157,1532156465,1532157061; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1532157061

    :return: response requests.Response
        原始请求对应返还的数据
    """
    raw_req = raw.strip("\n").split("\n")
    raw_req = [r.strip(" ") for r in raw_req]
    raw_req = [r for r in raw_req if r != ""]
    headers = dict()
    for r in raw_req[1:]:
        k, v = r.split(": ")
        headers[k] = v
    url = "https://" + headers['Host'] + raw_req[0].split(" ")[1]
    response = requests.get(url, headers=headers)
    return response


def get_comments(code, sleep=1):
    """获取股票code的雪球评论

    :param str code: 股票代码，如 `600122`
    :param float sleep: 睡眠时间， 默认值为 1
    :return:
    """
    headers = get_header()
    sess = requests.Session()

    # 访问首页，获取cookies
    sess.get(XUEQIU_HOME, headers=headers, timeout=10)

    # 获取首页评论
    symbol = make_symbol(code)
    real_time = str(time.time()).replace('.', '')[0:-1]  # 获取当前时间
    comment_url = 'https://xueqiu.com/statuses/search.json?' \
                  'count=10&comment=0&symbol={symbol}&hl=0&' \
                  'source=user&sort=time&page={page}&_={real_time}'
    url = comment_url.format(symbol=symbol, page=1, real_time=real_time)
    res = sess.get(url, headers=headers, timeout=10).json()
    count = res['count']  # 评论总条数
    total_page = res['maxPage']  # 页数
    print("总页数：", total_page)
    # 评论数据存储list
    comments = {
        "symbol": symbol,
        "count": count,
    }
    coms = []
    for i in range(1, total_page + 1):
        print(i)
        time.sleep(sleep)
        headers = get_header()
        sess_temp = requests.Session()

        # 访问首页，获取cookies
        sess_temp.get(XUEQIU_HOME, headers=headers, timeout=10)
        real_time = str(time.time()).replace('.', '')[0:-1]  # 获取当前时间

        url = comment_url.format(symbol=symbol, page=i, real_time=real_time)
        try:
            res = sess_temp.get(url, headers=headers, timeout=10).json()['list']
        except Exception:
            print(i, "fail")
            traceback.print_exc()
            continue
        for r in res:
            com = {
                "text": BeautifulSoup(r['text'], 'lxml').text,
                "id": r['id'],
                "time": r['timeBefore'],
                "reply_count": int(r['reply_count']),
                "source": r['source']
            }

            user = {
                "id": r['user']['id'],
                "city": r['user']['city'],
                "description": r['user']['description'],
                "followers_count": r['user']['followers_count'],
                "friends_count": r['user']['friends_count'],
                "gender": r['user']['gender'],
                "nick_name": r['user']['screen_name'],
                "province": r['user']['province'],
                "status_count": r['user']['status_count'],
            }

            com['user'] = user

            if com['reply_count'] > 0:
                com['sub_comments'] = _get_sub_comments(com['id'])
            else:
                com['sub_comments'] = []

            coms.append(com)
    comments['comment_list'] = coms
    return comments


def _get_sub_comments(comment_id):
    """获取评论下面的子评论

    :param str comment_id: 评论id，如 `106580772`
    :return: list sub_comments
    """
    sub_com_url = "https://xueqiu.com/statuses/comments.json?id={comment_id}" \
                  "&count=20&page=1&reply=true&asc=false&type=status&split=true"
    url = sub_com_url.format(comment_id=comment_id)

    headers = get_header()
    sess = requests.Session()

    # 访问首页，获取cookies
    sess.get(XUEQIU_HOME, headers=headers, timeout=10)

    res = sess.get(url, headers=headers).json()['comments']
    sub_comments = []

    for r in res:
        com = {
            "timestamp": r['created_at'],
            "ip": r['created_ip'],
            "text": BeautifulSoup(r['text'], 'lxml').text,
            "source": r['source'],
        }

        user = {
            "id": r['user']['id'],
            "city": r['user']['city'],
            "description": r['user']['description'],
            "followers_count": r['user']['followers_count'],
            "friends_count": r['user']['friends_count'],
            "gender": r['user']['gender'],
            "nick_name": r['user']['screen_name'],
            "province": r['user']['province'],
            "status_count": r['user']['status_count'],
        }

        com["user"] = user

        sub_comments.append(com)
    return sub_comments


def get_top_portfolio(market='cn', profit="monthly_gain", count=30):
    """获取top实盘组合

    :param market:
    :param profit:
    :param count:
    :return:
    """
    base_url = "https://xueqiu.com/cubes/discover/rank/cube/list.json?" \
               "category=12&count={count}&market={market}&profit={profit}&sort=best_benefit"
    url = base_url.format(market=market, count=count, profit=profit)
    headers = get_header()
    sess = requests.session()
    sess.get(XUEQIU_HOME, headers=headers)
    res = sess.get(url, headers=headers).json()['list']

    top_pfs = []
    for r in res:
        pf = {
            "name": r['name'],
            "symbol": r['symbol'],
            "description": r['description'],
            "follower_count": r['follower_count'],
            "updated_at": r['updated_at'],
            "net_value": r['net_value'],
            "monthly_gain": str(r['monthly_gain']) + "%",
            "total_gain": str(r['annualized_gain_rate']) + "%",
            "last_rb_id": r['last_rb_id'],
        }

        user = {
            "id": r['owner']['id'],
            "city": r['owner']['city'],
            "description": r['owner']['description'],
            "followers_count": r['owner']['followers_count'],
            "friends_count": r['owner']['friends_count'],
            "gender": r['owner']['gender'],
            "nick_name": r['owner']['screen_name'],
            "province": r['owner']['province'],
            "status_count": r['owner']['status_count'],
        }

        pf['user'] = user

        top_pfs.append(pf)
    return top_pfs


# 股票筛选
# --------------------------------------------------------------------

class ShareScreen:
    def __init__(self):
        self.name = "雪球股票筛选器"
        self.screened = OrderedDict()

    @staticmethod
    def _get_shares(raw, reason):
        res = get_raw_response(raw)
        shares = json.loads(res.text)
        shares['list'] = [i['symbol'][2:] for i in shares['list']]
        shares['reason'] = reason
        return shares

    def SS01(self):
        """选股器01 - 总市值低于30亿，每股收益大于0.2"""
        reason = "总市值低于30亿，每股收益大于0.2"
        raw = """
        GET /stock/screener/screen.json?category=SH&exchange=&areacode=&indcode=&orderby=symbol&order=desc&current=ALL&pct=ALL&page=1&mc=0_30&eps.20180331=0.2_6.77&_=1532157090470 HTTP/1.1
        Host: xueqiu.com
        Connection: keep-alive
        Accept: application/json, text/javascript, */*; q=0.01
        cache-control: no-cache
        DNT: 1
        X-Requested-With: XMLHttpRequest
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36
        Referer: https://xueqiu.com/hq/screener
        Accept-Encoding: gzip, deflate, br
        Accept-Language: en-US,en;q=0.9
        Cookie: device_id=93f4ed2cb55c692c95f053da19015b52; s=fq11y14kj3; bid=e0902c871217c79df259eb5d83f46eae_j950845q; _ga=GA1.2.1448042712.1508812875; __utmz=1.1527436687.45.17.utmcsr=sogou.com|utmccn=(referral)|utmcmd=referral|utmcct=/link; __utma=1.1448042712.1508812875.1528039186.1529730232.49; remember=1; remember.sig=K4F3faYzmVuqC0iXIERCQf55g2Y; xq_a_token=6ff26751fa685eb1ceab508fcb1c6b0556ef650a; xq_a_token.sig=wSoXzThiLbzH4mXexFY2U11fUzM; xq_r_token=5a288141cd3742deacc30e09eda6d0de65501ced; xq_r_token.sig=Hp0vJJ_CRQXm_3ATbMMnyspaIBA; xq_is_login=1; xq_is_login.sig=J3LxgPVPUzbBg3Kee_PquUfih7Q; u=3987902339; u.sig=wHo1L73HiVC2HlUxrHqBNa63rVo; aliyungf_tc=AQAAAO0MKVFvPwIAyD88OjvS/B9ge3BR; Hm_lvt_1db88642e346389874251b5a1eded6e3=1531897634,1531985157,1532156465,1532157061; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1532157061
        """
        shares = self._get_shares(raw=raw, reason=reason)
        self.screened['SS01'] = shares
        return shares
