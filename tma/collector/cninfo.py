# -*- coding: UTF-8 -*-

"""
collector.cninfo - 采集巨潮咨询网的数据

官网：http://www.sse.com.cn/
====================================================================
"""




import requests

url_sz = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse_latest'
url_sh = "http://www.cninfo.com.cn/cninfo-new/disclosure/sse_latest"
sh = requests.post(url_sh).json()
sz = requests.post(url_sz).json()

x = []
i = 0 
while 1:
    i +=1
    print(i)
    sh = requests.post(url_sh).json()
    x.extend(sh["classifiedAnnouncements"])
    if sh['hasMore']:
        continue
    else:
        break