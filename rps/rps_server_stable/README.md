# RPS 测试文档
    请在阅读本文档后, 再进行相关测试操作.  

> VERSION : 0.2  
> MODIFIED: 2016-12-29  
> AUTHORS : tianlu@xiongmaitech.com  

## 文件结构
    ```shell
    .
    ├── conf        配置文件目录
    ├── log         生成的日志及报告文件目录
    ├── module      程序代码模块目录
    ├── temp        程序运行中生成的临时文件目录
    ├── main.py     主函数文件
    ├── run_agent_and_device.py     代理及设备端程序运行文件
    └── README.md   README 文件
    ```

## 测试目标
在测试中我们设计了多台设备端, 多台客户端, 4台AgentServer, 1台AgentAccess和1台  
STATUS SERVER, 来进行测试.在测试中我们同时完成了功能测试和性能测试两个部分.  

我们主要的测试内容包括:  
    * 设备端: setconfig, delconfig, status  
    * 客户端: createbind, destroybind, listbind  
    * AgentAccess: 设备端注册功能, 客户端连接请求, 请求设备端连接功能  
    * AgentServer: 数据通信功能  
    * 多客户端多设备端同时通信系统稳定性  
    * 循环测试中不断更新设备在线状态, 模拟真实场景  
    * 持续测试系统稳定性  

## 测试方法
1. 准备工作:  
    conf 目录:  
        agent_access_ip_port.db: 配置正确的AgentAccess 服务器 ip/port  

2. 初始化主程序:
    在`rps_server`目录下, 运行 `main.py`, 选择 INIT  
    选择设备端每组设备数, [1, 100]  
    选择设备端每组在线设备数, [1, 100]  

3. 启动代理和设备端程序:  
    在`rps_server`目录下, 运行 `run_agent_and_device.py`  
    检查程序是否运行成功:  
        在Shell窗口运行 `ps -ef | grep agentdevice | wc`  
            -->  (输入设备数 * 3 + 1)  
        在Shell窗口运行 `ps -ef | grep device | wc`  
            -->  (输入设备数 * 3 * 2 + 1)  
        在Shell窗口运行 `ps -ef | grep agentclient | wc`  
            -->  11  

4. 在主程序选项中选择循环次数:  
    LOOP10 循环10遍 / LOOP 无限循环  

5. 查看运行情况:  
    在 `rps_server/log` 目录中, 可以分别 `tail -f filename`, 可以实时查看程序   
    运行结果  

6. 程序结束  
    * EXIT 退出, 一切正常
    * 手动强制退出(无限循环测试时), 此时需要注意不要在数据通信测试时退出, 请在   
      其他时间段按下 `Ctrl + C`, 然后再次启动 `main.py`, 执行 EXIT 退出.  
      (否则, 后台会有大量未退出进程)  
      TODO: 此处需要解决多进程手动退出问题

## 测试内容详述
1. 初始化 INIT
    * AgentAccess AgentServer 已经启动
    * 生成
        ac_port_list
        ad_port_list
        ad_port_str
        amount_dev
        amount_on
        dict_total

    * 启动AgentClient和AgentDevice

    * 启动设备端
        dev_list (3组) (生成设备端uuid列表)
        dict_uuid_port (将设备端uuid和端口对应关系保存为dict)
        dict_uuid_ad_port (将设备端和AgentDevice端口一一对应起来)

2. 设备端注册 DEVREG
    * 设备注册到AUTH SERVER
        dict_uuid_auth_code

    * 生成ON/OFF uuid列表
        on_dev_list
        off_dev_list

    * 分别对ON/OFF 设备执行操作
        * ON 设备
            分别对on_dev_list中的每一个uuid执行 setconfig 操作
        * OFF 设备
            分别对off_dev_list中的每一个uuid执行 delconfig 操作

3. 设备注册状态查询 QUERYSTATUS
    * 查询 LOCAL STATUS
        on_dev_list_local
        off_dev_list_local

    * 查询 CLOUD STATUS
        on_dev_list_cloud
        off_dev_list_cloud

    * 状态检验
        将以上的四个list与on_dev_list off_dev_list 进行比较

4. 客户端绑定 BIND
    * OFF 设备执行 destroybind
        需要先查询需要OFF的设备里有哪些是在线的, 只需要对在线的设备执行操作
    * ON 设备执行 createbind
        dict_ac_port_uuid_local_port

5. 客户端查询绑定 LISTBIND
    * 查询每一个ac_port对应的uuid 是否在 on_dev_list 之中

6. 客户端/设备端数据通信 SENDDATA
    * 启动 run_device.py




## 测试待补充


## 常见问题


## 更新日志
