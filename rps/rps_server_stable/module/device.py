#!/usr/bin/env python
# _*_ coding: utf-8 _*_

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-06-2016
# Description   : RPS服务测试模拟设备端程序

'''
提供设备端所使用的函数
这些函数的内部还需要很多修改
'''

import json
import httplib
from log_api import error_log


def dev_set_config(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[SET CONFIG] Connected agentdevice failed: %s ' % e)
        return 1, 'Connected agentdevice failed: %s ' % e

    try:
        conn.request('POST', '/setconfig', body, header)
    except Exception, e:
        error_log('[SET CONFIG] access agentdevice request failed %s ' % e)
        return 1, 'access agentdevice request failed %s ' % e

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[SET CONFIG] device get response failed with error: %s ' % e)
        return 1, 'device get response failed with error: %s ' % e

    if resp.status == 200:
        conn.close()
        return 0, ''
    else:
        status = resp.status
        error_log('[SET CONFIG] device setconfig getresponse status: %s' % resp.status)
        conn.close()
        return 1, 'device setconfig getresponse status: %s' % status


def dev_del_config(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[DEL CONFIG] Connected agentdevice failed: %s' % e)
        return 1, 'Connected agentdevice failed: %s' % e

    try:
        conn.request('POST', '/delconfig', body, header)
    except Exception, e:
        error_log('[DEL CONFIG] access agentdevice request failed: %s ' % e)
        return 1, 'access agentdevice request failed: %s ' % e

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[DEL CONFIG] device get response failed with error: %s' % e)
        return 1, 'device get response failed with error: %s' % e

    if resp.status == 200:
        conn.close()
        return 0, ''
    else:
        error_log('[DEL CONFIG] device delconfig getresponse status: %s' % resp.status)
        conn.close()
        return 1, 'device delconfig getresponse status: %s' % resp.status


def dev_status(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[LOCAL STATUS] Connected agentdevice failed: %s' % e)
        return 1, 'Connected agentdevice failed: %s' % e

    try:
        conn.request('POST', '/status', body, header)
    except Exception, e:
        error_log('[LOCAL STATUS] access agentdevice request failed: %s' % e)
        return 1, 'access agentdevice request failed: %s' % e

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[LOCAL STATUS] device get response failed with error: %s' % e)
        return 1, 'device get response failed with error: %s' % e

    if resp.status == 200:
        resp_body = json.loads(resp.read())
        conn.close()
        if resp_body['ErrorNum'] == u'0':
          #  print 'device status : %s'% resp_body['ErrorString']
            return 0, '', True
        else:
            # 此时表示设备代理不正常，表示不在线， 不是设备有问题
            #error_log('[LOCAL STATUS] device status : %s %s' % (resp_body['ErrorNum'], resp_body['ErrorString']))
            return 0, '', False
    else:
        error_log('[LOCAL STATUS] device status getresponse status: %s' % resp.status)
        conn.close()
        return 1, 'device status getresponse status: %s' % resp.status
