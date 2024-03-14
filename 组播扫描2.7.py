#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import threading
import ipaddr

# 定义子网的起始和结束IP地址
subnet_start = "171.213.36.1"
subnet_end = "171.213.254.254"

# 定义要扫描的端口列表
ports = [5005, 8086, 8088, 8888, 9080, 8000]

# 定义成功IP的文件
successful_ips_file = "successful_ips.txt"

# 检查IP和端口的连通性
def check_ip_port(ip, port):
    url = "http://%s:%s/udp/239.93.0.184:5140/qist.m3u8" % (ip, port)
    try:
        response = urllib2.urlopen(url, timeout=0.3)
        if response.getcode() == 200:
            print "访问 %s:%s 成功" % (ip, port)
            with open(successful_ips_file, 'a') as f:
                f.write("%s:%s\n" % (ip, port))
    except Exception as e:
        print "访问 %s:%s 失败: %s" % (ip, port, e)

# 清空文件内容
open(successful_ips_file, 'w').close()

# 转换起始和结束IP地址为IPv4Address对象
start_ip = ipaddr.IPAddress(subnet_start)
end_ip = ipaddr.IPAddress(subnet_end)

# 创建并启动线程来检查每个IP地址和端口
threads = []
for ip in range(int(start_ip), int(end_ip)+1):
    ip_address = str(ipaddr.IPAddress(ip))
    for port in ports:
        thread = threading.Thread(target=check_ip_port, args=(ip_address, port))
        thread.start()
        threads.append(thread)

# 等待所有线程完成
for thread in threads:
    thread.join()