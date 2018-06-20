# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import tma


setup(
    name=tma.__name__,
    version=tma.__version__,
    keywords=(
        "A股", "xueqiu", "雪球", "TuShare", "交易数据分析"
    ),
    description="Tools for Market A - A股工具集",
    long_description="",
    license="MIT License",
    url="https://github.com/zengbin93/TMA",
    author=tma.__author__,
    author_email="zeng_bin8888@163.com",
    packages=find_packages(exclude=['test', 'doc', 'img']),
    include_package_data=True,
    install_requires=[
        "tushare", "pandas", "requests", "zb"
    ],
    python_requires=">=3",
    entry_points={}
)


