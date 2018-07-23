# -*- coding: UTF-8 -*-
"""

selector.ma - 市净率选股
====================================================================
"""


from tma.collector import today_market

def screen_by_pb(pb_range=[0, 0.8]):
    """根据pb范围筛选股票
    
    :param pb_range: 市净率范围, defaults to [0, 0.8]
    :param pb_range: list, optional
    :return: 给定市净率范围的股票列表
    :rtype: list
    """

    tm = today_market(filters=['tp', 'st'])
    tm = tm[['code', 'name', 'pb']]
    codes = []
    for row in tm.iterrows():
        share = dict(row[1])
        if pb_range[1] > share['pb'] > pb_range[0]:
            codes.append(share)
    return codes
        

