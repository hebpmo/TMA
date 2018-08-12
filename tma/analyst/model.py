# -*- coding: UTF-8 -*-

"""
analyst.model - 一些实用模型
====================================================================
"""
from datetime import datetime
from collections import OrderedDict

from tma.collector import get_price
from tma.indicator import ShareDayIndicator


# 爬楼梯模型
# --------------------------------------------------------------------
class ClimbStairs:
    """爬楼梯模型实现"""

    def __init__(self, code, stair_prices=None):
        """

        :param code: str
            A股股票代码，如：600682
        :param stair_prices: list
            阶梯价格列表，如：[
                {'name': "MA5", "value": 8.88}, # name为阶梯名称，value为阶梯值
                ...
            ]
        """
        self.author = "zengbin"
        self.contact = "zeng_bin8888@163.com"
        self.version = "V0"

        self.code = code
        self.cur_price = get_price(self.code)

        # 设定阶梯价格列表，并排序（按价格从小到大）
        self.stair_prices = stair_prices
        if stair_prices is None:
            self.set_default_stair_prices()
        self.stair_prices = sorted(self.stair_prices, key=lambda x: x['value'])
        self.price_seq = [x['value'] for x in self.stair_prices]
        self.stair_nums = len(self.stair_prices)

        # 计算楼梯最低点的价格、最高点的价格、楼梯高度
        self.stair_low = min(self.price_seq)
        self.stair_high = max(self.price_seq)
        self.stair_height = max(self.price_seq) - min(self.price_seq)

        # 当前价格在阶梯中的位置
        self.pos = None

        # 当前价格上下各有多少个阶梯
        self.above_stairs = None
        self.above_nums = None
        self.below_stairs = None
        self.below_nums = None

    def set_default_stair_prices(self):
        sdi = ShareDayIndicator(self.code)
        sdi.run(target=['ma', 'lnd'])
        stair_prices = []
        choose_k = ['MA5_D', 'MA10_D', 'MA20_D', 'MA30_D', 'MA60_D',
                    'MA120_D', 'MA240_D', 'HIGH_5', 'LOW_5', 'HIGH_10',
                    'LOW_10', 'HIGH_20', 'LOW_20', 'HIGH_40', 'LOW_40',
                    'HIGH_60', 'LOW_60']
        for k, v in sdi.indicators.items():
            if k in choose_k:
                stair_prices.append({'name': k, "value": v})
        self.stair_prices = stair_prices

    def cur_price_pos(self):
        """获得当前价格在阶梯中的位置"""
        cur_price = self.cur_price
        price_gap = cur_price - min(self.price_seq)
        pos = price_gap / self.stair_height
        self.pos = pos
        return pos

    def cal_stair_nums(self):
        """计算当前价格上下各有几个阶梯"""
        self.above_stairs = [stair for stair in self.stair_prices
                             if self.cur_price <= stair['value']]
        self.below_stairs = [stair for stair in self.stair_prices
                             if self.cur_price > stair['value']]
        self.above_nums = len(self.above_stairs)
        self.below_nums = len(self.below_stairs)
        return {
            "above": self.above_nums,
            "below": self.below_nums,
            "total": self.stair_nums
        }

    @property
    def stair(self):
        s = OrderedDict()
        s['date'] = datetime.now().date().__str__()
        s['code'] = self.code
        s['prices'] = self.stair_prices
        s['nums'] = self.stair_nums
        s['height'] = self.stair_height
        return s

# 相似性计算，如 K线相似性等
# --------------------------------------------------------------------
