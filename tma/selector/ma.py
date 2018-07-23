# -*- coding: UTF-8 -*-
"""

selector.ma - 均线选股
====================================================================
"""

import os
from tqdm import tqdm
import pandas as pd
import time

from tma.indicator import ShareDayIndicator
from tma.collector.ts import get_all_codes
from tma import DATA_PATH


class MaShareScreen(object):
    """基于均线系统的股票筛选器"""

    def __init__(self):
        self.name = "均线系统股票筛选器"
        self.codes = get_all_codes()
        self.shares_ma = []
        self.screened = []
    
    def cal_shares_indicators_ma(self, use_cache=True, interval=3600*12):
        FILE_ALL_SHARES_INDICATORS_MA = os.path.join(DATA_PATH, "all_shares_indicators_ma.csv")
        
        # 读取缓存：文件存在，且最后一次修改时间距离现在不超过interval
        if os.path.exists(FILE_ALL_SHARES_INDICATORS_MA):
            now_t = time.time()
            modify_t = os.path.getmtime(FILE_ALL_SHARES_INDICATORS_MA)
            if use_cache and now_t - modify_t < interval:
                sdis_df = pd.read_csv(FILE_ALL_SHARES_INDICATORS_MA, dtype={"CODE": str})
                return sdis_df
        
        # 重新计算
        sdis = []
        failed = []
        for code in tqdm(self.codes):
            try:
                sdi = ShareDayIndicator(code)
                sdi.run(['ma'])
                sdis.append(sdi.indicators)
            except:
                failed.append(code)
                continue
        print("%i 个股票的指标计算失败，分别是：%s" % (len(failed), str(failed)))
        sdis_df = pd.DataFrame(sdis)
        sdis_df.to_csv(FILE_ALL_SHARES_INDICATORS_MA, index=False, encoding='utf-8')
        return sdis_df

    def get_shares_ma(self):
        sdis_df = self.cal_shares_indicators_ma()
        sdis_df = sdis_df[[
            'DATE', 'CODE', 'NAME', 'PRICE', 'MA5_D', 
            'MA10_D', 'MA20_D', 'MA30_D', 'MA60_D', 
            'MA120_D', 'MA240_D'
        ]]
        self.shares_ma = [dict(row[1]) for row in sdis_df.iterrows()]

    def SS01(self):
        """Share Screen 01 - 1号选股，当前价格向下偏离MA5_D超过10个点"""
        reason = "当前价格向下偏离MA5_D超过10个点"
        screened = []
        for share in self.shares_ma:
            if share['PRICE'] < 0.9 * share['MA5_D']:
                share['reason'] = reason
                screened.append(share)
        self.screened.extend(screened)

    def SS02(self):
        """Share Screen 02 - 2号选股，MA5_D与MA10_D相互靠近（差的绝对值小于0.1%）"""
        reason = "MA5_D与MA10_D相互靠近（差的绝对值小于0.1%）"
        screened = []
        for share in self.shares_ma:
            abs_gap = share['PRICE'] * 0.001
            if abs(share['MA5_D'] - share['MA10_D']) <= abs_gap:
                share['reason'] = reason
                screened.append(share)
        self.screened.extend(screened)
    
    def SS03(self):
        """Share Screen 03 - 3号选股，日K线完全空头排列（MA120_D > MA60_D > MA30_D > MA20_D > MA10_D > MA5_D）"""
        reason = "日K线完全空头排列（MA120_D > MA60_D > MA30_D > MA20_D > MA10_D > MA5_D）"
        screened = []
        for share in self.shares_ma:
            condition = share['MA120_D'] > share['MA60_D'] > share['MA30_D'] \
                        > share['MA20_D'] > share['MA10_D'] > share['MA5_D']
            if condition:
                share['reason'] = reason
                screened.append(share)
        self.screened.extend(screened)
        
class zb_list(list):
    def print_i(self, i):
        print(self.__getitem__(i))

    

    

