# -*- coding: UTF-8 -*-

import time
import traceback

from tma.indicator import ShareDayIndicator
from tma.utils import is_in_trade_time
from tma import sms
from tma import SCKEY
from tma.utils import debug_print

# "SCU10748T12f471f07094648d297222fc649e374d598bf38bc81fd"


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

            debug_info = "%s - %s - %s 万元" % (str(code), msg1, str(int(money/10000)))
            debug_print(debug_info)

            if money / 10000 < threshold:
                title = "%s - %s 即将破板" % (msg0, str(code))
                content = "%s: %s万元，低于阈值（%s万元）" % (msg1,
                            str(int(money/10000)), str(threshold))
                if SCKEY:
                    sms.server_chan_push(title, content, sckey=SCKEY)
                    break
                else:
                    raise ValueError("请配置SCKEY，如果还没有SCKEY，"
                                     "可以到这里申请一个：http://sc.ftqq.com/3.version")
        except Exception as e:
            traceback.print_exc()
            debug_print(str(e))
            continue

    end_info = "结束监控 - %s - %s | 参数配置：阈值（%i 万元）" \
                 % (msg0, str(code), threshold)
    debug_print(end_info)
