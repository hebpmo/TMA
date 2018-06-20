# -*- coding: UTF-8 -*-

"""
collector - 数据采集模块
1）tushare数据接口封装；
2）雪球数据采集
3）同花顺数据采集
====================================================================
"""


# tushare数据接口封装
from .ts import (klines, bars, ticks, today_market, get_price)

# 上海证券交易所官网采集数据接口
from .sse import get_sh_indexes


