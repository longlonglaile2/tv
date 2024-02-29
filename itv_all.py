
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
import os
import threading
from queue import Queue
import eventlet
eventlet.monkey_patch()

urls = [
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iSGViZWki",  # Hebei (河北)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iYmVpamluZyI%3D",  # Beijing (北京)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iZ3Vhbmdkb25nIg%3D%3D",  # Guangdong (广东)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbmdoYWki",  # Shanghai (上海)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0idGlhbmppbiI%3D",  # Tianjin (天津)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iY2hvbmdxaW5nIg%3D%3D",  # Chongqing (重庆)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbnhpIg%3D%3D",  # Shanxi (山西)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iU2hhYW54aSI%3D",  # Shaanxi (陕西)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ibGlhb25pbmci",  # Liaoning (辽宁)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iamlhbmdzdSI%3D",  # Jiangsu (江苏)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iemhlamlhbmci",  # Zhejiang (浙江)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5a6J5b69Ig%3D%3D",  # Anhui (安徽)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iRnVqaWFuIg%3D%3D",  # 福建
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rGf6KW%2FIg%3D%3D",  # 江西
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5bGx5LicIg%3D%3D",  # 山东
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rKz5Y2XIg%3D%3D",  # 河南
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5YyXIg%3D%3D",  # 湖北
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5Y2XIg%3D%3D",  # 湖南
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hebei%22",        #河北
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22beijing%22",   #北京
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22guangdong%22",    #广东
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shanghai%22",    #上海
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22tianjin%22",    #天津
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22chongqing%22",    #重庆
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shanxi%22",    #山西
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shaanxi%22",    #陕西
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22liaoning%22",    #辽宁
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22jiangsu%22",    #江苏
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22zhejiang%22",    #浙江
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22anhui%22",    #安徽
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22fujian%22",    #福建
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22jiangxi%22",    #江西
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shandong%22",    #山东
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22henan%22",    #河南
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hubei%22",    #湖北
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hunan%22"    #湖南
    ]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    # 使用WebDriver访问网页
    driver.get(url)  # 将网址替换为你要访问的网页地址
    time.sleep(10)
    # 获取网页内容
    page_content = driver.page_source

    # 关闭WebDriver
    driver.quit()

    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
    urls_all = re.findall(pattern, page_content)
    # urls = list(set(urls_all))  # 去重得到唯一的URL列表
    urls = set(urls_all)  # 去重得到唯一的URL列表
    x_urls = []
    for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
        url = url.strip()
        ip_start_index = url.find("//") + 2
        ip_end_index = url.find(":", ip_start_index)
        ip_dot_start = url.find(".") + 1
        ip_dot_second = url.find(".", ip_dot_start) + 1
        ip_dot_three = url.find(".", ip_dot_second) + 1
        base_url = url[:ip_start_index]  # http:// or https://
        ip_address = url[ip_start_index:ip_dot_three]
        port = url[ip_end_index:]
        ip_end = "1"
        modified_ip = f"{ip_address}{ip_end}"
        x_url = f"{base_url}{modified_ip}{port}"
        x_urls.append(x_url)
    urls = set(x_urls)  # 去重得到唯一的URL列表

    valid_urls = []
    #   多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls:
            url = url.strip()
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)

    for url in valid_urls:
        print(url)
    # 遍历网址列表，获取JSON文件并解析
    for url in valid_urls:
        try:
            # 发送GET请求获取JSON文件，设置超时时间为0.5秒
            ip_start_index = url.find("//") + 2
            ip_dot_start = url.find(".") + 1
            ip_index_second = url.find("/", ip_dot_start)
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_index_second]
            url_x = f"{base_url}{ip_address}"

            json_url = f"{url}"
            response = requests.get(json_url, timeout=0.5)
            json_data = response.json()

            try:
                # 解析JSON文件，获取name和url字段
                for item in json_data['data']:
                    if isinstance(item, dict):
                        name = item.get('name')
                        urlx = item.get('url')
                        #if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                        if 'http' in urlx:
                            urld = f"{urlx}"
                        else:
                            urld = f"{url_x}{urlx}"

                        if name and urlx:
                            # 删除特定文字
                            name = name.replace("cctv", "CCTV")
                            name = name.replace("中央", "CCTV")
                            name = name.replace("高清", "")
                            name = name.replace("HD", "")
                            name = name.replace("标清", "")
                            name = name.replace("频道", "")
                            name = name.replace("-", "")
                            name = name.replace(" ", "")
                            name = name.replace("PLUS", "+")
                            name = name.replace("＋", "+")
                            name = name.replace("(", "")
                            name = name.replace(")", "")
                            name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                            name = name.replace("CCTV1综合", "CCTV1")
                            name = name.replace("CCTV2财经", "CCTV2")
                            name = name.replace("CCTV3综艺", "CCTV3")
                            name = name.replace("CCTV4国际", "CCTV4")
                            name = name.replace("CCTV4中文国际", "CCTV4")
                            name = name.replace("CCTV5体育", "CCTV5")
                            name = name.replace("CCTV6电影", "CCTV6")
                            name = name.replace("CCTV7军事", "CCTV7")
                            name = name.replace("CCTV7军农", "CCTV7")
                            name = name.replace("CCTV7国防军事", "CCTV7")
                            name = name.replace("CCTV8电视剧", "CCTV8")
                            name = name.replace("CCTV9记录", "CCTV9")
                            name = name.replace("CCTV9纪录", "CCTV9")
                            name = name.replace("CCTV10科教", "CCTV10")
                            name = name.replace("CCTV11戏曲", "CCTV11")
                            name = name.replace("CCTV12社会与法", "CCTV12")
                            name = name.replace("CCTV13新闻", "CCTV13")
                            name = name.replace("CCTV新闻", "CCTV13")
                            name = name.replace("CCTV14少儿", "CCTV14")
                            name = name.replace("CCTV15音乐", "CCTV15")
                            name = name.replace("CCTV16奥林匹克", "CCTV16")
                            name = name.replace("CCTV17农业农村", "CCTV17")
                            name = name.replace("CCTV17农业", "CCTV17")
                            name = name.replace("CCTV5+体育赛视", "CCTV5+")
                            name = name.replace("CCTV5+体育赛事", "CCTV5+")
                            name = name.replace("CCTV5+体育", "CCTV5+")
                            results.append(f"{name},{urld}")
            except:
                continue
        except:
            continue


channels = []

for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

error_channels = []


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            随着事件小程序。超时(5, 错误的):
开始时间=时间。时间()
内容=请求。得到(ts_url).内容
结束时间=时间。时间()
响应时间=(结束时间-开始时间) * 1

            如果内容:
                随着 打开(ts_lists_0，ab‘) 如同女:
f.写(内容)  # 写入文件
文件大小=低输入联网（low-entry networking的缩写）(内容)
                #打印（f“文件大小:{文件大小}字节")
下载速度=文件大小/响应时间/1024
                #打印（f“下载速度:{下载速度:。3f} kB/s“）
标准化速度=部(最大(下载速度/1024, 0.001), 100)  # 将速率从kB/秒转换为MB/秒并限制在1~100之间
                #打印（f“标准化后的速率:{normalized_speed:。

                # 删除下载的文件
os。去除(ts_lists_0)
结果=频道名称，频道url，f“{标准化速度:。3f}MB/秒
结果。附加(结果)
numberx =(低输入联网（low-entry networking的缩写）(结果) + 低输入联网（low-entry networking的缩写）(错误频道)) / 低输入联网（low-entry networking的缩写）(频道) * 100
                打印(f“可用频道：{低输入联网（low-entry networking的缩写）(结果)}个,不可用频道：{低输入联网（low-entry networking的缩写）(错误频道)}个,总频道：{低输入联网（low-entry networking的缩写）(频道)}个,总进度：{numberx:。2f} %。")
        除...之外:
错误频道=频道名称，频道url
错误频道。附加(错误通道)
numberx =(低输入联网（low-entry networking的缩写）(结果) + 低输入联网（low-entry networking的缩写）(错误频道)) / 低输入联网（low-entry networking的缩写）(频道) * 100
            打印(f“可用频道：{低输入联网（low-entry networking的缩写）(结果)}个,不可用频道：{低输入联网（low-entry networking的缩写）(错误频道)}个,总频道：{低输入联网（low-entry networking的缩写）(频道)}个,总进度：{numberx:。2f} %。")

        # 标记任务完成
任务队列。任务完成()


# 创建多个工作线程
线程数=10
为 _ 在 范围(线程数):
t =线程。线(目标=工作进程，守护进程=真实的)  # 将工作线程设置为守护线程
t.开始()

# 添加下载任务到队列
为频道在频道:
任务队列。放(频道)

# 等待所有任务完成
任务队列。加入()


极好的 频道键(频道名称):
匹配= re。搜索(r‘\ d+‘，频道名称)
    如果匹配:
        返回 （同Internationalorganizations）国际组织(匹配。组())
    其他:
        返回 漂浮物(inf)  # 返回一个无穷大的数字作为关键字

# 对频道进行排序
结果。分类(密钥=希腊字母的第11个x:(x[0], -漂浮物(x[2].使分离()[0])))
结果。分类(密钥=希腊字母的第11个x:频道键(x[0]))

# 将结果写入文件
随着 打开(“itv_all_results.txt“, “w”，编码=utf-8‘) 如同文件:
    为结果在结果:
频道名称，频道url，速度=结果
文件。写(f“{频道名称},{频道网址},{速度}\n“)

随着 打开(“itv_all_speed.txt“, “w”，编码=utf-8‘) 如同文件:
    为结果在结果:
频道名称，频道url，速度=结果
文件。写(f“{频道名称},{频道网址}\n“)


结果计数器=5  # 每个频道需要的个数

随着 打开(“itv_all.txt“, “w”，编码=utf-8‘) 如同文件:
通道计数器={}
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

with open("itv_all.m3u", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('#EXTM3U\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    #file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    #file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
通道计数器【通道名称】= 1
