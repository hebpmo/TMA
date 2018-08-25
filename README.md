# TMA - Tools for Market A - A股工具集

> 专为中国A股设计开发的工具集，着重点是交易数据获取和分析。我是一只菜鸟，对A股
的认识非常肤浅，如果你愿意用积攒的经验为我开发这套工具
提供一些帮助，请联系`zeng_bin8888@163.com`，不胜感激！

## 快速入门


### 安装、卸载、更新
* 安装 - `pip install tma`
* 卸载 - `pip uninstall tma`
* 更新 - `pip install --upgrade tma`

### 基于TFIDF的文档排序模型

```python
from tma.collector import xhn
from tma.analyst import rank

# 采集新华网今日首页头条文章
hp = xhn.HomePage()
articles = hp.get_articles()
news = [x['title'] + '|' + x['source'] + "|" +
        x['content'] for x in articles]
news = [x.replace('\n', "") for x in news]

# 使用TFIDF排序模型
ranker = rank.TfidfDocRank(news, N=20)
# 查看前30条排序结果
print(ranker.top30)
# 查看前3条排序结果
ranker.rank(top=3)
```

### A股交易日历

A股交易日历引用自Tushare，另外自己实现了几个函数，使用方法如下：

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

* 另外封装了一个Calendar类
```python
from tma import Calendar

c = Calendar()

# 判断当前是不是交易时间
if c.is_trade_time():
    print("当前是交易时间")

# 判断某一天是不是交易日
d = "2018-07-13"
if c.is_trade_day(d):
    print("%s 是交易日" % d)

# 获取最近n个交易日
c.recent_trade_days(-3)
c.recent_trade_days(date='2018-09-10', n=3)
```

### 新华网首页头条获取

新华网`http://www.xinhuanet.com/`首页头条通常都是一些国内外大事。

```python
from tma.collector.xhn import HomePage

hp = HomePage()

# 获取头条文章列表 [url, title, pub_date]
a_list = hp.get_article_list()

# 获取头条文章中发布日期为今天的文章内容
articles = hp.get_articles()

# 获取头条文章中发布日期为recent_days的文章内容
recent_days = ['2018-07-15', '2018-07-14', '2018-07-13']
articles = hp.get_articles(recent_days)
```

### 获取上海证券交易所的上证系列指数行情
上证系列指数包含214个指数，共有为10个类别，分别是：定制指数、风格指数、成份指数、
主题指数、债券指数、策略指数、重点指数、基金指数、综合指数、行业指数。

关于上证系列指数的相关信息，请点击查看：
* [上证系列指数列表](http://www.sse.com.cn/market/sseindex/indexlist/)
* [上证系列指数计算与维护细则](http://www.sse.com.cn/market/sseindex/calculation/c/sse_indices_cal_and_main_cn.pdf)

上证系列指数行情获取方法如下：
```python
from tma.collector import get_sh_indexes

sh_indexes = get_sh_indexes()
```


## 版本更新记录
> 所有功能的添加都是针对A股，没有考虑其他市场。

### v 0.1.0

* pub_date: 2018-07-15
* 新增功能 - 三级股票池 - `tma.pool.StockPool`
* 新增功能 - 虚拟仿真交易账户 - `tma.account.Account`
* 新增功能 - tushare数据接口封装 - `tma.collector.ts`
* 新增功能 - 获取上海证券交易所所有指数的实时行情 - `tma.collector.sse.get_sh_indexes`
* 新增功能 - 新华网首页头条新闻采集 - `tma.collector.xhn.HomePage`
* 新增功能 - 雪球数据采集：个股评论、热门组合 - `tma.collector.xueqiu`
* 新增功能 - A股全市场单个交易日的指标体系 - `tma.indicator.market.MarketIndicator`
* 新增功能 - 以日为更新周期的个股指标体系 - `tma.indicator.market.ShareDayIndicator`
* 新增功能 - A股交易日历 - `tma.utils.Calendar`
* 新增功能 - 预警消息推送：server酱、邮件发送 - `tma.sms`
* 新增功能 - 监控单只股票 涨停板买一挂单金额 / 跌停板卖一挂单金额 - `tma.monitor.single.sm_limit`

