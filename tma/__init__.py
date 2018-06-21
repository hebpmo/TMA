# -*- coding: UTF-8 -*-
import os

# 元信息
# --------------------------------------------------------------------
__name__ = 'tma'
__version__ = "0.0.2"
__author__ = "zengbin"


# 设置用户文件夹
# --------------------------------------------------------------------

def set_path(path=None):
    if not path:
        USER_HOME = os.path.expanduser('~')
        PATH = os.path.join(USER_HOME, ".tma")
    else:
        PATH = path
    DATA_PATH = os.path.join(PATH, "data")
    ACCOUNT_PATH = os.path.join(PATH, "account")
    POOL_PATH = os.path.join(PATH, "pool")
    for P in [PATH, DATA_PATH, ACCOUNT_PATH, POOL_PATH]:
        if not os.path.exists(P):
            os.mkdir(P)
    return PATH, DATA_PATH, ACCOUNT_PATH, POOL_PATH

PATH, DATA_PATH, ACCOUNT_PATH, POOL_PATH = set_path()


# API - 列表
# --------------------------------------------------------------------
from .pool import StockPool
from .account import Account


# module介绍
# --------------------------------------------------------------------

__doc__ = """
TMA - Tools for Market A - A股工具集
"""
