# 项目开发：TMA - Tools for Market A - A股工具集

## 一些基础概念定义

1. A股三大主体：1）全市场、2）指数、3）个股


## 新手教程

### 1 - 监控（涨停/跌停）板（买一/卖一）挂单金额

```python
import tma
from tma.monitor import sm_limit

# 设置SCKEY - 调用Server酱推送消息到微信
tma.SCKEY = "XXXXXXXXXX"

sm_limit('600122', kind="zt", threshold=10000, interval=1)

```

### 2 - A股交易日历

A股交易日历引用自Tushare，另外自己实现了几个函数，使用案例如下：

* 查看完整的交易日历
```python
from tma import trade_calendar

print(trade_calendar)
```

* 获取某一个交易日前后N个交易日的日期
``` python
from tma import get_recent_trade_days

after_10 = get_recent_trade_days("2018-07-03", 10)
before_10 = get_recent_trade_days("2018-07-03", -10)
```

* 判断某一天是不是交易日
``` python
from tma import is_trade_day

day = "2018-07-03"
if is_trade_day(day):
    print("%s 是交易日" % day)
```

* 判断当前是否是交易时间
``` python
from tma import is_in_trade_time

if is_in_trade_time():
    print("当前是交易时间")
```



## 功能规划
作为A股的工具集，本身可以开发的功能非常多。但是个人能力有限，只能把可以开发的功能先列出来，慢慢搞。
目前已经规划的功能有：
1. 三级股票池
2. 虚拟仿真账户
3. 个股指标体系 - 日
4. 个股指标体系 - 周
5. 全市场指标体系 - 日
6. 选股方法 - 大幅偏离MA5

### 三级股票池



### 虚拟仿真账户



## 开发笔记

### 2018-06-30

* 添加功能 - 监控涨停板买一挂单金额、跌停板卖一挂单金额

### 2018-07-01

* 添加功能 - 微信通知

### 2018-07-02

* 添加全局日志记录器
* 添加debug模式

### 2018-07-03

* 添加功能 - A股交易日历

### 2018-07-04

* 添加 - rules模块（A股交易纪律）


