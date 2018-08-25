# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import tma


setup(
    name=tma.__name__,
    version=tma.__version__,
    keywords=(
        "A股", "xueqiu", "雪球", "TuShare", "交易数据分析", "三级股票池", "仿真交易",
        "A股数据采集"
    ),
    description="Tools for Market A - A股工具集",
    long_description="专为中国A股设计开发的工具集，着重点是交易数据获取和分析。我是一只菜鸟，对A股"
                     "的认识非常肤浅，如果你愿意用积攒的经验为我开发这套工具提供一些帮助，"
                     "请联系 zeng_bin8888@163.com ，不胜感激！",
    license="MIT License",
    url="https://github.com/zengbin93/TMA",
    author=tma.__author__,
    author_email="zeng_bin8888@163.com",
    packages=find_packages(exclude=['test', 'doc', 'img']),
    include_package_data=True,
    install_requires=[
        "tushare", "pandas", "requests", "zb", "retrying", "numpy",
        "bs4", "jieba"
    ],
    python_requires=">=3",
    entry_points={}
)


