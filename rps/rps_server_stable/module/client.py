#!/usr/bin/env python
# _*_ coding: utf-8 _*_

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-06-2016
# Description   : RPS服务测试模拟客户端程序

'''
提供Client所使用的函数
'''


import json
import httplib
from log_api import error_log


def cli_create_bind(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[CREATE BIND] Connect to agentclient failed: %s' % e)
        return 1, 'Connect to agentclient failed: %s' % e
    try:
        conn.request('POST', '/createbind', body, header)
    except Exception, e:
        error_log('[CREATE BIND] access clientdevice request failed')
        return 1, 'access clientdevice request failed'

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[CREATE BIND] client get response failed with error: %s' % e)
        return 1, 'client get response failed with error: %s' % e

    if resp.status == 200:
        resp_body = resp.read()
        resp_body = json.loads(resp_body)
        conn.close()
        # INFO: 这里是一定要有返回值的(返回的是json)
        return 0, '', resp_body['local_port']
    else:
        status = resp.status
        error_log('[CREATE BIND] Client setconfig getresponse status: %s' % resp.status)
        conn.close()
        return 1, 'Client setconfig getresponse status: %s' % status


def cli_destroy_bind(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[DESTROY BIND] Connect to agentclient failed: %s' % e)
        return 1, 'Connect to agentclient failed: %s' % e

    try:
        conn.request('POST', '/destroybind', body, header)
    except Exception, e:
        error_log('[DESTROY BIND] access client request failed')
        return 1, 'access client request failed'

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[DESTROY BIND] Client get response failed with error: %s' % e)
        return 1, 'Client get response failed with error: %s' % e

    if resp.status == 200:
        #print 'client destroybind successed !'
        conn.close()
        return 0, ''
    else:
        status = resp.status
        conn.close()
        error_log('[DESTROY BIND] Client destorybind getresponse status: %s' % status)
        return 1, 'Client destorybind getresponse status: %s' % status


def cli_list_bind(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except Exception, e:
        error_log('[LIST BIND] Connect to agentclient failed: %s' % e)
        return 1, 'Connect to agentclient failed: %s' % e

    try:
        conn.request('POST', '/listbind', body, header)
    except Exception, e:
        error_log('[LIST BIND] access clientdevice request failed')
        return 1, 'access clientdevice request failed'

    try:
        resp = conn.getresponse()
    except Exception, e:
        error_log('[LIST BIND] client get response failed with error: %s' % e)
        return 1, 'client get response failed with error: %s' % e


    if resp.status == 200:
        #print 'Client listbind successed !'
        # logging.info('client listbind : {0} {1}'.format(resp.status, resp.reason))
        # logging.info('client listbind response : {0}'.format(resp.read()))
        resp_body = resp.read()
        conn.close()
        #error_log(resp_body)
        # INFO: 这里是一定要返回resp.read()的, 已经验证了
        return 0, '', resp_body
    elif resp.status == 404:
        conn.close()
        return 1, resp.status
    else:
        status = resp.status
        reason = resp.reason
        conn.close()
        error_log('[LIST BIND] Client (%s:%s) listbind getresponse status: %s, %s' % (host, port, status, reason))
        return 1, 'Client ( %s:%s )listbind getresponse status: %s, %s' % (host, port, status, reason)

