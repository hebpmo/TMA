# coding: utf-8

"""
StockPool - 股票池对象
====================================================================
"""
import os
import traceback
from zb.tools import file_tools as ft

from tma import POOL_PATH

def _verify_share(share):
    base = {
        "code": None,
        "name": None,
        "level": None,   # 1, 2, 3
        "date": None,    # 入选日期
        "reason": None,  # 入选理由
        "price": None    # 入选时的价格
    }
    try:
        assert share.keys() == base.keys(), \
            "share中应当包含这些key：%s" % str(base.keys())
        assert share['level'] in [1, 2, 3], \
            "level取值必须是[1, 2, 3]中的一个，当前值：%s" % str(share['level'])
        return True
    except:
        return False


class StockPool:
    def __init__(self, name):
        self.name = name

        # 股票池保存路径, 以.pool为后缀
        self.path = os.path.join(POOL_PATH, '%s.pool' % self.name)
        self.path_hist = self.path.replace(".pool", "_hist.pool")

        self.level1 = {}
        self.level2 = {}
        self.level3 = {}
        self._read_pool()


    def _read_pool(self):
        """读入股票池文件"""
        path = self.path
        if not os.path.exists(path):
            ft.create_file(path)
            ft.create_file(self.path_hist)
        else:
            self.level1 = {}
            self.level2 = {}
            self.level3 = {}
            shares = [eval(share.strip('\n')) for share in ft.read_file(path)]
            for share in shares:
                if share['level'] == '1':
                    if share['code'] not in self.level1.keys():
                        self.level1[share['code']] = []
                    self.level1[share['code']].append(share)

                elif share['level'] == '2':
                    if share['code'] not in self.level2.keys():
                        self.level2[share['code']] = []
                    self.level2[share['code']].append(share)

                elif share['level'] == '3':
                    if share['code'] not in self.level3.keys():
                        self.level3[share['code']] = []
                    self.level3[share['code']].append(share)

                else:
                    print("error: ", share)

    def add(self, share, read=True):
        """添加单只股票

        每只股票可以多个入选理由，因此存在多条记录。

        """
        try:
            _verify_share(share)
            ft.write_file(self.path, str(share), mode='a')
            if read:
                self._read_pool()
        except Exception:
            traceback.print_exc()

    def add_many(self, shares):
        """添加多只股票"""
        for share in shares:
            self.add(share, read=False)
        self._read_pool()

    def remove(self, code, level, save_to_hist=True):
        """指定股票代码，删除股票

        不管该股票有多少条记录，都会一次性全部删除

        """
        try:
            shares = [eval(share.strip('\n')) for share in ft.read_file(self.path)]
            shares_keep = []
            shares_hist = []
            for share in shares:
                if share['code'] == code and share['level'] == level:
                    shares_hist.append(share)
                else:
                    shares_keep.append(share)
            ft.write_file(self.path, shares_keep, mode='w')
            if save_to_hist:
                ft.write_file(self.path_hist, shares_keep, mode='a')
            self._read_pool()
        except Exception:
            traceback.print_exc()

    def delete(self, code, level):
        self.remove(code=code, level=level, save_to_hist=False)

    def empty(self):
        """清空股票池"""
        shares = ft.read_file(self.path)
        ft.write_file(self.path_hist, shares, mode='a')
        ft.create_file(self.path, mode='w')
        self._read_pool()
