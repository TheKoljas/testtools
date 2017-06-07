#!/usr/bin/env python
# encoding: utf-8

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-08-2016
# Description   : RPS 测试主程序

'''
RPS测试主程序函数
利用进程池的方式, 来模拟出10个客户端和100个设备端

主函数 main() 包含初始化及其后所有内容

本函数中的所有函数返回值都只为某一功能 SUCCESSED/FAILED
'''

import pickle
from api import *
from log_api import *


# 生成dev_list, 读取ad_port_list, 并将其一一对应生成 dict_uuid_ad_port
def run_device():
    # 获取设备端数目
    file_amount_dev = open('./temp/amount_dev.pkl', 'rb')
    amount_dev = pickle.load(file_amount_dev)
    file_amount_dev.close()

    dev_list = get_three_group_dev_list(amount_dev)

    file_dev_list = open('./temp/dev_list.pkl', 'wb')
    pickle.dump(dev_list, file_dev_list)
    file_dev_list.close()

    file_ad_port_list = open('./temp/ad_port_list.pkl', 'rb')
    ad_port_list = pickle.load(file_ad_port_list)
    file_ad_port_list.close()

    dict_uuid_ad_port = get_dict_uuid_ad_port(dev_list, ad_port_list)
    file_dict_uuid_ad_port = open('./temp/dict_uuid_ad_port.pkl', 'wb')
    pickle.dump(dict_uuid_ad_port, file_dict_uuid_ad_port)
    file_dict_uuid_ad_port.close()

    res = run_echo_server(dev_list)
    if res:
        report_log('[INFO] 设备端启动状态: 成功')
    else:
        report_log('[ERROR] 设备端启动状态: 失败')


