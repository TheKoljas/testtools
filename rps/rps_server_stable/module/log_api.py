#!/usr/bin/env python
# encoding: utf-8

# 提供测试报告report.log 和 测试错误 error.log 文件写入函数
# 这个函数使用频率和范围比较广, 使用时单独import， 不集成到api.py中

from time import time, ctime, strftime, gmtime
import pickle


def report_log(msg):
    msg = '[ %s ] %s\n' % (ctime(), msg)
    filepath = './log/report_' + strftime('%Y%m%d', gmtime(time())) + '.log'
    with open(filepath, 'a+') as f:
        f.writelines(msg)


def error_log(msg):
    msg = '[ %s ] %s\n' % (ctime(), msg)
    filepath = './log/error_' + strftime('%Y%m%d', gmtime(time())) + '.log'
    with open(filepath, 'a+') as f:
        f.writelines(msg)


def analysis_log(stime, index, msg, amount_dev, amount_on):
    file_dict_analysis_log = open('./temp/dict_analysis_log.pkl', 'rb')
    dict_analysis_log = pickle.load(file_dict_analysis_log)
    file_dict_analysis_log.close()

    if msg:
        dict_analysis_log[msg] = int(dict_analysis_log[msg]) + 1

        file_dict_analysis_log = open('./temp/dict_analysis_log.pkl', 'wb')
        pickle.dump(dict_analysis_log, file_dict_analysis_log)
        file_dict_analysis_log.close()

    if not str(index):
        for key in dict_analysis_log:
            dict_analysis_log[key] = 0
        file_dict_analysis_log = open('./temp/dict_analysis_log.pkl', 'wb')
        pickle.dump(dict_analysis_log, file_dict_analysis_log)
        file_dict_analysis_log.close()
    else:
        utime = time() - int(stime)
        total_failed = int(dict_analysis_log['REG']) + int(dict_analysis_log['STATUS']) + int(dict_analysis_log['BIND']) + int(dict_analysis_log['LIST']) + int(dict_analysis_log['DATA'])
        total_successed = index + 1 - total_failed
        analysis_string = '''本次测试设备端分为3组, 每组设备端数目: %s , 其中每组同时在线设备端数目: %s
本次测试总计消耗时间为: --> %s s
本次测试执行总循环次数: --> %s
本次测试总成功运行次数: --> %s
本次测试总失败运行次数: --> %s

设备端绑定注册异常次数: %s
AUTH SERVER 异常次数: %s
SET CONFIG  异常次数: %s
DEL CONFIG  异常次数: %s

设备端查询绑定异常次数: %s
LOCAL STATUS异常次数: %s
STATUSSERVER异常次数: %s

客户端创建映射异常次数: %s
CTRATE BIND 异常次数: %s
DESTROY BIND异常次数: %s
  
客户端查询映射异常次数: %s

C/D   数据传输异常次数: %s\n''' % (amount_dev, amount_on, int(utime), index + 1, total_successed, total_failed, dict_analysis_log['REG'], dict_analysis_log['AUTH'], dict_analysis_log['SET'], dict_analysis_log['DEL'], dict_analysis_log['STATUS'], dict_analysis_log['LOCAL'], dict_analysis_log['SERVER'], dict_analysis_log['BIND'],dict_analysis_log['CREATE'], dict_analysis_log['DESTROY'], dict_analysis_log['LIST'], dict_analysis_log['DATA'])

        filepath = './log/analysis_' + strftime('%Y%m%d', gmtime(time())) + '.log'
        with open(filepath, 'w') as f:
            f.writelines(analysis_string)

