# -*- coding: UTF-8 -*-

"""
collector.aggregation - 聚合数据采集
聚合数据采集是指一次性采集模型分析所需要的数据
====================================================================
"""
import os
import traceback
from tqdm import tqdm
import pandas as pd

import tma
# tma.DEBUG = True
from tma.utils import debug_print
from tma.collector.ts import get_klines
from tma.collector.ts import get_all_codes


def agg_market_klines(k_freq="D", refresh=True, cache=True):
    """获取整个市场全部股票的K线

    :param k_freq: str 默认值 D
        K线周期，可选值参考 `tma.collector.ts.get_klines`
    :param refresh: bool 默认值 True
        是否刷新数据。
        全市场所有股票K线的获取需要较长的时间，默认情况下，获取的数据会
        缓存到用户目录下的`.tma/data`文件夹。当 refresh 为 False 且
        存在对应k_freq的K线数据时，直接读取缓存数据。
    :param cache: bool 默认值 True
        是否缓存数据到用户目录下。
    :return: :class: `pd.DataFrame`
        字段列表:
        ['date', 'open', 'close', 'high', 'low', 'volume', 'code']
    """
    FILE_CACHE = os.path.join(tma.DATA_PATH,
                              "market_klines_%s.csv" % k_freq)
    if os.path.exists(FILE_CACHE) and not refresh:
        df = pd.read_csv(FILE_CACHE, encoding='utf-8', dtype={"code": str})
        return df

    shares = get_all_codes()
    shares_kls = []
    failed = []
    for share in tqdm(shares):
        try:
            kls = get_klines(share, freq=k_freq)
            shares_kls.append(kls)
        except:
            if tma.DEBUG:
                traceback.print_exc()
            failed.append(share)
    if tma.DEBUG:
        msg = "agg_market_klines(k_freq='%s') 运行结果：总共有%i只股票，" \
              "其中未获取到k线的股票数量是%i" % (
                  k_freq, len(shares), len(failed)
              )
        debug_print(msg, level='INFO')
    df = pd.concat(shares_kls, ignore_index=True)
    if cache:
        # 缓存数据
        df.to_csv(FILE_CACHE, index=False, encoding='utf-8')
    return df
