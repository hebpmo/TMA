# coding: utf-8

"""
Account - 虚拟账户，用于仿真交易

仿真交易分为两种模式：
1）strict - 严格模式，只能在正常交易时间段进行虚拟交易，参照真实交易规则；
2）loose - 宽松模式，不进行任何限制，允许任意添加交易记录
====================================================================
"""

import os
from datetime import datetime
import json

from tma import ACCOUNT_PATH
from tma.collector import get_price

class Account:
    def __init__(self, name, fund=-1, mode="strict"):
        self.name = name
        self.mode = mode
        self.fund = fund
        self.path = os.path.join(ACCOUNT_PATH, "%s_trade.json" % self.name)
        self._read_info()

    def _read_info(self):
        if os.path.exists(self.path):
            self.info = json.load(open(self.path, 'r'))
        else:
            self.info = {
                "name": self.name,
                "path": self.path,
                "fund": self.fund,  # 把fund设置为-1表示不限制资金大小
                "trades": {},
                "create_date": datetime.now().date().__str__(),
            }

    def _save_info(self):
        json.dump(self.info, open(self.path, 'w'))

    def buy(self, code, amount, price=None):
        if not price:
            price = get_price(code)
        record = {
            "code": code,
            "amount": amount,
            "price": price,
            "date": datetime.now().date().__str__(),
            "kind": "BUY"
        }
        if code not in self.info['trades'].keys():
            self.info['trades'][code] = []
        self.info['trades'][code].append(record)
        self._save_info()

    def sell(self):
        pass





