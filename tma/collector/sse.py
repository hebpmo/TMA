# -*- coding: UTF-8 -*-

"""
collector.sse - 采集上海证券交易所的数据

官网：http://www.sse.com.cn/
====================================================================
"""

import requests
import pandas as pd

def get_sh_indexes():
    """获取上海证券交易所所有指数的实时行情"""
    url = "http://www.sse.com.cn/js/common/indexQuotes.js"
    res = requests.get(url).text
    lines = res.split("\n")
    lines = [x.replace('_t.push(', "").strip(");'") for x in lines if "_t.push(" in x]
    lines = [
        eval(line, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        for line in lines
    ]

    index_sh = pd.DataFrame(lines)
    index_sh = index_sh[['JC', 'ZSDM', 'abbr', 'ZRSP', 'DRKP', 'DRSP', 'DRZD', 'DRZX', 'ZDF']]
    index_sh = index_sh.rename(columns={
        'JC': 'name',
        'ZSDM': 'code',
        'abbr': 'kind',
        'ZRSP': 'preclose',
        'DRKP': 'open',
        'DRSP': 'close',
        'DRZD': 'high',
        'DRZX': 'low',
        'ZDF': 'change'
    })

    # index_sh.astype()
    return index_sh



