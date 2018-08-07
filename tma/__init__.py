# -*- coding: UTF-8 -*-
import os

# 元信息
# --------------------------------------------------------------------
__name__ = 'tma'
__version__ = "0.1.1"
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

# 基本参数配置
# --------------------------------------------------------------------
DEBUG = False

# 全局日志记录器
from zb.utils import create_logger

log_file = os.path.join(PATH, "tma.log")
logger = create_logger(log_file, name='tma', cmd=True)

# API - 列表
# --------------------------------------------------------------------
from tma.pool import StockPool
from tma.account import Account
from tma.rules import RULES
from tma import selector
from tma import monitor
from tma import analyst
from tma import indicator
from tma.utils import Calendar
from tma.utils import (trade_calendar, is_in_trade_time,
                       is_trade_day, get_recent_trade_days)

# module介绍
# --------------------------------------------------------------------

__doc__ = """
TMA - Tools for Market A - A股工具集
"""
