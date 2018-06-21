# -*- coding: UTF-8 -*-

"""
indicator.meta - 指标信息（元标签）
====================================================================
"""

from collections import OrderedDict

# A股 Market 指标体系 - 日
# 编码规则：M + 三位数字（001~999）
# --------------------------------------------------------------------

MARKET_INDICATOR_META = OrderedDict()

MARKET_INDICATOR_META['INFO'] = OrderedDict({
    "create_date": '2018-06-20',
    "creator": "zengbin",
    "explain": "A股全市场单个交易日的指标体系 - 用于刻画市场状态，感知趋势变化",
    "update": [
        # 更新记录：日期 - 更改人 - 变动内容
    ],
})

MARKET_INDICATOR_META['M001'] = OrderedDict({
    'explain': "全市场赚钱效应",
    "cal_method": "全市场上涨个股数量 / 开盘个股总数"
})

MARKET_INDICATOR_META['M002'] = OrderedDict({
    'explain': "开盘个股数量",
})

MARKET_INDICATOR_META['M003'] = OrderedDict({
    'explain': "上涨个股数量"
})

MARKET_INDICATOR_META['M004'] = OrderedDict({
    'explain': "涨3个点以上个股数量"
})

MARKET_INDICATOR_META['M005'] = OrderedDict({
    "explain": "跌3个点以上个股数量"
})

MARKET_INDICATOR_META['M006'] = OrderedDict({
    "explain": "换手率前五十只股票的赚钱效应",
    "cal_method": "换手率前五十只股票中上涨个股数量 / 50",
})

MARKET_INDICATOR_META['M007'] = OrderedDict({
    "explain": "换手率前五十只股票中涨3个点以上的数量"
})

MARKET_INDICATOR_META['M008'] = OrderedDict({
    "explain": "换手率前五十只股票中跌3个点以上的数量"
})

MARKET_INDICATOR_META['M009'] = OrderedDict({
    "explain": "涨停板个股数量",
    "cal_method": "（涨幅 > 0.095）的个股总数",
})

MARKET_INDICATOR_META['M010'] = OrderedDict({
    "explain": "一字涨停板个股数量",
    "cal_method": "（涨幅 > 0.095）且（最高价 == 最低价）的个股总数",
})

MARKET_INDICATOR_META['M011'] = OrderedDict({
    "explain": "盘中触及涨停板个股数量",
    "cal_method": "（最高价涨幅 > 0.095）且（现价 < 最高价）的个股总数",
})

MARKET_INDICATOR_META['M012'] = OrderedDict({
    "explain": "涨停封板成功率",
    "cal_method": "涨停板个股数量 / （涨停板个股数量 + 盘中触及涨停板个股数量）",
})

MARKET_INDICATOR_META['M013'] = OrderedDict({
    "explain": "跌停板个股数量",
    "cal_method": "（跌幅 > 0.095）的个股总数",
})

MARKET_INDICATOR_META['M014'] = OrderedDict({
    "explain": "一字跌停板个股数量",
    "cal_method": "（跌幅 > 0.095）且（最高价 == 最低价）的个股总数",
})

MARKET_INDICATOR_META['M015'] = OrderedDict({
    "explain": "盘中触及跌停板个股数量",
    "cal_method": "（最低价跌幅 > 0.095）且（现价 > 最低价）的个股总数",
})

MARKET_INDICATOR_META['M016'] = OrderedDict({
    "explain": "跌停封板成功率",
    "cal_method": "跌停板个股数量 / （跌停板个股数量 + 盘中触及跌停板个股数量）",
})


# 查询 Indicator 元信息
# --------------------------------------------------------------------

def check_indicator_meta(indicator=None):
    """查询 indicator 的元信息"""
    if indicator.startswith("M"):
        return MARKET_INDICATOR_META.get(indicator, None)



