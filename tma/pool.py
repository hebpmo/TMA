"""
StockPool - 股票池对象
====================================================================
"""
import os
import traceback
from datetime import datetime
from collections import OrderedDict
import json
import pandas as pd

from tma import POOL_PATH
from tma.collector import bars


class StockPool:
    """三级股票池对象"""
    def __init__(self, name, pool_path=None):
        self.name = name
        if pool_path is None:
            self.pool_path = POOL_PATH
        else:
            self.pool_path = pool_path

        # 三级股票池缓存文件
        self.path = os.path.join(self.pool_path, '%s_pool.json' % self.name)
        self.path_hist = self.path.replace(".json", "_hist.pool")

        # 如果pool_path路径下已经有名称为name的股票池，恢复；否则，新建
        if os.path.exists(self.path):
            self.restore()
        else:
            self.shares = OrderedDict(level1=[], level2=[], level3=[])

        self.shares_hist = None

    # 三级股票池的保存与恢复
    # --------------------------------------------------------------------
    def save(self):
        """把股票池中的股票保存到文件"""
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.shares, f, indent=2, ensure_ascii=False)

    def save_hist(self, shares):
        """删除股票池中股票的同时，保存一份到对应的hist文件"""
        shares = [str(dict(share)) + "\n" for share in shares]
        with open(self.path_hist, 'a', encoding='utf-8') as f:
            f.writelines(shares)

    def restore(self):
        """从文件中恢复股票池"""
        with open(self.path, 'r', encoding='utf-8') as f:
            self.shares = OrderedDict(json.load(f))

    def restore_hist(self):
        """从文件中恢复选股历史"""
        with open(self.path_hist, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.shares_hist = [eval(x) for x in lines]

    # 添加股票
    # --------------------------------------------------------------------
    def add(self, code, reason, level, dt=None, save=True):
        """添加单只股票到股票池

        Note: 每只股票可以多个入选理由，因此存在多条记录。

        :param code: str
            股票代码
        :param reason: str
            选股逻辑
        :param level: int
            加入股票池的等级，可选值 [1, 2, 3]
        :param dt: str 默认值 datetime.now()
            加入股票池的时间
        :param save: bool 默认值 True
            是否实时保存到json文件
        :return: None
        """
        if dt is None:
            dt = datetime.now().__str__().split(".")[0]
        share = dict()
        share['code'] = code
        share['dt'] = dt
        share['level'] = level
        share['reason'] = reason
        self.shares["level" + str(level)].append(share)
        if save:
            self.save()

    def add_many(self, codes, reason, level, dt=None):
        """添加多只股票到股票池

        Note: 每只股票可以多个入选理由，因此存在多条记录。

        :param codes: str or list
            股票代码
        :param reason: str
            选股逻辑
        :param level: int
            加入股票池的等级，可选值 [1, 2, 3]
        :param dt: str 默认值 datetime.now()
            加入股票池的时间
        :return: None
        """
        if dt is None:
            dt = datetime.now().__str__().split(".")[0]
        if isinstance(codes, str):
            codes = [codes]
        for code in codes:
            share = dict()
            share['code'] = code
            share['dt'] = dt
            share['level'] = level
            share['reason'] = reason
            self.shares["level" + str(level)].append(share)
        self.save()

    # 查看股票
    # --------------------------------------------------------------------
    def check(self, code, level):
        """查看股票

        :param code: 股票代码
        :type code: str
        :param level: 股票池等级
        :type level: int
        :return: 股票池中对应code、level的所有数据
        :rtype: list
        """
        shares_l = self.shares['level'+str(level)] 
        shares = [x for x in shares_l if x['code'] == code]
        return shares

    # 删除股票
    # --------------------------------------------------------------------
    def remove(self, code, level):
        """删除指定等级的股票

        :param code: str
            股票代码
        :param level: int
            对应的股票等级，可选值 [1, 2, 3]
        :return: None
        """
        shares_l = self.shares['level' + str(level)]
        removed = [share for share in shares_l if share['code'] == code]
        self.save_hist(removed)
        shares_l = [share for share in shares_l if share['code'] != code]
        self.shares['level' + str(level)] = shares_l
        self.save()

    def empty(self, clear=True):
        """清空三级股票池

        Note: 默认会同时将股票池对应的json文件清空，谨慎操作！

        :param clear: bool 默认值 True
            是否同时清空对应的json文件
        :return: None
        """
        shares = self.shares['level1']
        shares.extend(self.shares['level2'])
        shares.extend(self.shares['level3'])
        self.save_hist(shares)

        self.shares = OrderedDict(level1=[], level2=[], level3=[])
        if clear:
            self.save()

    # 检查各级股票池的表现
    # --------------------------------------------------------------------
    def check_performance(self, level=3):
        """查看各级股票池的表现
        
        :param level: 股票池等级, defaults to 3
        :param level: int, optional

        """
        shares_l = self.shares['level'+str(level)]
        codes_l = list(set([x['code'] for x in shares_l]))
        batch_num = int(len(codes_l)/800) + 1

        res = []
        for i in range(batch_num):
            codes = codes_l[i*800: (i+1)*800]
            res.append(bars(codes))
        codes_bar = pd.concat(res, ignore_index=True)

        # 计算赚钱效应
        codes_bar['price'] = codes_bar['price'].astype(float)
        codes_bar['pre_close'] = codes_bar['pre_close'].astype(float)
        codes_bar['change'] = codes_bar['price'] - codes_bar['pre_close']
        up_nums = len(codes_bar[codes_bar['change']>0])
        down_nums = len(codes_bar[codes_bar['change']<=0])
        total_nums = len(codes_bar)

        return {
            "up_nums": up_nums,
            "down_nums": down_nums,
            "total_nums": total_nums,
            "up_rate": round(up_nums/total_nums, 4)
        }
    





