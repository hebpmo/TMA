# -*- coding: UTF-8 -*-
import os
import pandas as pd


class BillAnalysis(object):
    """A股账户交易账单分析"""
    pass


"""
国泰君安 - 对账单 - 分析
===============================================================================
"""

# path = r"C:\ZB\Life\金融\对账单\国泰君安_对账单_20160329_20180522.csv"
path = r"C:\ZB\tgja_20160329_20180522.csv"


def read_data(path):
    data = pd.read_csv(path)
    data.columns = [x.strip("\t=") for x in data.columns]

    for col in data.columns:
        try:
            data[col] = data[col].apply(lambda x: x.strip("\t="))
        except:
            continue
    return data


data = read_data(path)


def cal_gain(data, cur_cap=0):
    """计算账户整体盈亏
    账户整体盈亏 = 入金 + 当前市值 - 出金
    """
    res = data.groupby(by='交易类型').sum()['发生金额']
    return -res['证券转银行'] - res['银行转证券'] + cur_cap


def cal_share_gain(data):
    """计算所有个股盈亏
    个股盈亏 = 卖出 + 当前市值 - 买入
    """
    data = data[data['证券名称'] != ""]
    res = data.groupby(['证券名称', '交易类型']).sum()['成交金额']
    shares = res.index.levels[0]
    share_gains = []
    for share in shares:
        try:
            print(share, " - 总盈亏：")
            stg = res[share]['证券卖出'] - res[share]['证券买入']
            print(stg, '\n')
            share_gains.append((share, stg))
        except:
            print("\nerro: ", res[share])
    return share_gains


def get_share_detail(share):
    """获取个股的交易记录详情"""
    col_need = ['交收日期', '证券名称', '交易类型', '成交价格', '成交数量', '成交金额']
    detail = data[data['证券名称'] == share][col_need]
    return detail


"""
平安证券 - 对账单 - 分析
===============================================================================
"""


# path = r"C:\Users\Mike\Desktop\pazq_records"

def read_data(path):
    files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".xls")]

    res = pd.DataFrame()

    for file in files:
        data = pd.read_csv(file, encoding='gbk', sep='\t')
        res = res.append(data, ignore_index=True)

    res.columns = [x.strip('"=') for x in res.columns]
    for col in res.columns:
        res[col] = res[col].astype(str)
        res[col] = res[col].apply(lambda x: x.strip('"='))
    res.sort_values("发生日期", ascending=False, inplace=True)
    res.reset_index(drop=True, inplace=True)
    res.drop(['备注', 'Unnamed: 21'], axis=1, inplace=True)
    float_col = ['发生金额', '成交均价', '成交数量', '成交金额', '股份余额',
                 '手续费', '印花税', '资金余额', '委托价格', '委托数量', '过户费']
    for col in float_col:
        res[col] = res[col].astype(float)
    return res


def cal_gain(data):
    """根据交易数据，计算总盈亏"""
    res = dict(data.groupby('业务名称').sum()['发生金额'])
    total_gain = -res['银证转出'] - res['银证转入']
    return round(total_gain, 4)


def cal_share_gain(data):
    """计算个股操作盈亏"""
    data = data[data['证券代码'] != "nan"]
    res = data.groupby(['证券名称', '业务名称']).sum()['成交金额']
    shares = res.index.levels[0]
    share_gains = []
    for share in shares:
        try:
            print(share, " - 总盈亏：")
            stg = res[share]['证券卖出清算'] - res[share]['证券买入清算']
            print(stg, '\n')
            share_gains.append((share, stg))
        except:
            print("\nerro: ", res[share])
    return share_gains
