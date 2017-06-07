#!/usr/bin/env python
# encoding: utf-8

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-08-2016
# Description   : RPS 测试客户端程序

'''
RPS测试客户端程序函数
利用进程池的方式, 来模拟出10个客户端

主函数 main() 包含初始化及其后所有内容

本函数中的所有函数返回值都只为某一功能 SUCCESSED/FAILED
'''

import pickle
from api import *
from echo import *

def run_client():
    # 启动echo_cli
    # 启动Client发送数据时需要传入local_port, 那么这一步必然是在list_bind之后
    file_ac_port_list = open('./temp/ac_port_list.pkl', 'rb')
    ac_port_list = pickle.load(file_ac_port_list)
    file_ac_port_list.close()

    file_dict_ac_port_uuid_local_port = open('./temp/dict_ac_port_uuid_local_port.pkl', 'rb')
    dict_ac_port_uuid_local_port = pickle.load(file_dict_ac_port_uuid_local_port)
    file_dict_ac_port_uuid_local_port.close()

    # TODO: 在完成listbind之后再来写
    run_echo_client(ac_port_list, dict_ac_port_uuid_local_port)
    write_report(' RPS 测试数据传输：  完成')

if __name__ == '__main__':
    run_client()
