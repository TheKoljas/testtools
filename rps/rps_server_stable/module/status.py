#!/usr/bin/env python
# _*_ coding: utf-8 _*_

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-06-2016
# Description   : RPS服务测试模拟设备端设备

'''
提供与服务器所使用的函数
'''

import json
import httplib
from log_api import *


# 输入dev_list 将查询结果直接返回, 注意此函数正确情况下会有三个返回值
def query_cloud_status(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[STATUS SERVER] Connected status server failed: %s' % e)
        return 1, 'Connected status server failed: %s' % e

    try:
        conn.request('POST', '/', body, header)
    except Exception, e:
        error_log('[STATUS SERVER] Access status request failed: %s' % e)
        return 1, 'access status request failed: %s' % e

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[STATUS SERVER] Status get response failed with error: %s' % e)
        return  1, 'status get response failed with error: %s' % e

    if resp.status == 200:
        resp_body = json.loads(resp.read())
        if resp_body['StatusProtocol']['Header']['ErrorNum'] == u'200':
            #print "MSG_STATUS_MULTIQUERY_RSP: %s" % resp_body['StatusProtocol']['Header']['ErrorString']
            #print "    Multi Query Status: %s" % resp_body['StatusProtocol']['Body']
            body = resp_body['StatusProtocol']['Body']
            conn.close()
            return 0, '', body
        else:
            errorstring = resp_body['StatusProtocol']['Header']['ErrorString']
            error_log('[STATUS SERVER] %s' % errorstring)
            conn.close()
            return 1, errorstring
    else:
        status = resp.status
        error_log('[STATUS SERVER] getresponse status: %s' % status)
        conn.close()
        return 1, 'getresponse status: %s' % status
