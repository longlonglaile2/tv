#!/usr/bin/env python3
import urllib.request
import threading
import ipaddress

# 定义子网的起始和结束IP地址
subnet_start = "124.231.215.1"
subnet_end = "124.231.215.254"
# 定义要扫描的URL路径列表
url_paths = ["hls/2/index.m3u8", "newlive/live/hls/2/live.m3u8", "tsfile/live/1000_2.m3u8", "tsfile/live/0001_1.m3u8"]  # 如果有需要，可以添加更多的URL路径

# 定义要扫描的端口列表
ports = [85, 808, 7004, 8081, 9901, 8181, 8888, 9999]

# 定义成功IP的文件
successful_ips_file = "successful_jd.txt"

# 定义最大线程数
max_threads = 300

# 检查IP和端口的连通性
def check_ip_port(ip, port, url_path):
    url = f"http://{ip}:{port}/{url_path}"
    try:
        response = urllib.request.urlopen(url, timeout=0.5)
        if response.getcode() == 200:
            content_header = response.headers.get('Content-Type')
            if content_header and 'mpegurl' in content_header:
                print(f"访问 http://{ip}:{port}/{url_path} 成功。服务器: {content_header}")
                with open(successful_ips_file, 'a', encoding='utf-8') as f:
                    f.write(f"{ip}:{port}\n")
    except Exception as e:
        print(f"访问 http://{ip}:{port}/{url_path} 失败: {e}")

# 清空文件内容
open(successful_ips_file, 'w').close()

# 转换起始和结束IP地址为IPv4Address对象
start_ip = ipaddress.IPv4Address(subnet_start)
end_ip = ipaddress.IPv4Address(subnet_end)

# 创建并启动线程来检查每个IP地址和端口
threads = []
for ip in range(int(start_ip), int(end_ip)+1):
    ip_address = str(ipaddress.IPv4Address(ip))
    for port in ports:
        for url_path in url_paths:
            if len(threads) >= max_threads:
                # 如果当前活动线程数已达到最大值，则等待线程完成
                for thread in threads:
                    thread.join()
                threads = []  # 清空线程列表
            thread = threading.Thread(target=check_ip_port, args=(ip_address, port, url_path))
            thread.start()
            threads.append(thread)

# 等待剩余线程完成
for thread in threads:
    thread.join()
