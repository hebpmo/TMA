# -*- coding: UTF-8 -*-
"""

====================================================================
"""

from tma.indicator import MarketIndicator
from tma.utils import is_in_trade_time


def get_market_status():
    # 非交易时间，自动退出
    if not is_in_trade_time():
        return
    mi = MarketIndicator()
    mi.update()

    market_status_template = "### 实时市场状态\n --- \n" \
    "* 今日开盘个股总数为{M002}家，上涨个股数量为{M003}家，**赚钱效应{M001}**；" \
    "其中涨3个点以上个股数量是{M004}家，跌3个点以上个股数量是{M005}家。\n" \
    "* 换手率前50只个股赚钱效应{M006}，其中涨3个点以上个股数量是{M007}家，"  \
    "跌3个点以上个股数量是{M008}家。\n"  \
    "* 目前两市涨停{M009}家，其中一字板{M010}家；盘中触及涨停后打开家数为"  \
    "{M011}，封板成功率为{M012}；两市跌停{M013}家，其中一字板跌停{M014}" \
    "家，盘中触及跌停板{M015}家。\n\n"

    i = mi.indicators
    market_status = market_status_template.format(
        M002=i['M002']['value'], M003=i['M003']['value'],
        M001="%.2f" % (i['M001']['value']*100) + "%",
        M004=i['M004']['value'], M005=i['M005']['value'],
        M006="%.2f" % (i['M006']['value'] * 100) + "%",
        M007=i['M007']['value'], M008=i['M008']['value'],
        M009=i['M009']['value'], M010=i['M010']['value'],
        M011=i['M011']['value'],
        M012="%.2f" % (i['M012']['value'] * 100) + "%",
        M013=i['M013']['value'], M014=i['M014']['value'],
        M015=i['M015']['value'],
    )

    return market_status


