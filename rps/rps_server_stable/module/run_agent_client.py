#!/usr/bin/env python
# encoding: utf-8

import os
import pickle
import multiprocessing
from log_api import error_log


file_ac_port_list = open('./temp/ac_port_list.pkl', 'rb')
ac_port_list = pickle.load(file_ac_port_list)
file_ac_port_list.close()

def agentclient(command):
    ret = os.system(command)
    if ret:
        error_log('[AGENT CLIENT] ' + ret)

def run_agent_client():
    record = []
    for ac_port in ac_port_list:
        command = './module/agentclient ' + str(ac_port) + ' &'
        process = multiprocessing.Process(target=agentclient, args = (command,))
        process.start()
        record.append(process)

    for process in record:
        process.join()

