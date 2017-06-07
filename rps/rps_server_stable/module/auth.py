#!/usr/bin/env python
# encoding: utf-8

import socket
import json
import httplib
from log_api import *

def multi_new_auth_code(host, port, header, body):
    try:
        conn = httplib.HTTPConnection(host, port)
    except socket.error, e:
        error_log('[AUTH SERVER] Connected auth server failed: %s' % e)
        return 1, '[AUTH SERVER] Connected auth server failed: %s' % e

    try:
        conn.request('POST', '/', body, header)
    except socket.error, e:
        error_log('[AUTH SERVER] access auth request failed: %s' % e)
        return 1, '[AUTH SERVER] access auth request failed: %s' % e

    try:
        resp = conn.getresponse()
    except socket.error, e:
        error_log('[AUTH SERVER] auth get response failed with error: %s' % e)
        return  1, 'auth get response failed with error: %s' % e

    if resp.status == 200:
        resp_body = json.loads(resp.read())
        if resp_body['AuthProtocol']['Header']['ErrorNum'] == u'200':
            #print "MSG_MULTIAUTH_CODE_NEW_RSP: %s" % resp_body['AuthProtocol']['Header']['ErrorString']
            return 0, '', resp_body['AuthProtocol']['Body']['ReadAuthCode']
        else:
            error_log('[AUTH SERVER] %s' % resp_body['AuthProtocol']['Header']['ErrorString'])
            return 1, resp_body['AuthProtocol']['Header']['ErrorString']
    else:
        error_log('[AUTH SERVER] getresponse status: %s' % resp.status)
        return 1, 'getresponse status: %s' % resp.status
