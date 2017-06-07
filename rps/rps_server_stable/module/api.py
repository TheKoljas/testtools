#!/usr/bin/env python
# encoding: utf-8

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-06-2016
# Description   : RPS服务测试接口函数


'''
本文件中的函数均为基础测试单元函数
各报错信息均在此打印, 返回值只返回某一项功能 'SUCCESSED/FAILED'
在具体测试中, 根据需求的不同, 我们会使用不同的基础测试内容组合
'''

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import pickle
from client import *
from device import *
from utils import *
from echo import *
from log_api import error_log, analysis_log
import time
import multiprocessing

MANAGER = multiprocessing.Manager()
Q_CLI = MANAGER.Queue()
LOCK_CLI = MANAGER.Lock()


exec_ret_dicts = {
    'status': 0,
    'target': 0,
    'errors': ''
}


# --------------------- main.py 调用函数 ----------------------

# 每次测试完成后, 初始化测试环境
def reset_env():
    try:
        os.system('rm -rf temp/dict_ac_port_uuid_local_port.pkl temp/dict_local_port_uuid_port.pkl temp/off_dev_list.pkl temp/on_dev_list.pkl temp/used_port_list')
    except Exception, e:
        error_log('reset_env: %s' % e)
        return False
    else:
        return True


# 初始化客户端, 设备端
# 设备端序列号生成的函数放在了run_device.py文件中, 理论上放在这里更适合
# 在这里我们完成了设备端的setconfig/delconfig, 至于客户端.... 看样子真正的
# 初始化应该在后面的创建映射时
def init_dev_cli(amount_dev, amount_on):
    os.system('rm ./temp/*')
    os.system("kill -9 `ps -ef|grep device|grep -v grep|awk '{print $2}'`")
    os.system("kill -9 `ps -ef|grep client|grep -v grep|awk '{print $2}'`")

    # dev_list       在run_device.py中生成
    # dict_uuid_port 在run_device.py中生成
    # dict_uuid_ad_port 在run_device.py中生成
    # TODO: 此处启动了AgentClient, 并且分配了PORT, 由此, 生成了ac_port_list
    #       此处启动了AgentDevice, 并且分配了PORT, 由此, 生成了ad_port_list
    ac_port_list = []
    p = get_free_port()
    file_ac_port_str = open('./temp/ac_port_str', 'wb')
    for index in range(10):
        ac_port = p.next()
        ac_port_list.append(ac_port)
        file_ac_port_str.write(str(ac_port) + '\n')
    file_ac_port_str.close()

    file_ac_port_list = open('./temp/ac_port_list.pkl', 'wb')
    pickle.dump(ac_port_list, file_ac_port_list)
    file_ac_port_list.close()

    # 为什么这里要沿用上面的生成器? 因为要考虑到上面分配的端口并不是立刻就使用了
    file_ad_port_str = open('./temp/ad_port_str', 'wb')
    ad_port_list = []
    # amount_dev 是每组设备端数目, 总数当然要 * 3
    for index in range(int(amount_dev) * 3):
        ad_port = p.next()
        ad_port_list.append(ad_port)
        file_ad_port_str.write(str(ad_port) + '\n')
    file_ad_port_str.close()

    file_ad_port_list = open('./temp/ad_port_list.pkl', 'wb')
    pickle.dump(ad_port_list, file_ad_port_list)
    file_ad_port_list.close()

    file_amount_dev = open('./temp/amount_dev.pkl', 'wb')
    pickle.dump(amount_dev, file_amount_dev)
    file_amount_dev.close()

    file_amount_on = open('./temp/amount_on.pkl', 'wb')
    pickle.dump(amount_on, file_amount_on)
    file_amount_on.close()

    # 初始化错误统计信息
    dict_total = {}
    file_dict_total = open('./temp/dict_total.pkl', 'wb')
    pickle.dump(dict_total, file_dict_total)
    file_dict_total.close()

    dict_analysis_log = {}
    dict_analysis_log['REG'] = 0
    dict_analysis_log['AUTH'] = 0
    dict_analysis_log['SET'] = 0
    dict_analysis_log['DEL'] = 0
    dict_analysis_log['STATUS'] = 0
    dict_analysis_log['LOCAL'] = 0
    dict_analysis_log['SERVER'] = 0
    dict_analysis_log['BIND'] = 0
    dict_analysis_log['CREATE'] = 0
    dict_analysis_log['DESTROY'] = 0
    dict_analysis_log['LIST'] = 0
    dict_analysis_log['DATA'] = 0
    file_dict_analysis_log = open('./temp/dict_analysis_log.pkl', 'wb')
    pickle.dump(dict_analysis_log, file_dict_analysis_log)
    file_dict_analysis_log.close()

    return True


# 设备端注册
# 对ON/OFF设备分别执行setconfig/delconfig操作
def reg_dev():
    # 获取 aa ip/prt 列表
    aa_ip_list, aa_port_list = get_aa_ip_port_list()
    # 获取总的 dev_list
    file_dev_list = open('./temp/dev_list.pkl', 'rb')
    dev_list = pickle.load(file_dev_list)
    file_dev_list.close()
    # 获取uuid:port对应关系dict
    file_dict_uuid_port = open('./temp/dict_uuid_port.pkl', 'rb')
    dict_uuid_port = pickle.load(file_dict_uuid_port)
    file_dict_uuid_port.close()
    # 获取uuid对应的ad_port 对应关系 dict
    file_dict_uuid_ad_port = open('./temp/dict_uuid_ad_port.pkl', 'rb')
    dict_uuid_ad_port = pickle.load(file_dict_uuid_ad_port)
    file_dict_uuid_ad_port.close()

    # 设备要注册到auth服务器上
    if not os.path.exists('./temp/dict_uuid_auth_code.pkl'):
        res_new = new_auth_code(dev_list)
        if res_new[0] != 0:
            exec_ret_dicts.update({
                'status': res_new[0],
                'target': res_new[0],
                'errors': res_new[1]
            })
            error_log('[AUTH SERVER]' + exec_ret_dicts['errors'])
            return False, 'AUTH'

        file_dict_uuid_auth_code = open('./temp/dict_uuid_auth_code.pkl', 'wb')
        pickle.dump(res_new[2], file_dict_uuid_auth_code)
        file_dict_uuid_auth_code.close()

    # 获取每组在线设备数目
    file_amount_on = open('./temp/amount_on.pkl', 'rb')
    amount_on = pickle.load(file_amount_on)
    file_amount_on.close()

    on_dev_list = [] # 会包含三个on list
    off_dev_list = [] # 会包含三个off list
    for dev_group_list in dev_list:
        on_list, off_list = get_on_off_dev_list(dev_group_list, amount_on)
        on_dev_list.append(on_list)
        off_dev_list.append(off_list)

    # 将on_dev_list/off_dev_list固化, 供后面使用
    file_on_dev_list = open('./temp/on_dev_list.pkl', 'wb')
    pickle.dump(on_dev_list, file_on_dev_list)
    file_on_dev_list.close()

    file_off_dev_list = open('./temp/off_dev_list.pkl', 'wb')
    pickle.dump(off_dev_list, file_off_dev_list)
    file_off_dev_list.close()

    for index in range(3):
        res_set = on_dev_set_config(on_dev_list, dict_uuid_port, dict_uuid_ad_port, aa_ip_list, aa_port_list, index)
        if res_set[0] != 0:
            return False, 'SET'

        res_del = off_dev_del_config(off_dev_list, dict_uuid_ad_port, index)
        if res_del[0] != 0:
            return False, 'DEL'
    # setconfig 后立即去查服务器垣断是没有准备好的, 所以先sleep一下
    time.sleep(5)
    return True, ''


# 查询所有在线设备状态, 这里的STATUS包括STATUS SERVER服务器查询和设备端LOCAL STATUS
# 查询对照的方法就是云状态批量查询, 与上一步on_dev_list对比, 本地状态一个个查询, 同样需要做对比
# 对比时OFF状态的也需要对比!!!
# 对照需要 on_dev_list off_dev_list
#          on_dev_list_local off_dev_list_local
#          on_dev_list_cloud off_dev_list_cloud
def query_status():
    # 先读取on_dev_list 和 off_dev_list (各有3组)
    file_on_dev_list = open('./temp/on_dev_list.pkl', 'rb')
    on_dev_list = pickle.load(file_on_dev_list)
    file_on_dev_list.close()
    file_off_dev_list = open('./temp/off_dev_list.pkl', 'rb')
    off_dev_list = pickle.load(file_off_dev_list)
    file_off_dev_list.close()

    # 需要获取uuid和ad_port的对应关系
    file_dict_uuid_ad_port = open('./temp/dict_uuid_ad_port.pkl', 'rb')
    dict_uuid_ad_port = pickle.load(file_dict_uuid_ad_port)
    file_dict_uuid_ad_port.close()

    # 需要获取uuid和auth_code的对应关系
    file_dict_uuid_auth_code = open('./temp/dict_uuid_auth_code.pkl', 'rb')
    dict_uuid_auth_code = pickle.load(file_dict_uuid_auth_code)
    file_dict_uuid_auth_code.close()

    file_dev_list = open('./temp/dev_list.pkl', 'rb')
    dev_list = pickle.load(file_dev_list)
    file_dev_list.close()

    # 先查询本地的LOCAL STATUS
    res_local = get_local_status(dict_uuid_ad_port)
    if res_local[0] != 0:
        return False, 'LOCAL'

    on_dev_list_local = res_local[2]
    off_dev_list_local = res_local[3]

    # 查询云端STATUS SERVER
    res_cloud = get_cloud_status(dev_list, dict_uuid_auth_code)
    if res_cloud[0] != 0:
        return False, 'SERVER'

    on_dev_list_cloud = res_cloud[2]
    off_dev_list_cloud = res_cloud[3]

    # 比较三个有关状态的列表是否一致, 写个单独的程序比较合适
    res_check = []
    res_check = check_dev_status(on_dev_list, off_dev_list, on_dev_list_local, off_dev_list_local, on_dev_list_cloud, off_dev_list_cloud)
    if res_check[0]:
        return True, ''
    else:
        error_log('[STATUS] RPS 云状态查询结果|设备端STATUS查询结果|在线设备设备号三者不一致')
	return res_check


# 客户端对ON执行createbind, 对OFF执行 destroybind
# 需要的参数有 aa_ip/aa_port  uuid/port local_host/local_port
# 其中 aa_ip/aa_port 对应的 uuid这个关系默认是已知的
# local_host/local_port 则是在AgentClient启动时给其分配的port, 所以这里默认已知
# TODO: 创建一个对应关系, aa : dev_list
#       创建一个列表, ac_port_list
# TODO: 看样子是要在这里启动AgentClient, 并且给他分配PORT
def cli_bind():
    # 获取 aa ip/prt 列表
    aa_ip_list, aa_port_list = get_aa_ip_port_list()
    # 获取AgentClient端口列表
    file_ac_port_list = open('./temp/ac_port_list.pkl', 'rb')
    ac_port_list = pickle.load(file_ac_port_list)
    file_ac_port_list.close()
    # 先读取on_dev_list 和 off_dev_list (各有3组)
    file_on_dev_list = open('./temp/on_dev_list.pkl', 'rb')
    on_dev_list = pickle.load(file_on_dev_list)
    file_on_dev_list.close()
    file_off_dev_list = open('./temp/off_dev_list.pkl', 'rb')
    off_dev_list = pickle.load(file_off_dev_list)
    file_off_dev_list.close()
    # 获取 uuid port 关系字典
    file_dict_uuid_port = open('./temp/dict_uuid_port.pkl', 'rb')
    dict_uuid_port = pickle.load(file_dict_uuid_port)
    file_dict_uuid_port.close()
    # 获取 uuid port 关系字典
    file_dict_uuid_auth_code = open('./temp/dict_uuid_auth_code.pkl', 'rb')
    dict_uuid_auth_code = pickle.load(file_dict_uuid_auth_code)
    file_dict_uuid_auth_code.close()

    # OFF 设备执行 destroybind
    res_off = off_dev_destroy_bind(off_dev_list, ac_port_list, dict_uuid_port)
    if res_off[0] != 0:
        return False, 'DESTROY'

    # ON 设备执行 createbind
    _dict_ac_port_uuid_local_port = {}
    res_create = on_dev_create_bind(on_dev_list, ac_port_list, aa_ip_list, aa_port_list, dict_uuid_port, dict_uuid_auth_code)
    if res_create[0] != 0:
        return False, 'CREATE'
    _dict_ac_port_uuid_local_port = res_create[2]

    if os.path.exists('./temp/dict_ac_port_uuid_local_port.pkl'):
        os.system('rm ./temp/dict_ac_port_uuid_local_port.pkl')
    file_dict_ac_port_uuid_local_port = open('./temp/dict_ac_port_uuid_local_port.pkl', 'wb')
    pickle.dump(_dict_ac_port_uuid_local_port, file_dict_ac_port_uuid_local_port)
    file_dict_ac_port_uuid_local_port.close()

    return True, ''


# 查询映射关系 list_bind
# 需要的参数有 ac_port_list, 查询后生成 dict_uuid_local_port, 将这个字典里的uuid和on_dev_list作对比
def list_bind():
    # 获取AgentClient端口列表
    file_ac_port_list = open('./temp/ac_port_list.pkl', 'rb')
    ac_port_list = pickle.load(file_ac_port_list)
    file_ac_port_list.close()
    # 加个_list表示这是listbind得到的
    _dict_ac_port_uuid_local_port = {}

    res_list = all_ac_port_list_bind(ac_port_list)
    if res_list[0] != 0:
        return False

    _dict_ac_port_uuid_local_port = res_list[2]
    # 读取上一步生成的dict_ac_port_local_port_bind (加上bind以示区别)
    file_dict_ac_port_uuid_local_port = open('./temp/dict_ac_port_uuid_local_port.pkl', 'rb')
    dict_ac_port_uuid_local_port_bind = pickle.load(file_dict_ac_port_uuid_local_port)
    file_dict_ac_port_uuid_local_port.close()

    dict_local_port_uuid_port = {}
    dict_local_port_uuid_port = res_list[3]
    file_dict_local_port_uuid_port = open('./temp/dict_local_port_uuid_port.pkl', 'wb')
    pickle.dump(dict_local_port_uuid_port, file_dict_local_port_uuid_port)
    file_dict_local_port_uuid_port.close()

    file_on_dev_list = open('./temp/on_dev_list.pkl', 'rb')
    on_dev_list = pickle.load(file_on_dev_list)
    file_on_dev_list.close()

    res_check = check_list_bind(on_dev_list, ac_port_list, _dict_ac_port_uuid_local_port, dict_ac_port_uuid_local_port_bind)
    if res_check:
        return True
    else:
        error_log('[LIST BIND] listbind 的结果与createbind 不一致, 检查失败')
        return False


def trans_data():
    # 启动echo_cli
    # 启动Client发送数据时需要传入local_port, 那么这一步必然是在list_bind之后
    file_ac_port_list = open('./temp/ac_port_list.pkl', 'rb')
    ac_port_list = pickle.load(file_ac_port_list)
    file_ac_port_list.close()

    file_dict_ac_port_uuid_local_port = open('./temp/dict_ac_port_uuid_local_port.pkl', 'rb')
    dict_ac_port_uuid_local_port = pickle.load(file_dict_ac_port_uuid_local_port)
    file_dict_ac_port_uuid_local_port.close()

    # TODO: 在完成listbind之后再来写
    res_cli = _run_echo_client(ac_port_list, dict_ac_port_uuid_local_port)
    if res_cli:
        return True
    else:
        return False


# ---------------- 基础功能函数 ----------------------

# 获取三组设备uuid, 以[[], [], []]的格式返回
def get_three_group_dev_list(amount_dev):
    dev_list = build_dev_list(amount_dev)
    return dev_list


# 获取 uuid 和 ad_port 对应关系字典
def get_dict_uuid_ad_port(dev_list, ad_port_list):
    return build_dict_uuid_ad_port(dev_list, ad_port_list)


def basic_cpu_ram_test():
    _basic_cpu_status()
    _basic_ram_status()


# ---------------- 集成功能函数 ----------------------

# 启动设备端, 会生成dict_uuid_port 对应关系dict
def run_echo_server(dev_list):
    dict_uuid_port = {}
    p = get_free_port()

    pool_dev = multiprocessing.Pool(len(dev_list[0]) + len(dev_list[1]) + len(dev_list[2]))
    for dev_group_list in dev_list:
        for uuid in dev_group_list:
            port = p.next()
            dict_uuid_port[uuid] = port
            host = 'localhost'
            pool_dev.apply_async(echo_server, (host, port,))

    file_dict_uuid_port = open('./temp/dict_uuid_port.pkl', 'wb')
    pickle.dump(dict_uuid_port, file_dict_uuid_port)
    file_dict_uuid_port.close()

    pool_dev.close()
    pool_dev.join()

    return True


# 客户端启动函数, 需要接受的传参有 ac_port_list, dict_ac_port_uuid_local_port_bind
# 我们需要通过dict_ac_port_uuid_local_port_bind 查找每个ac_port对应的local_port
def _run_echo_client(ac_port_list, dict_ac_port_uuid_local_port):
    file_dict_local_port_uuid_port = open('./temp/dict_local_port_uuid_port.pkl', 'rb')
    dict_local_port_uuid_port = pickle.load(file_dict_local_port_uuid_port)
    file_dict_local_port_uuid_port.close()
#    print dict_local_port_uuid_port
    pool_cli = multiprocessing.Pool(10)

    # 通过异步方式， 起10个进程
    for ac_port in ac_port_list:
        for uuid_local_port in dict_ac_port_uuid_local_port[ac_port]:
            uuid, local_port = uuid_local_port.split(':', 1)
            host = 'localhost'
            port = local_port
            uuid_port = dict_local_port_uuid_port[ac_port]
            dest_port = uuid_port[port]
            pool_cli.apply_async(client_send_data_multi_thread, (host, port, dest_port, Q_CLI, LOCK_CLI,))

    pool_cli.close()
    pool_cli.join()

    result = []
    while not Q_CLI.empty():
        result.append(Q_CLI.get())
    for item in result:
        if not item:
            return False

    return True


