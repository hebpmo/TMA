# -*- coding: UTF-8 -*-

"""
collector.xueqiu - 采集雪球数据

官网：https://xueqiu.com/
====================================================================
"""

import requests
import time
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
    count = res['count']            # 评论总条数
    total_page = res['maxPage']     # 页数
    print("总页数：", total_page)
    # 评论数据存储list
    comments = {
        "symbol": symbol,
        "count": count,
    }
    coms = []
    for i in range(1, total_page+1):
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
            "monthly_gain": str(r['monthly_gain'])+"%",
            "total_gain": str(r['annualized_gain_rate'])+"%",
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



