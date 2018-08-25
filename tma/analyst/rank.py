# -*- coding: UTF-8 -*-

"""
analyst.rank - 一些排序模型
====================================================================
"""
import re
import jieba.analyse
import string

from tma.collector.aggregation import agg_market_klines


class BaseRank:
    """基类"""

    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

    def rank(self, top=None):
        raise NotImplementedError

    @property
    def top30(self):
        return self.rank(top=30)

    @property
    def top50(self):
        return self.rank(top=50)

    @property
    def top100(self):
        return self.rank(top=100)


class WeekRank(BaseRank):
    """
    排序准则：周涨幅 * 0.5 + 周振幅 * 0.5
    """

    def __init__(self, date, refresh=False):
        """周排序

        :param date: str
            每周最后一个交易日的日期，如："2018-08-03"
        :param refresh: bool 默认值 False
            是否刷新数据
        """
        desc = "以涨幅和振幅为依据的周排序方法"
        super().__init__(name='week_top', desc=desc)
        # 参数
        self.date = date
        self.refresh = refresh
        # 数据及计算结果
        self.latest_mkls = None

    def data_prepare(self):
        """获取排序需要的数据，按照排序准则进行计算"""
        mkls = agg_market_klines(k_freq='W',
                                 refresh=self.refresh)
        latest_mkls = mkls[mkls["date"] == self.date]
        latest_mkls["change"] = latest_mkls["close"] - latest_mkls['open']
        latest_mkls["change_rate"] = latest_mkls["change"] / latest_mkls["open"]
        latest_mkls["wave"] = latest_mkls["high"] - latest_mkls['low']
        latest_mkls["wave_rate"] = latest_mkls["wave"] / latest_mkls["low"]
        latest_mkls['criterion'] = 0.5 * latest_mkls["change_rate"] + \
                                   0.5 * latest_mkls["wave_rate"]
        latest_mkls.drop(['open', 'close', 'high', 'low',
                          'volume', 'change', 'wave', ], axis=1, inplace=True)
        latest_mkls.sort_values('criterion', ascending=False, inplace=True)
        self.latest_mkls = latest_mkls.reset_index(drop=True)

    def rank(self, top=None):
        """默认的排序，即 周涨幅 * 0.5 + 周振幅 * 0.5"""
        if not self.latest_mkls:
            self.data_prepare()
        if top is None:
            top_shares = list(self.latest_mkls['code'])
        else:
            indexes = range(top)
            top_shares = list(self.latest_mkls.loc[indexes, 'code'])
        return list(enumerate(top_shares, 1))

    def rank_by_change_rate(self):
        """以周涨跌幅为依据的排序"""
        if not self.latest_mkls:
            self.data_prepare()
        wr = self.latest_mkls
        wr.sort_values('change_rate', ascending=False, inplace=True)
        wr = wr.reset_index(drop=True)
        return wr


class TfidfDocRank(BaseRank):
    """基于TFIDF的文档重要性排序

    :param documents: list
        中文文档内容列表，如：
        ['美俄安全对话：会谈5小时，未发布联合声明',
         '内塔尼亚胡仍盼美国承认戈兰高地归以色列',
         '缩量盘整中资金调仓换股 金融股5日吸金近60亿元']
    :param N: int, 默认值 10
        从每篇文档中取出的重要关键词的数量

    ========================================================
    核心思想：
        文档由词构成，前N个关键词的平均重要性高的文档重要性也高。

    算法过程
    ========================================================
    输入:
        1）文档列表，2）N
    计算:
        step 1. 对每一个文档进行分词，计算每个词的tfidf值；
        step 2. 计算每篇文档的词均tfidf值，公式如下：
            文档词均tfidf值 = 所有词的tfidf值之和 / 文档总词数
        step 3. 按照“文档词均tfidf值”，从大到小排序
    输出:
        文档排序结果
    ========================================================
    """

    def __init__(self, documents, N=10):
        desc = "基于TFIDF的文档重要性排序"
        super().__init__(name='tfidf_doc_rank', desc=desc)
        self.documents = documents
        self.N = N

    def data_prepare(self):
        docs = self.documents
        # 清理数字、字母
        docs = [re.sub("[\d+\u3000a-zA-Z]", "", x) for x in docs]

        # 清理中英文标点
        ch_punc = "！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀" \
                  "｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟" \
                  "〰〾〿–—‘’‛“”„‟…‧﹏."
        punc = ch_punc + string.punctuation
        docs = [re.sub("[%s]" % punc, "", x) for x in docs]
        return docs

    @staticmethod
    def mean_tfidf(doc, top_k=None):
        """计算doc的词均tfidf值"""
        kw = jieba.analyse.extract_tags(doc, topK=None, withWeight=True)
        if len(kw) >= top_k:
            kw = kw[:top_k]
        else:
            for i in range(top_k - len(kw)):
                kw.append(kw[-1])
        total = sum([x[1] for x in kw])
        return total / len(kw)

    def rank(self, top=None, reverse=True):
        docs = self.data_prepare()
        results = [(self.mean_tfidf(doc, top_k=self.N), self.documents[i])
                   for i, doc in enumerate(docs)]
        results = sorted(results, key=lambda x: x[0], reverse=reverse)
        if not top:
            return results
        else:
            return results[:top]
