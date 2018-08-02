# -*- coding: UTF-8 -*-

"""
Tushare数据接口封装
====================================================================
"""

import os
import time
from datetime import datetime

import pandas as pd
import tushare as ts

from tma import DATA_PATH

# --------------------------------------------------------------------

def get_market_basic(cache=True, use_cache=False):
    """返回A股所有股票的基础信息"""
    FILE_BASIC = os.path.join(DATA_PATH, "market_basic.csv")

    if os.path.exists(FILE_BASIC):
        now_t = time.time()
        modify_t = os.path.getmtime(FILE_BASIC)
        if use_cache and now_t - modify_t < 3600*12:
            basic_df = pd.read_csv(FILE_BASIC, dtype={"code": str})
            return basic_df
    
    basic_df = ts.get_stock_basics()
    basic_df.reset_index(inplace=True)
    basic_df['code'] = basic_df['code'].astype(str)
    if cache:
        basic_df.to_csv(FILE_BASIC, encoding='utf-8', index=False)
    return basic_df

def get_all_codes():
    """返回A股所有股票的代码"""
    basic_df = get_market_basic(cache=True, use_cache=True)
    return list(basic_df['code'])

# --------------------------------------------------------------------

def index_all():
    """指数行情接口"""
    return ts.get_index()


def get_price(code):
    """获取一只股票的最新价格

    :param code: str
        股票代码，如：600122
    :return: float
    """
    data = ts.get_realtime_quotes(code)
    return float(data.loc[0, 'price'])


def get_ticks(code, source="spider", date=None, cons=None):
    """返回date日期的分笔数据

    :param source:
    :param code: str: 股票代码，如 603655
    :param date: str: 日期，如 2018-03-15
    :param cons: tushare的api连接
    :return:
    """
    if not date:
        date = datetime.now().date().__str__()
    TODAY = datetime.now().date().__str__()

    # 统一 ticks 的输出结果
    def _unify_out(ticks, date):
        ticks = ticks[['time', 'price', 'volume', 'type']]
        ticks['datetime'] = ticks['time'].apply(lambda x: datetime.strptime(date + " " + x, "%Y-%m-%d %H:%M:%S"))
        ticks['vol'] = ticks['volume']
        type_convert = {
            "买盘": 0,
            "卖盘": 1,
            "中性盘": 2,
            "0": 2
        }
        ticks['type'] = ticks["type"].apply(lambda x: type_convert[str(x)])
        ticks.drop(['time', 'volume'], axis=1, inplace=True)
        ticks.sort_values('datetime', inplace=True)
        ticks.reset_index(drop=True, inplace=True)
        return ticks[['datetime', 'price', 'vol', 'type']]

    if source == "spider" and date == TODAY:
        ticks = ts.get_today_ticks(code=code)
        ticks = _unify_out(ticks, date=TODAY)
    elif source == "spider" and date != TODAY:
        ticks = ts.get_tick_data(code=code, date=date)
        ticks = _unify_out(ticks, date=date)
    else:
        if not cons:
            cons = ts.get_apis()
        ticks = ts.tick(code=code, conn=cons, date=date)
    return ticks


ticks = get_ticks


def get_bars(codes):
    """获取codes的实时quotes"""
    return ts.get_realtime_quotes(codes)


bars = get_bars

# K线
# --------------------------------------------------------------------

def get_klines(code, freq="D", start_date=None):
    """获取K线数据

    :param code: str 股票代码
    :param start_date: str 默认为 None
        开始日期。值为None时，默认获取全部。
    :param freq: str 默认为 "D"
        K线周期，可选值 D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟
    :return: pd.DataFrame
    """
    if start_date is None:
        data = ts.get_k_data(code=code, ktype=freq)
    else:
        data = ts.get_k_data(code=code, start=start_date, ktype=freq)
    return data


klines = get_klines

# 全市场行情
# --------------------------------------------------------------------

def filter_tp(tm):
    """停盘股过滤

    :param tm: return of function today_market
    :return:
    """
    tm1 = tm[tm['volume'] != 0.0]
    tm1.reset_index(drop=True, inplace=True)
    return tm1


def filter_st(tm):
    """ST股过滤

    :param tm: return of function today_market
    :return:
    """
    fst = tm['name'].apply(lambda x: True if "ST" not in x else False)
    tm1 = tm[fst]
    tm1.reset_index(drop=True, inplace=True)
    return tm1


def get_today_market(filters=None, save=True,
                     use_latest=False, interval=600):
    """返回最近一个交易日所有股票的交易数据

    :param filters: list 默认为 ['tp']
        需要应用的过滤规则，可选 "tp"、"st"。tp表示过滤停盘股，st表示过滤st股。
    :param save: bool 默认为 True
        是否缓存到user目录下
    :param use_latest: bool 默认为 False
        是否使用最近缓存的数据
    :param interval: int 默认 600
        更新行情的最小间隔（单位：s），即：如果DATA_PATH路径下的latest_market的修改时间
        与当前时间的间隔小于interval设定的数值，且use_latest为True，
        将使用latest_market.csv中的行情
    :return: pd.DataFrame
        最新的市场行情
    """
    if filters is None:
        filters = ['tp']
    tm_csv = os.path.join(DATA_PATH, 'latest_market.csv')
    if use_latest and os.path.exists(tm_csv) \
            and time.time() - os.path.getmtime(tm_csv) < interval:
        tm = pd.read_csv(tm_csv, encoding='utf-8')
        return tm

    tm = ts.get_today_all()
    if filters is None:
        return tm
    filters = [x.lower() for x in filters]
    if "tp" in filters:
        tm = filter_tp(tm)
    if "st" in filters:
        tm = filter_st(tm)
    if save:
        tm.to_csv(tm_csv, index=False, encoding='utf-8')
    return tm


today_market = get_today_market


def get_hist_market(date):
    """历史行情数据

    :param date: str:
        指定日期，如 "2018-03-19"
    :return:
    """
    hm = ts.get_day_all(date)
    hm['date'] = date
    return hm


hist_market = get_hist_market

# 融资融券
# --------------------------------------------------------------------
# tushare接口： sh_margins | sh_margin_details 
#              sz_margins | sz_margin_details


