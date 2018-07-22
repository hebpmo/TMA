"""
StockPool - 股票池对象
====================================================================
"""
import os
import traceback
from datetime import datetime
from collections import OrderedDict
import json

from tma import POOL_PATH


class StockPool:
    def __init__(self, name, pool_path=None):
        self.name = name
        if pool_path is None:
            self.pool_path = POOL_PATH
        else:
            self.pool_path = pool_path

        # 三级股票池缓存文件
        self.path = os.path.join(self.pool_path, '%s_pool.json'
                                 % self.name)
        self.path_hist = self.path.replace(".json", "_hist.pool")

        self.shares = OrderedDict(
            level1=[],
            level2=[],
            level3=[]
        )

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
        with open(self.path_hist, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.shares_hist = [eval(x) for x in lines]

    # 添加股票
    # --------------------------------------------------------------------
    def add(self, code, reason, level, dt=None):
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
        shares_l = self.shares['level'+str(level)]
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

        self.shares = OrderedDict(
            level1=[],
            level2=[],
            level3=[]
        )
        if clear:
            self.save()

