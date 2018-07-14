# -*- coding: UTF-8 -*-

import time
import traceback
from datetime import datetime

from tma.indicator import ShareDayIndicator
from tma.utils import is_in_trade_time
from tma import sms
from tma.utils import debug_print
from tma import logger


# 涨跌停板破板
# --------------------------------------------------------------------

def sm_limit(code, kind, threshold=10000, interval=1):
    """监控单只股票 涨停板买一挂单金额 / 跌停板卖一挂单金额

    :param code: str
        股票代码
    :param kind: str
        涨停板（zt） / 跌停板（dt）
    :param threshold: int, 默认值 10000
        金额阈值，单位：万元； 对于涨停板/跌停板来说，
        如果买一/卖一挂单金额小于阈值，说明有破板的可能，
        及时发送预警通知。
    :param interval: int, 默认值 1
        监控间隔，单位：秒
    :return: None
    """
    if kind == "zt":
        msg0 = "【涨停板 - 破板监控】"
        msg1 = "买一总挂单金额"
    elif kind == "dt":
        msg0 = "【跌停板 - 破板监控】"
        msg1 = "卖一总挂单金额"
    else:
        raise ValueError("kind 可选值为 ['zt', 'dt']，"
                         "当前值为 '%s'" % kind)

    start_info = "开始监控 - %s - %s | 参数配置：阈值（%i 万元）" \
                 % (msg0, str(code), threshold)
    debug_print(start_info)

    while is_in_trade_time():
        time.sleep(interval)
        try:
            sdi = ShareDayIndicator(code)
            sdi.cal_bs_first()

            if kind == "zt":
                money = sdi.features['BUY_FIRST']
            elif kind == "dt":
                money = sdi.features['SELL_FIRST']

            debug_info = "%s - %s - %s 万元" % (str(code), msg1, str(int(money / 10000)))
            debug_print(debug_info)

            if money / 10000 < threshold:
                title = "%s - %s 即将破板" % (msg0, str(code))
                content = "%s: %s万元，低于阈值（%s万元）" % (msg1,
                                                   str(int(money / 10000)), str(threshold))
                sms.server_chan_push(title, content)
        except Exception as e:
            traceback.print_exc()
            debug_print(str(e))
            continue

    end_info = "结束监控 - %s - %s | 参数配置：阈值（%i 万元）" \
               % (msg0, str(code), threshold)
    debug_print(end_info)


# 市场状态 & 个股行情
# --------------------------------------------------------------------

def get_shares_status(codes):
    raise NotImplementedError


def get_market_status():
    raise NotImplementedError


def fix_inform(codes, interval=1800):
    """交易时间段内，每隔一段时间播报一次市场状态和个股行情

    :param codes: list or str
        个股代码
    :param interval: int
        固定间隔时间，单位：秒
    :return: None
    """
    if isinstance(codes, str):
        codes = [codes]

    start_info = "启动 - 固定间隔播报 | 参数配置：个股列表（%s）、时间间隔（%s）" \
                 % (str(codes), str(interval))
    logger.info(start_info)

    shares = [ShareDayIndicator(code) for code in codes]

    share_status_template = "### {code}（{name}）\n --- \n" \
                            " 当前价格为{price}元，" \
                            "涨跌幅{change_rate}，振幅{wave_rate}，" \
                            "总成交金额{total_amount}万元。\n"

    while is_in_trade_time():
        status = []
        # 构造播报信息 - 市场

        # 构造播报信息 - 个股
        for share in shares:
            share.update(target=['bsf'])
            si = share.indicators
            share_status = share_status_template.format(
                code=si['CODE'], name=si['NAME'], price=si['PRICE'],
                change_rate=str(round(si['CHANGE_RATE'] * 100, 4)) + "%",
                wave_rate=str(round(si['WAVE_RATE'] * 100, 4)) + "%",
                total_amount=str(int(si['TOTAL_AMOUNT'] / 10000))
            )
            status.append(share_status)

        title = "市场状态播报 - %s" % datetime.now().__str__().split('.')[0]
        content = ''.join(status)
        sms.server_chan_push(title, content)
        time.sleep(interval)

    end_info = "结束 - 固定间隔播报 | 参数配置：个股列表（%s）、时间间隔（%s）" \
               % (str(codes), str(interval))
    logger.info(end_info)
