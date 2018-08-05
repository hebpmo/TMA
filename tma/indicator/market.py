# -*- coding: UTF-8 -*-

"""
indicator.market - A股市场指标计算
====================================================================
"""

import pandas as pd
from collections import OrderedDict

from tma.collector import today_market
from tma.indicator.meta import check_indicator_meta


class MarketDayIndicator(object):
    """A股全市场单个交易日的指标体系"""
    def __init__(self):
        self.features = OrderedDict()
        self.m = None

    # 数据获取
    # --------------------------------------------------
    def _get_market(self, use_exists=True):
        if not use_exists:
            self.m = today_market(filters=['tp'], use_latest=False)
        if self.m is None:
            m = self.m = today_market(filters=['tp'], use_latest=True)
        else:
            m = self.m
        return m

    # 指标计算
    # --------------------------------------------------
    @staticmethod
    def _up_rate(m):
        """计算赚钱效应相关指标"""
        total = len(m)
        m['is_up'] = m['changepercent'].apply(lambda x: True if x > 0.0 else False)
        m['is_up_3'] = m['changepercent'].apply(lambda x: True if x > 3.0 else False)
        m['is_down_3'] = m['changepercent'].apply(lambda x: True if x < -3.0 else False)
        up3 = dict(m['is_up_3'].value_counts())[True]
        up = dict(m['is_up'].value_counts())[True]
        down3 = dict(m['is_down_3'].value_counts())[True]
        return total, up, up3, down3

    def cal_total_market(self):
        """计算全市场赚钱效应相关指标"""
        m = self._get_market()
        total, up, up3, down3 = self._up_rate(m)
        f = OrderedDict(
            {
                "M001": up / total,
                "M002": total,
                "M003": up,
                "M004": up3,
                "M005": down3,
            }
        )
        self.features.update(f)

    def cal_turnover_top50(self):
        """计算换手率前50只股票的赚钱效应相关指标"""
        m = self._get_market()
        m.sort_values('turnoverratio', inplace=True)
        m.reset_index(drop=True, inplace=True)
        m_tt50 = m.tail(50)
        total, up, up3, down3 = self._up_rate(m_tt50)
        f = OrderedDict(
            {
                "M006": up / total,
                "M007": up3,
                "M008": down3,
            }
        )
        self.features.update(f)

    def cal_limit_arrived(self):
        """计算涨跌停板相关指标"""
        m = self._get_market()
        m = m[[
            'code', 'name', 'changepercent', 'trade',
            'open', 'high', 'low', 'settlement', 'volume'
        ]]
        la = []
        for i in m.index:
            data = m.loc[i]
            if data['volume'] == 0.0:
                continue

            # 涨停板观察
            if data['high'] > data['settlement'] * 1.095:
                if data['high'] > data['trade']:  # 盘中触及涨停板
                    x = dict(data)
                    x['kind'] = "盘中触及涨停板"
                    la.append(x)
                elif data['high'] == data['low']:  # 一字涨停板
                    x = dict(data)
                    x['kind'] = "一字涨停板"
                    la.append(x)
                elif data['high'] == data['trade']:  # 涨停板
                    x = dict(data)
                    x['kind'] = "涨停板"
                    la.append(x)
                else:
                    continue

            # 跌停板观察
            if data['low'] < data['settlement'] * 0.905:
                if data['trade'] > data['low']:  # 盘中触及跌停板
                    x = dict(data)
                    x['kind'] = "盘中触及跌停板"
                    la.append(x)
                elif data['high'] == data['low']:  # 一字跌停板
                    x = dict(data)
                    x['kind'] = "一字跌停板"
                    la.append(x)
                elif data['low'] == data['trade']:  # 跌停板
                    x = dict(data)
                    x['kind'] = "跌停板"
                    la.append(x)
                else:
                    continue

        df_la = pd.DataFrame(la)
        df_la = df_la[['code', 'name', 'trade', 'open', 'high', 'low',
                        'kind', 'changepercent']]
        df_la = df_la.sort_values('kind')

        la_count = OrderedDict(df_la['kind'].value_counts())
        x1 = la_count.get("涨停板", 0) + la_count.get("一字涨停板", 0)
        x2 = la_count.get("一字涨停板", 0)
        x3 = la_count.get("盘中触及涨停板", 0)
        x4 = la_count.get("跌停板", 0) + la_count.get("一字跌停板", 0)
        x5 = la_count.get("一字跌停板", 0)
        x6 = la_count.get("盘中触及跌停板", 0)

        f = OrderedDict(
            {
                "M009": x1,
                "M010": x2,
                "M011": x3,
                "M013": x4,
                "M014": x5,
                "M015": x6
            }
        )
        f['M012'] = x1 / (x1 + x3) if x1 + x3 != 0 else 0
        f['M016'] = x4 / (x4 + x6) if x4 + x6 != 0 else 0

        self.features.update(f)

    # 其他
    # --------------------------------------------------
    @property
    def indicators(self):
        indicators = OrderedDict()
        for k, v in self.features.items():
            indicators[k] = {
                "value": round(v, 4),
                "explain": check_indicator_meta(k)['explain']
            }
        return indicators

    def update(self):
        self._get_market(use_exists=False)
        self.run()

    def run(self):
        self._get_market()
        self.cal_total_market()
        self.cal_turnover_top50()
        self.cal_limit_arrived()



