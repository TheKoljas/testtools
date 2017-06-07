#!/usr/bin/env python
# encoding: utf-8

# CopyRight     : xiongmaitech
# Authors       : tianlu@xiongmaitech.com
# Date          : 12-06-2016
# Description   : RPS服务测试基础工具程序

'''
本文件中的函数都只做为工具函数, 供其他文件中函数调用
'''

import random
from time import ctime
import socket
import json
from echo import *
from device import *
from client import *
from status import *
from auth import *
from log_api import *



# cpu ram 监控
# TODO: 基础功能待完善
def basic_cpu_ram_test():
    _basic_cpu_status()
    _basic_ram_status()

# ------------------------------- 基础功能函数 -----------------------------

# 生成三组设备端uuid
def build_dev_list(count_dev):
    _dev_list_1 = ['device1111110' + str(i) for i in range(100, 100 + int(count_dev))]
    _dev_list_2 = ['device2222220' + str(i) for i in range(100 + int(count_dev), 100 + int(count_dev) * 2)]
    _dev_list_3 = ['device3333330' + str(i) for i in range(100 + int(count_dev) * 2, 100 + int(count_dev) * 3)]
    return (_dev_list_1, _dev_list_2, _dev_list_3)


# 测试报告写入
def file_write(content):
    content = '[ %s ] %s\n' % (ctime(), content)
    with open('report', 'a+') as f:
        f.writelines(content)


# 获取空闲port, 设计为生成器可以尽量避免端口重复
def get_free_port():
    port = 24000
    while True:
        if (port < 65000):
            if _check_port(port):
                yield port
        else:
            port = 24000
        port += 1


# 创建设备端 uuid 和 ad_port 对应关系字典
def build_dict_uuid_ad_port(dev_list, ad_port_list):
    _dict_uuid_ad_port = {}
    for dev_group_list in dev_list:
        for uuid in dev_group_list:
            # 每次ad_port_list就弹出最后一个成员
            _dict_uuid_ad_port[uuid] = ad_port_list.pop()

    return _dict_uuid_ad_port


# 获取AgentAccess IP/PORT 列表
def get_aa_ip_port_list():
    aa_ip_list = []
    aa_port_list = []
    aa_ip_port = get_data('./conf/agent_access_ip_port.db')

    for index in range(3):
        aa_ip_list.append(aa_ip_port[str(index)]['IP'])
        aa_port_list.append(aa_ip_port[str(index)]['Port'])

    return aa_ip_list, aa_port_list


# 从输入list中随机选取amount_on个编号
def get_on_off_dev_list(dev_group_list, amount_on):
    _on_dev_list = random.sample(dev_group_list, int(amount_on))
    _off_dev_list = list(set(dev_group_list).difference(set(_on_dev_list)))

    return (_on_dev_list, _off_dev_list)


# 获取文件json数据
def get_data(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        return data


# 从status返回的json中解析出SerialNumber, 返回 on_dev_list off_dev_list
def rsl_status_body(body):
    #body = json.loads(body)
    _on_dev_list = []
    _off_dev_list = []
    for element in body:
        if element['Status'] == u'Online':
            _on_dev_list.append(element['SerialNumber'])
        elif element['Status'] == u'Offline':
            _off_dev_list.append(element['SerialNumber'])
        elif element['Status'] == u'NotAllow':
            error_log('[STATUS SERVER] Device %s is not allow' % element['SerialNumber'])
            pass
    return _on_dev_list, _off_dev_list


# 从listbind返回的json中解析出 uuid:local_port
def rsl_list_bind_body(body):
    body_json = json.loads(body)
    _uuid_local_port_list = []
    _dict_local_port_uuid_port = {}
    for element in body_json:
        value = element['dest_uuid'] + ':' + element['local_port']
        _uuid_local_port_list.append(value)
        _dict_local_port_uuid_port[element['local_port']] = element['dest_port']

    return _uuid_local_port_list, _dict_local_port_uuid_port


# 啊, 下面这一堆为啥搞这么复杂, 待我来分析
# 首先我们listbind得到的结果要和createbind的作对比,
# 然后, 确定无误了, 再判断注册上的uuid是否在on_dev_list中, 只要中间有一个环节出错了, 就直接报错
def check_list_bind(on_dev_list, ac_port_list, dict_ac_port_uuid_local_port, dict_ac_port_uuid_local_port_bind):
    diff_list = []
    for ac_port in ac_port_list:
        diff_list = list(set(dict_ac_port_uuid_local_port[ac_port]).difference(set(dict_ac_port_uuid_local_port[ac_port])))
        if not diff_list:
            for uuid_local_port in dict_ac_port_uuid_local_port[ac_port]:
                uuid, local_port = uuid_local_port.split(':', 1)
                if (uuid in on_dev_list[0]) or (uuid in on_dev_list[1]) or (uuid in on_dev_list[2]):
                    pass
                else:
                    return False
        else:
            return False

    return True


# ---------------------------------- 综合功能函数 -----------------------------

def new_auth_code(dev_list):
    dict_uuid_auth_code = {}
    for dev_group_list in dev_list:
        for uuid in dev_group_list:
            host = '120.132.75.75'
            port = 9907
            header = {"CSeq": "1", "Host": host, "Port": port, "User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)"}
            body = {"AuthProtocol": {"Header": {"Version": "1.0", "CSeq": "1","MessageType": "MSG_MULITAUTH_CODE_NEW_REQ" },"Body": { "UserName": "test", "SecretKey": "123456", "SerialNumber": uuid}}}
            body = json.dumps(body)
            res_new = multi_new_auth_code(host, port, header, body)
            if res_new[0] != 0:
                return res_new
            dict_uuid_auth_code[uuid] = res_new[2]

    return 0, '', dict_uuid_auth_code


# 对index组ON设备执行setconfig 操作
def on_dev_set_config(on_dev_list, dict_uuid_port, dict_uuid_ad_port, aa_ip_list, aa_port_list, index):
    for uuid in on_dev_list[index]:
        aa_ip = aa_ip_list[index]
        aa_port = aa_port_list[index]
        uuid_port = dict_uuid_port[uuid]
        ad_port = dict_uuid_ad_port[uuid]
        host = 'localhost'
        port = ad_port
        header = {"CSeq": "1","Host": host,"Port": port}
        body = {"tcp_access_ip": aa_ip,"tcp_access_port": str(aa_port),"uuid": uuid,"authcode": uuid,"area": "Asia:China:Hangzhou","oemid": "Test","device_tcp_port": str(uuid_port)}
        body = json.dumps(body)

        res_set = dev_set_config(host, port, header, body)
        if res_set[0] != 0:
            return res_set

    return 0, ''


# 对index组OFF设备执行delconfig操作
def off_dev_del_config(off_dev_list, dict_uuid_ad_port, index):
    for uuid in off_dev_list[index]:
        ad_port = dict_uuid_ad_port[uuid]
        host = 'localhost'
        port = ad_port
        header = {"CSeq": "1","Host": host,"Port": port}
        body = ''
        res_del = dev_del_config(host, port, header, body)
        if res_del[0] != 0:
            return res_del

    return 0, ''


# 查询设备 LOCAL STATUS 值, 生成一个ON/OFF 设备uuid列表
def get_local_status(dict_uuid_ad_port):
    on_dev_list_local = []
    off_dev_list_local = []
    for uuid, ad_port in dict_uuid_ad_port.items():
        host = '127.0.0.1'
        port = ad_port
        header = {"headers": {"CSeq": "1", "Host": host, "Port": port, 'content-length': 0}}
        body = ''
        res_local = dev_status(host, port, header, body)
        if (res_local[0] == 0) and (res_local[2] == True):
            on_dev_list_local.append(uuid)
        elif (res_local[0] == 0) and (res_local[2] == False):
            off_dev_list_local.append(uuid)
        else:
            return res_local

    return 0, '', on_dev_list_local, off_dev_list_local


# 查询设备的云端状态
def get_cloud_status(dev_list, dict_uuid_auth_code):
    on_dev_list_cloud = []
    off_dev_list_cloud = []
    headers = get_data('./conf/statusserver_hds_py.db')
    host = headers['Host']
    port = headers['Port']

    header = {"CSeq": "1", "User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)"}
    body = '''{"StatusProtocol": {"Header": {"Version": "1.0","CSeq": "1","MessageType": "MSG_STATUS_MULTIQUERY_REQ"},"Body": ['''
    body_str = ''
    for dev_group_list in dev_list:
        for uuid in dev_group_list:
            body_str += '{"SerialNumber": "%s", "AuthCode": "%s"},' % (uuid, dict_uuid_auth_code[uuid])
    # 要去掉body_str最后的一个冒号
    body = body + body_str[:-1] + ']}}'

    res_cloud = query_cloud_status(host, port, header, body)
    if res_cloud[0] == 0:
        on_dev_list_cloud, off_dev_list_cloud = rsl_status_body(res_cloud[2])
    else:
        return res_cloud

    return 0, '', on_dev_list_cloud, off_dev_list_cloud


# 检查查询到的设备status
# ON/OFF都需要检测, 只要有一个报错, 那就说明系统出了问题, 直接返回ERROR, 只有
# 所有的都通过了, 才可以返回TRUE
def check_dev_status(on_dev_list, off_dev_list, on_dev_list_local, off_dev_list_local, on_dev_list_cloud, off_dev_list_cloud):
    # 先检查下ON/OFF设备的个数是否一致, 如果个数都不一致, 那就不用再一个一个的遍历比较了, 多方便
    len_on_dev = len(on_dev_list[0]) + len(on_dev_list[1]) + len(on_dev_list[2])
    len_off_dev = len(off_dev_list[0]) + len(off_dev_list[1]) + len(off_dev_list[2])
    len_on_dev_local = len(on_dev_list_local)
    len_off_dev_local = len(off_dev_list_local)
    len_on_dev_cloud = len(on_dev_list_cloud)
    len_off_dev_cloud = len(off_dev_list_cloud)
    if (len_on_dev == len_on_dev_local) and (len_off_dev == len_off_dev_local):
	if (len_on_dev == len_on_dev_cloud) and (len_off_dev == len_off_dev_cloud):
            pass
        else:
            error_log('len_on_dev:       %s' % len_on_dev)
            error_log('len_on_dev_local: %s' % len_on_dev_local)
            error_log('len_on_dev_cloud: %s' % len_on_dev_cloud)
            error_log('len_off_dev:       %s' % len_off_dev)
            error_log('len_off_dev_local: %s' % len_off_dev_local)
            error_log('len_off_dev_cloud: %s' % len_off_dev_cloud)
            return False, 'SERVER'
        #pass
    else:
        error_log('len_on_dev:       %s' % len_on_dev)
        error_log('len_on_dev_local: %s' % len_on_dev_local)
        error_log('len_on_dev_cloud: %s' % len_on_dev_cloud)
        error_log('len_off_dev:       %s' % len_off_dev)
        error_log('len_off_dev_local: %s' % len_off_dev_local)
        error_log('len_off_dev_cloud: %s' % len_off_dev_cloud)
	if (len_on_dev == len_on_dev_cloud) and (len_off_dev == len_off_dev_cloud):
            return False, 'LOCAL'
        else:
            return False, 'LOCALSERVER'
        #return False, 'LOCAL'

    print 'on_dev_list -------- %s ' % len_on_dev
    print on_dev_list

    print 'off_dev_list -------- %s ' % len_off_dev
    print off_dev_list

    print 'on_dev_list_local -------- %s ' % len_on_dev_local
    print on_dev_list_local

    print 'off_dev_list_local --------- %s ' % len_off_dev_local
    print off_dev_list_local

    print 'on_dev_list_cloud --------- %s ' % len_on_dev_cloud
    print on_dev_list_cloud

    print 'off_dev_list_cloud ---------- %s ' % len_off_dev_cloud
    print off_dev_list_cloud

    # 从on_dev_list/off_dev_list 开始循环吧, 谁让人家有两层麻烦一些呢
    for on_dev_group_list in on_dev_list:
        for uuid in on_dev_group_list:
            if (uuid in on_dev_list_local):
            	if (uuid in on_dev_list_cloud):
                    pass
                else:
                    return False, 'SERVER'
                pass
            else:
                error_log('[STATUS] %s status is error' % uuid)
            	if (uuid in on_dev_list_cloud):
                    return False, 'LOCAL'
                else:
                    return False, 'LOCALSERVER'
                return False, 'LOCAL'

    for off_dev_group_list in off_dev_list:
        for uuid in off_dev_group_list:
            if (uuid in off_dev_list_local):
            	if (uuid in off_dev_list_cloud):
                    pass
                else:
                    return False, 'SERVER'
                pass
            else:
                error_log('[STATUS] %s status is error' % uuid)
            	if (uuid in off_dev_list_cloud):
                    return False, 'LOCAL'
                else:
                    return False, 'LOCALSERVER'
                return False, 'LOCAL'

    return True, ''


# 客户端对在线设备创建映射, 每一个ac_port都需要对所有在线设备创建映射
def on_dev_create_bind(on_dev_list, ac_port_list, aa_ip_list, aa_port_list, dict_uuid_port, dict_uuid_auth_code):
    _dict_ac_port_uuid_local_port = {}
    for ac_index in range(10):
        ac_port = ac_port_list[ac_index]
        _uuid_local_port_list = []
        for index in range(3):
            for uuid in on_dev_list[index]:
                host = 'localhost'
                port = ac_port
                auth_code = dict_uuid_auth_code[uuid]
                service_type = _get_service_type()
                header = {"headers": { "CSeq": "1", "Host": host, "Port": port}}
                body = {"tcp_access_ip": aa_ip_list[index],"tcp_access_port": str(aa_port_list[index]),"dest_uuid": uuid,"dest_port": str(dict_uuid_port[uuid]), "authcode": auth_code, "service_type": service_type}
                header = json.dumps(header)
                header = json.loads(header)
                body = json.dumps(body)
                res_create = cli_create_bind(host, port, header, body)
                if res_create[0] != 0:
                    return res_create
                value = uuid + ':' + res_create[2]
                _uuid_local_port_list.append(value)
            _dict_ac_port_uuid_local_port[ac_port] = _uuid_local_port_list

    return 0, '', _dict_ac_port_uuid_local_port


def off_dev_destroy_bind(off_dev_list, ac_port_list, dict_uuid_port):
    # 先listbind, 再去destroy(destroy需要传参service_type)
    dict_uuid_local_port_service_type = {}
    res_off = _list_bind_for_off_dev(ac_port_list)
    if res_off[0] != 0:
        #pass
        return res_off
    else:
        dict_uuid_local_port_service_type = res_off[2]
        dict_uuid_local_port_ac_port = res_off[3]

    # 那些本身就不在线的设备就不用执行destroy了, 对于在线的设备才需要执行
    # 而listbind出来的都是在线的设备
    if dict_uuid_local_port_service_type:
        for uuid_local_port, service_type in dict_uuid_local_port_service_type.items():
            _uuid_local_port_list = uuid_local_port.split(':', 1)
            if (_uuid_local_port_list[0] in off_dev_list[0]) or (_uuid_local_port_list[0] in off_dev_list[1]) or (_uuid_local_port_list[0] in off_dev_list[2]):
                host = "localhost"
                port = dict_uuid_local_port_ac_port[uuid_local_port]
                header = {"headers": {"CSeq": "1", "Host": host, "Port": port}}
                dest_uuid = _uuid_local_port_list[0]
                dest_port = dict_uuid_port[dest_uuid]
                body = {"dest_uuid": dest_uuid,"dest_port": str(dest_port),"service_type":  service_type}
                #header = json.loads(header)
                body = json.dumps(body)
                res_destroy = cli_destroy_bind(host, port, header, body)
                if res_destroy[0] != 0:
                    return res_destroy

    return 0, ''


# 对所有ac_port查询映射关系, 我们需要生成bind_uuid_list(内容为10个list, 每一个都相同)
# 然后也需要生成 dict_ac_port_uuid_local_port (一个ac_port对应很多个local_port), 供后面发送数据使用
def all_ac_port_list_bind(ac_port_list):
    _dict_ac_port_uuid_local_port = {}
    _dict_local_port_uuid_port = {}
    for ac_port in ac_port_list:
        _uuid_local_port_list = []
        host = 'localhost'
        port = ac_port
        header = {'content-length':0}
        body = ''
       # header = json.loads(header)
        res_list = cli_list_bind(host, port, header, body)
        if res_list[0] != 0:
            return res_list
        _uuid_local_port_list, _dict_local_port_uuid_port_simple = rsl_list_bind_body(res_list[2])
        _dict_ac_port_uuid_local_port[ac_port] = _uuid_local_port_list
        _dict_local_port_uuid_port[ac_port] = _dict_local_port_uuid_port_simple

    return 0, '', _dict_ac_port_uuid_local_port, _dict_local_port_uuid_port


# -------------------------- 内部调用函数 -------------------------

# 检查端口占用, 端口被占用, 返回True , 端口空闲返回 False
def _is_inuse(ip_list, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    flag = True
    for ip in ip_list:
        try:
            s.connect((ip, int(port)))
            s.shutdown(2)
            flag = True
            break
        except:
            flag = False

    return flag


# 获取本地ip:port
def _get_local_ip():
    return socket.gethostbyname(socket.gethostname())


# 检查端口是否占用
def _check_port(port):
    ip_list = ("127.0.0.1", "0.0.0.0", _get_local_ip())
    if (_is_inuse(ip_list, port)):
        return False
    else:
        return True


# 生成uuid:local_port : service_type 字典, 为off_dev 执行 destroybind做准备
def _list_bind_for_off_dev(ac_port_list):
    _dict_uuid_local_port_service_type = {}
    _dict = {}
    _dict1 = {}
    _dict_uuid_local_port_ac_port = {}
    for ac_port in ac_port_list:
        host = 'localhost'
        port = ac_port
        header = {"headers": {"CSeq": "1","Host": host, "Port": port}}
        body = ''
        header = json.dumps(header)
        header = json.loads(header)
        res_list = cli_list_bind(host, port, header, body)
        if res_list[0] != 0:
            if res_list[1] == 404:
                pass
            else:
                return res_list
        else:
            if res_list[2]:
                _dict = _rsl_list_bind_body_for_off_dev(res_list[2])
                _dict1 = _dict_uuid_local_port_service_type
                _dict_uuid_local_port_service_type = dict(_dict1, **_dict)
        for key in _dict.keys():
            _dict_uuid_local_port_ac_port[key] = ac_port

    return 0, '', _dict_uuid_local_port_service_type, _dict_uuid_local_port_ac_port


# 从listbind返回的json中解析出 dest_uuid:port 对应的 service_type
# 一个设备离线, 那么所有的客户端都需要执行destroybind, 但是考虑到不同客户端与其建立
# 连接的service_type并不同, 那么我们就需要local_port用来区分, 这就是为什么需要local_port的原因
# 生成 dict_uuid_local_port_service_type
def _rsl_list_bind_body_for_off_dev(body):
    body_json = json.loads(body)
    _dict_uuid_local_port_service_type = {}
    for element in body_json:
        key = element['dest_uuid'] + ':' + str(element['local_port'])
        _dict_uuid_local_port_service_type[key] = element['service_type']

    return _dict_uuid_local_port_service_type


# 随机生成service_type
def _get_service_type():
    type_list = ['RpsAV', 'RpsCmd']

    return random.choice(type_list)


