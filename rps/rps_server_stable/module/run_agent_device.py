#!/usr/bin/env python
# encoding: utf-8

import os
import pickle
import multiprocessing
from log_api import error_log


file_ad_port_list = open('./temp/ad_port_list.pkl', 'rb')
ad_port_list = pickle.load(file_ad_port_list)
file_ad_port_list.close()

def agentdevice(command):
    ret = os.system(command)
    if ret:
        error_log('[AGENT DEVICE] ' + ret)

def run_agent_device():
    record = []
    for ad_port in ad_port_list:
        command = './module/agentdevice ' + str(ad_port) + ' &'
        process = multiprocessing.Process(target = agentdevice, args = (command,))

        process.start()
        record.append(process)

    for process in record:
        process.join()
