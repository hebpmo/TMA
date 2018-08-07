# -*- coding: utf-8 -*-
"""
sms - 预警消息推送模块
====================================================================
"""

from zb.tools import sms

server_chan_push = sms.server_chan_push
bear_push = sms.bear_push
EmailSender = sms.EmailSender


def send_email(from_, pw, to, subject, content, files=None, service='163'):
    """邮件发送（支持附件），推荐使用163邮箱"""
    se = EmailSender(from_=from_, pw=pw, service=service)
    se.send_email(to=to, subject=subject, content=content, files=files)
    se.quit()
