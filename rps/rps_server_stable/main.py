#!/usr/bin/env python
# encoding: utf-8

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-08-2016
# Description   : RPS 测试主程序

'''
RPS测试主程序函数

主函数 main() 包含初始化及其后所有内容

本函数中的所有函数返回值都只为某一功能 SUCCESSED/FAILED

只要某一个功呢个出现错误，此处就将在report.log中写入状态为“失败”, 当次测试退出,
测试重新开始
'''

from time import *
from module.api import *
from module.log_api import *


usage_str = '''Usage: [OPTIONS]
Options:
-h, --help      Show this help message !
MESSAGE TYPE    INIT | LOOP10 | LOOP
exit            Exit the application !
'''

init_str = ''' RPS 测试系统初始化: '''

reg_str = ''' RPS 测试设备端注册: '''

qry_str = ''' RPS 测试设备端查询: '''

bind_str = ''' RPS 测试客户端映射: '''

list_str = ''' RPS 测试客户端查询: '''

trans_str = ''' RPS 测试数据传输  : '''

reset_str = ''' RPS 测试环境重置  : '''

def service_debug_rps():
    print usage_str

    while True:
        option = format(raw_input("请输入正确的MESSAGE TYPE, 并按下ENTER:")).upper()
        if (option == u'-H' or option == u'--HELP'):
            print usage_str
            continue
        elif option == u'INIT':
            while True:
                while True:
                    amount_dev = format(raw_input("请输入每组设备端数目[1, 100], 并按下ENTER:"))
                    if amount_dev.isdigit():
                        if (100 >= int(amount_dev) >= 1):
                            break
                        else:
                            print '输入有误!'
                            continue
                    else:
                        print '输入有误!'
                        continue

                while True:
                    amount_on = format(raw_input("请输入每组设备端在线数目[1, 100], 并按下ENTER:"))
                    if amount_on.isdigit():
                        if (100 >= int(amount_dev) >= 1):
                            break
                        else:
                            print '输入有误!'
                            continue
                    else:
                        print '输入有误!'
                        continue

                if int(amount_dev) < int(amount_on):
                    print "[ERROR] 每组在线设备数目应小于等于每组设备总数目! 请重新输入."
                    continue
                else:
                    break

            report_log('=====> 测试初始化 <=====')
            error_log('=====> 测试初始化 <=====')

            res_init = init_dev_cli(amount_dev, amount_on)
            if res_init:
                report_log(init_str + '完成')
            else:
                report_log(init_str + '--> 失败')
                continue

        elif option == u'LOOP10':
            report_log('=====> 测试循环10遍 <=====')
            error_log('=====> 测试循环10遍 <=====')

            _flag = False
            stime = time()
            # index 为 '' 表示测试重新开始,所有计数归零
            analysis_log(stime, '', '', amount_dev, amount_on)

            for index in range(1):
                # 只要循环中有一个流程发生错误，就执行重置操作
                if _flag:
                    res_reset = reset_env()
                    if not res_reset:
                        report_log(reset_str + '--> 失败')
                    else:
                        report_log(reset_str + '完成')
                    _flag = False

                report_log('-----> 测试开始：第 %s 循环 <-----' % index)
                error_log('-----> 测试开始：第 %s 循环 <-----' % index)

                res_reg = reg_dev()
                if res_reg:
                    report_log(reg_str + '完成')
                else:
                    _flag = True
                    report_log(reg_str + '--> 失败')
                    analysis_log(stime, index, 'REG', amount_dev, amount_on)
                    if res_reg[1] == 'AUTH':
                        analysis_log(stime, index, 'AUTH', amount_dev, amount_on)
                    elif res_reg[1] == 'SET':
                        analysis_log(stime, index, 'SET', amount_dev, amount_on)
                    elif res_reg[1] == 'DEL':
                        analysis_log(stime, index, 'DEL', amount_dev, amount_on)
                    continue

                res_qry = query_status()
                if res_qry[0]:
                    report_log(qry_str + '完成')
                else:
                    _flag = True
                    report_log(qry_str + '--> 失败')
                    analysis_log(stime, index, 'STATUS', amount_dev, amount_on)
                    if res_qry[1] == 'LOCAL':
                        analysis_log(stime, index, 'LOCAL', amount_dev, amount_on)
                    elif res_qry[1] == 'SERVER':
                        analysis_log(stime, index, 'SERVER', amount_dev, amount_on)
                    elif res_qry[1] == 'LOCALSERVER':
                        analysis_log(stime, index, 'LOCAL', amount_dev, amount_on)
                        analysis_log(stime, index, 'SERVER', amount_dev, amount_on)
                        #pass
                    continue

                res_bind = cli_bind()
                if res_bind:
                    report_log(bind_str + '完成')
                else:
                    _flag = True
                    report_log(bind_str + '--> 失败')
                    analysis_log(stime, index, 'BIND', amount_dev, amount_on)
                    if res_bind[1] == 'CREATE':
                        analysis_log(stime, index, 'CREATE', amount_dev, amount_on)
                    elif res_qry[1] == 'DESTROY':
                        analysis_log(stime, index, 'DESTROY', amount_dev, amount_on)
                    else:
                        pass
                    continue

                res_list = list_bind()
                if res_list:
                    report_log(list_str + '完成')
                else:
                    _flag = True
                    report_log(list_str + '--> 失败')
                    analysis_log(stime, index, 'LIST', amount_dev, amount_on)
                    continue

                res_trans = trans_data()
                if res_trans:
                    report_log(trans_str + '完成')
                else:
                    _flag = True
                    report_log(trans_str + '--> 失败')
                    analysis_log(stime, index, 'DATA', amount_dev, amount_on)
                    continue

                analysis_log(stime, index, '', amount_dev, amount_on)
                _flag = False

        elif option == u'LOOP':
            report_log('=====> 测试循环 ∞ 遍 <=====')
            error_log('=====> 测试循环 ∞ 遍 <=====')

            index = 0
            _flag = False
            stime = time()

            analysis_log(stime, '', '', amount_dev, amount_on)

            while True:
                # 只要循环中有一个流程发生错误，就执行重置操作
                if _flag:
                    res_reset = reset_env()
                    if not res_reset:
                        report_log(reset_str + '--> 失败')
                    else:
                        report_log(reset_str + '完成')
                    index += 1
                    _flag = False

                report_log('-----> 测试开始：第 %s 循环 <-----' % index)
                error_log('-----> 测试开始：第 %s 循环 <-----' % index)
                res_reg = []
                res_reg = reg_dev()
                if res_reg[0]:
                    report_log(reg_str + '完成')
                else:
                    _flag = True
                    report_log(reg_str + '--> 失败')
                    analysis_log(stime, index, 'REG', amount_dev, amount_on)
                    if res_reg[1] == 'AUTH':
                        analysis_log(stime, index, 'AUTH', amount_dev, amount_on)
                    elif res_reg[1] == 'SET':
                        analysis_log(stime, index, 'SET', amount_dev, amount_on)
                    elif res_reg[1] == 'DEL':
                        analysis_log(stime, index, 'DEL', amount_dev, amount_on)
                    continue

	            res_qry = []
                res_qry = query_status()
                if res_qry[0]:
                    report_log(qry_str + '完成')
                else:
                    _flag = True
                    report_log(qry_str + '--> 失败')
                    analysis_log(stime, index, 'STATUS', amount_dev, amount_on)
                    if res_qry[1] == 'LOCAL':
                        analysis_log(stime, index, 'LOCAL', amount_dev, amount_on)
                    elif res_qry[1] == 'SERVER':
                        analysis_log(stime, index, 'SERVER', amount_dev, amount_on)
                    elif res_qry[1] == 'LOCALSERVER':
                        analysis_log(stime, index, 'LOCAL', amount_dev, amount_on)
                        analysis_log(stime, index, 'SERVER', amount_dev, amount_on)
                    continue

                res_bind = []
                res_bind = cli_bind()
                if res_bind[0]:
                    report_log(bind_str + '完成')
                else:
                    _flag = True
                    report_log(bind_str + '--> 失败')
                    analysis_log(stime, index, 'BIND', amount_dev, amount_on)
                    if res_bind[1] == 'CREATE':
                        analysis_log(stime, index, 'CREATE', amount_dev, amount_on)
                    elif res_qry[1] == 'DESTROY':
                        analysis_log(stime, index, 'DESTROY', amount_dev, amount_on)
                    else:
                        pass
                    continue

                res_list = list_bind()
                if res_list:
                    report_log(list_str + '完成')
                else:
                    _flag = True
                    report_log(list_str + '--> 失败')
                    analysis_log(stime, index, 'LIST', amount_dev, amount_on)
                    continue

                res_trans = trans_data()
                if res_trans:
                    report_log(trans_str + '完成')
                else:
                    _flag = True
                    report_log(trans_str + '--> 失败')
                    analysis_log(stime, index, 'DATA', amount_dev, amount_on)
                    continue

                analysis_log(stime, index, '', amount_dev, amount_on)
                _flag = False
                index += 1

        elif option == u'EXIT':
            break

        else:
            print "ERROR OPTIONS!"
            print usage_str


if __name__ == '__main__':
    service_debug_rps()
