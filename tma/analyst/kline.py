# -*- coding: UTF-8 -*-

"""
analyst.kline - K线分析
====================================================================
"""


from tma.collector.ts import get_klines


kls = get_klines('600165', freq='D', start_date='2018-01-01')





