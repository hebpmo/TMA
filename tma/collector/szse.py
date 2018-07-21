# -*- coding: UTF-8 -*-

"""
collector.szse - 采集深圳证券交易所的数据

官网：http://www.sse.com.cn/
====================================================================
"""

import pandas as pd


#
# --------------------------------------------------------------------

def get_index_shares(code):
    """获取深圳证券交易所制定的相关指数的样本股列表

    :param code: str
        指数代码，如：399678 - 深次新股
    :return: pd.DataFrame

    说明：
    “计算标志”为0时，表示该样本的成交量、成交金额纳入指数的成交量、成交金额，
    但不纳入指数点位的计算；
    “计算标志”为1时，表示该样本的成交量、成交金额纳入指数的成交量、成交金额，
    同时也纳入指数点位的计算。
    """
    excel_url = "http://www.szse.cn/api/report/ShowReport?" \
                "SHOWTYPE=xlsx&CATALOGID=1747_zs&TABKEY=" \
                "tab1&ZSDM={code}".format(code=code)
    shares = pd.read_excel(excel_url, dtype={"证券代码": str})
    return shares
