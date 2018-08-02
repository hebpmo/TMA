# -*- coding: utf-8 -*-
"""
sms - 预警消息推送模块
====================================================================
"""

from retrying import retry
import requests
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from tma import SCKEY


@retry(stop_max_attempt_number=6)
def server_chan_push(title, content, sckey=None):
    """使用server酱推送消息到微信，关于server酱，
    请参考：http://sc.ftqq.com/3.version

    :param title: str
        消息标题
    :param content: str
        消息内容，最长64Kb，可空，支持MarkDown
    :param sckey: str
        从[Server酱](https://sc.ftqq.com/3.version)获取的key
    :return: None
    """
    if not sckey and not SCKEY:
        raise ValueError("请配置SCKEY，如果还没有SCKEY，"
                         "可以到这里申请一个：http://sc.ftqq.com/3.version")

    # 优先使用系统内部配置的SCKEY
    sckey = SCKEY if SCKEY else sckey
    url = 'https://sc.ftqq.com/%s.send' % sckey
    requests.post(url, data={'text': title, 'desp': content})


@retry(stop_max_attempt_number=6)
def bear_push(title, content, send_key=None):
    """使用PushBear推送消息给所有订阅者微信，关于PushBear，
    请参考：https://pushbear.ftqq.com/admin/#/

    :param title: str
        消息标题
    :param content: str
        消息内容，最长64Kb，可空，支持MarkDown
    :param send_key: str
        从[PushBear](https://pushbear.ftqq.com/admin/#/)获取的通道send_key
    :return: None
    """
    if not send_key:
        raise ValueError("请配置通道send_key，如果还没有，"
                         "可以到这里创建通道获取：https://pushbear.ftqq.com/admin/#/")
    api = "https://pushbear.ftqq.com/sub"
    requests.post(api, data={'text': title, 'desp': content, "sendkey": send_key})


class EmailSender:
    """
    example
    ----------------
    subject = '附件发送测试'
    content = '检测附件发送是否成功'
    files = ['test.py',
             'f:\\已下载.txt']

    e = EmailSender('zeng_bin8888@163.com', pw=pw, service='163')
    e.send_email(to, subject, content, files)
    """

    def __init__(self, from_, pw, service='163'):
        self.from_ = from_  # 用于发送email的邮箱
        self.pw = pw  # 发送email的邮箱密码

        # 登录邮箱
        self.smtp = smtplib.SMTP()
        smtps = {
            "qq": 'smtp.exmail.qq.com',
            "163": 'smtp.163.com'
        }
        assert service in smtps.keys(), "目前仅支持：%s" % str(smtps.keys()).strip("dict_keys()")
        smtp = smtps[service]
        self.smtp.connect(smtp)
        self.smtp.login(self.from_, self.pw)

    def construct_msg(self, to, subject, content, files=None):
        """构造email信息

        parameters
        ---------------
        subject     邮件主题
        content     邮件文本内容
        files       附件（list）,可以是相对路径下的文件，也可以是绝对路径下的文件

        return
        --------------
        msg         构造好的邮件信息
        """
        msg = MIMEMultipart()
        msg['from'] = self.from_
        msg['to'] = to
        msg['subject'] = subject
        txt = MIMEText(content)
        msg.attach(txt)

        # 添加附件
        if files is not None:
            for file in files:
                f = MIMEApplication(open(file, 'rb').read())
                f.add_header('Content-Disposition', 'attachment',
                             filename=os.path.split(file)[-1])
                msg.attach(f)

        return msg

    @retry(stop_max_attempt_number=6)
    def send_email(self, to, subject, content, files=None):
        """登录邮箱，发送msg到指定联系人"""
        smtp = self.smtp
        msg = EmailSender.construct_msg(self, to, subject, content, files=files)
        smtp.sendmail(self.from_, to, str(msg))

    def quit(self):
        smtp = self.smtp
        smtp.quit()  # 退出登录


def send_email(from_, pw, to, subject, content, files=None, service='163'):
    """邮件发送（支持附件），推荐使用163邮箱"""
    se = EmailSender(from_=from_, pw=pw, service=service)
    se.send_email(to=to, subject=subject, content=content, files=files)
    se.quit()
