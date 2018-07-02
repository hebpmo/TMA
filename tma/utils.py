# -*- coding: UTF-8 -*-

import tushare as ts
from datetime import datetime



trade_calendar = ts.trade_cal()  # tushare提供的交易日历

def is_trade_day(date, trade_calendar=trade_calendar):
    """判断date日期是不是交易日

    :param date: str or datetime.date, 如 2018-03-15
    :param trade_calendar: 交易日历
    :return: Bool
    """

    trade_day = trade_calendar[trade_calendar["isOpen"] == 1]
    trade_day_list = list(trade_day['calendarDate'])
    if isinstance(date, datetime):
        date = str(date.date())
    if date in trade_day_list:
        return True
    else:
        return False

def is_in_trade_time():
    """判断当前是否是交易时间"""
    today = str(datetime.now().date())
    if not is_trade_day(today):  # 如果今天不是交易日，返回False
        return False
    t1 = today + " " + "09:30:00"
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    t2 = today + " " + "11:30:00"
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    t3 = today + " " + "13:00:00"
    t3 = datetime.strptime(t3, "%Y-%m-%d %H:%M:%S")
    t4 = today + " " + "15:00:00"
    t4 = datetime.strptime(t4, "%Y-%m-%d %H:%M:%S")
    if t1 <= datetime.now() <= t2 or t3 <= datetime.now() <= t4:
        return True
    else:
        return False

def get_recent_trade_days(date, n=10):
    """返回date(含)之前(或之后)的 n个交易日日期"""
    assert is_trade_day(date), "输入的date必须是交易日"
    tc = ts.trade_cal()
    tct = tc[tc['isOpen'] == 1]
    tct.reset_index(drop=True, inplace=True)
    tcts = list(tct['calendarDate'])
    date_i = tcts.index(date)
    if n > 0:
        rtd = tcts[date_i+1:date_i+n+1]
    else:
        rtd = tcts[date_i+n:date_i+1]
    return rtd


def debug_print(msg, level="INFO"):
    from tma import DEBUG, logger
    LOGS = {
        "INFO": logger.info,
        "DEBUG": logger.debug,
        "EXCEPTION": logger.exception
    }
    if DEBUG:
        LOGS[level](msg)
