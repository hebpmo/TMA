# -*- coding: UTF-8 -*-

"""
indicator.share - 个股指标计算
====================================================================
"""
import numpy as np
from datetime import datetime
import traceback
from collections import OrderedDict

from tma.collector import klines, ticks, get_price, bars


class ShareDayIndicator(object):
    """以日为更新周期的个股指标体系"""

    def __init__(self, code):
        self.code = code
        self.features = OrderedDict({
            "DATE": datetime.now().date().__str__(),
            "CODE": code,
            "PRICE": get_price(code)
        })
        self.kls = None
        self.tks = None
        self.bar = None
        self.update_time = {"kls": None,
                            'tks': None,
                            "bar": None,
                            "last_run": None}
        self.default_target = ('ma', 'lnd', 'bs', 'bsf')
        self.basic_info()

    # 相关数据获取
    # --------------------------------------------------------------------

    def _get_kls(self, use_exists=True):
        """获取日K线"""
        if not use_exists:
            self.kls = klines(self.code, freq='D')
        if self.kls is None:
            kls = self.kls = klines(self.code, freq='D')
        else:
            kls = self.kls
        self.update_time['kls'] = datetime.now().__str__()
        return kls

    def _get_today_ticks(self, use_exists=True):
        """获取当日分笔"""
        if not use_exists:
            self.tks = ticks(self.code)
        if self.tks is None:
            tks = self.tks = ticks(self.code)
        else:
            tks = self.tks
        self.update_time['tks'] = datetime.now().__str__()
        return tks

    def _get_realtime_bar(self):
        """获取实时行情"""
        bar = self.bar = bars(self.code)
        self.update_time['bar'] = datetime.now().__str__()
        return bar

    # --------------------------------------------------------------------

    def basic_info(self):
        bar = self._get_realtime_bar()
        self.bar = bar.iloc[0]
        open_price = float(bar.loc[0, 'open'])
        high_price = float(bar.loc[0, 'high'])
        low_price = float(bar.loc[0, 'low'])
        cur_price = float(bar.loc[0, 'price'])

        BASIC = OrderedDict()
        BASIC['NAME'] = bar.loc[0, 'name']
        BASIC['TOTAL_AMOUNT'] = float(bar.loc[0, 'amount'])
        BASIC['CHANGE_RATE'] = (cur_price - open_price) / open_price
        BASIC['WAVE_RATE'] = (high_price - low_price) / open_price

        self.features.update(BASIC)


    def cal_move_average(self, update=False):
        """计算移动均线指标"""
        if update or self.kls is None:
            kls = self.kls = self._get_kls()
        else:
            kls = self.kls
        seq_close = kls['close']
        MA = OrderedDict()
        MA.update({
            "MA5_D": np.mean(seq_close[-5:]),
            "MA10_D": np.mean(seq_close[-10:]),
            "MA20_D": np.mean(seq_close[-20:]),
            "MA30_D": np.mean(seq_close[-30:]),
            "MA60_D": np.mean(seq_close[-60:]),
            "MA120_D": np.mean(seq_close[-120:]),
            "MA240_D": np.mean(seq_close[-240:]),
        })
        for k, v in MA.items():
            MA[k] = round(v, 4)

        self.features.update(MA)

    def cal_latest_nd(self, d=None, update=False):
        """计算最近N个交易日的相关指标

        :param update:
        :param d: list, 默认 None
            指定N的大小，可以指定多个；如果为 None，则 d = [5, 10, 20, 40, 60]。
        :return:
        """
        if update or self.kls is None:
            kls = self.kls = self._get_kls()
        else:
            kls = self.kls
        if d is None:
            d = [5, 10, 20, 40, 60]
        kls['wave'] = kls['high'] - kls['low']
        kls['wave_rate'] = kls['wave'] / kls['open']
        LND = OrderedDict()
        for i in d:
            try:
                kls_d = kls[-i:]
                o = kls_d.iloc[0]['open']
                h = max(kls_d['high'])
                l = min(kls_d['low'])
                # 最高价
                LND["HIGH_" + str(i)] = h
                # 最低价
                LND["LOW_" + str(i)] = l
                # 涨跌幅
                LND["CHANGE_" + str(i)] = (kls_d.iloc[i-1]['close']-o) / o,
                # 最大回撤
                LND["MAX_DOWN_" + str(i)] = (kls_d.iloc[i-1]['close']-h) / h
                # 平均每日波动率
                LND["WAVE_RATE_A" + str(i)] = np.mean(kls_d['wave_rate'])
                # 累计波动率
                LND["WAVE_RATE_T" + str(i)] = (h - l) / o
            except Exception:
                traceback.print_exc()
        for k, v in LND.items():
            if isinstance(v, tuple):
                v = v[0]
            LND[k] = round(v, 4)

        self.features.update(LND)

    def cal_bs_dist(self, update=False):
        """计算今日分笔的买卖盘分布"""
        if update or self.tks is None:
            tks = self.tks = self._get_today_ticks()
        else:
            tks = self.tks
        tks['amount'] = tks['price'] * tks['vol'] * 100
        res = dict(tks.groupby('type').sum()['amount'])
        BS_DIST = OrderedDict()

        BS_DIST['BUY_AMOUNT'] = int(res.get(0, 0))
        BS_DIST['SELL_AMOUNT'] = int(res.get(1, 0))
        BS_DIST['NEUTRAL_AMOUNT'] = int(res.get(2, 0))

        self.features.update(BS_DIST)

    def cal_bs_first(self, update):
        """计算买一、卖一挂单金额"""
        if update or self.bar is None:
            bar = self._get_realtime_bar().iloc[0]
        else:
            bar = self.bar

        BS_FIRST = OrderedDict()

        # 卖一总挂单金额
        if not bar['b1_v']:
            BS_FIRST['BUY_FIRST'] = 0
        else:
            BS_FIRST['BUY_FIRST'] = float(bar['b1_v']) * float(bar['b1_p']) * 100

        # 买一总挂单金额
        if not bar['a1_v']:
            BS_FIRST['SELL_FIRST'] = 0
        else:
            BS_FIRST['SELL_FIRST'] = float(bar['a1_v']) * float(bar['a1_p']) * 100

        self.features.update(BS_FIRST)

    def update(self, target=None):
        """更新个股指标"""
        if not target:
            target = self.default_target
        self.run(target=target, update=True)

    def run(self, target=None, update=False):
        """计算所有个股相关指标的主函数，
        继承ShareIndicator对象，重写run方法可以自由选择计算哪些指标
        """
        if not target:
            target = self.default_target
        funcs = {
            "ma": self.cal_move_average,
            "lnd": self.cal_latest_nd,
            "bs": self.cal_bs_dist,
            "bsf": self.cal_bs_first
        }
        for x in target:
            if x in funcs.keys():
                funcs[x](update=update)
            else:
                raise ValueError('%s 不是合法的指标关键词' % x)
        # 记录最后一次运行的时间
        self.update_time['last_run'] = datetime.now().__str__()

    @property
    def indicators(self):
        indicators = OrderedDict()
        for k, v in self.features.items():
            if isinstance(v, float):
                indicators[k] = round(v, 4)
            else:
                indicators[k] = v
        return indicators



class ShareWeekIndicator(object):
    """以周为更新周期的个股指标体系"""
    def __init__(self):
        pass

