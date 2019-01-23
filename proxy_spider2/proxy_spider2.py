# -*- coding: utf-8 -*-
import requests
import time
import os
import random
import multiprocessing
import threading
from bs4 import BeautifulSoup


class XCDL_Spider(object):
    """
    使用代理池无限制爬取西刺代理网站，并保存至文件
    """
    def __init__(self, url):
        # 爬取网站的url
        if not url:
            return
        self.url = url
        self.ipType = self.url.split('/')[-2]
        self.page = 1
        # 保存文件的路径
        self.path = os.path.join(os.path.abspath('.'), "data")
        print(self.path)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        # 设置头信息
        self.headers = self.set_headers()
        # 代理池文件路径
        self.proxy_pool_path = r"D:\python_project\github_spider\proxy_spider2\data\available_https_proxy.txt"
        # 代理池列表
        self.proxy_pool = self.get_proxy_pool(self.proxy_pool_path)
        # 代理指针，-1表示不使用代理
        self.proxy_pool_index = -1
        # 线程锁
        self.lock = threading.Lock()
        # 多线程
        self.thread = []

    def get_proxy_pool(self, path):
        """
        获取可用代理池文件里的代理ip
        :param path: 可用代理IP文件路径
        :return: 可用代理列表
        """
        proxy_pool = []
        with open(path, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                available_proxy = line.strip()
                if available_proxy:
                    proxy_pool.append(available_proxy)
        return proxy_pool

    def set_headers(self):
        """
        设置请求头信息
        :return:请求头
        """
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        ]
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
        }
        return headers

    def get_page(self, url, page=1):
        """
        发起请求并返回页面，设置代理，若代理返回错误或异常，则换下个代理继续执行
        :param url: 要爬取得网站
        :param page: 页码
        :return: 网页源码
        """
        try:
            if self.proxy_pool_index == -1:
                proxy = {}
            elif self.proxy_pool_index < len(self.proxy_pool):
                proxy = {"https": self.proxy_pool[self.proxy_pool_index]}
            else:
                return None
            response = requests.get(url + str(page), headers=self.headers, proxies=proxy, timeout=3)
            if response.status_code == 200:
                return response.text
            else:
                self.proxy_pool_index += 1
                print("返回异常：", response.status_code)
                # print("返回请求：", response.request)
                return self.get_page(url, page)
        except Exception as e:
            self.proxy_pool_index += 1
            return self.get_page(url, page)

    def get_proxy(self, content):
        """
        提取网页中的ip和端口，并写入本地文件
        :param content: 得到的网页源码
        :return:
        """
        soupIP = BeautifulSoup(content, 'lxml')
        if self.page == 1:
            # 获取网站总页数
            page_div = soupIP.find_all('a')
            page = page_div[-2].text.strip()
            self.page = int(page)
        trs = soupIP.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            # print(tds)
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            proxyType = tds[5].text.strip()
            if self.lock.acquire():
                if proxyType == 'HTTP':
                    res = 'http://' + ip + ':' + port
                    print(res)
                    # 将爬取到的代理写入文件
                    self.write_http_proxy(res)
                else:
                    res = 'https://' + ip + ':' + port
                    print(res)
                    # 将爬取到的代理写入文件
                    self.write_https_proxy(res)
                self.lock.release()

    def start_request(self):
        """
        开始爬虫，获取网站总页数，并爬取下一页
        :return:
        """
        # 爬取第一页
        self.parse(self.page)
        # 爬取下一页
        self.next_page()

    def parse(self, page_num):
        """
        根据IP类型得到网页源码，并提取IP和port信息
        :param page_num: 网站页码
        :return:
        """
        content = self.get_page(self.url, page_num)
        if content:
            self.get_proxy(content)

    def next_page(self):
        """
        翻页，使用多线程爬取后续所有页码
        :return:
        """
        for next_page in range(2, self.page):
            t = threading.Thread(target=self.parse, args=(next_page,))
            self.thread.append(t)
        for t in self.thread:
            t.start()
            time.sleep(1)
        for t in self.thread:
            t.join()
        print(self.url, len(self.thread))

    def write_http_proxy(self, proxy):
        """
        保存http代理信息到本地文件
        :param proxy: http代理信息
        :return:
        """
        with open(self.path + "/http_proxy.txt", 'a', encoding='utf-8') as fp:
            fp.write(proxy + '\n')

    def write_https_proxy(self, proxy):
        """
        保存https代理信息到本地文件
        :param proxy: https代理信息
        :return:
        """
        with open(self.path + "/https_proxy.txt", 'a', encoding='utf-8') as fp:
            fp.write(proxy + '\n')


if __name__ == '__main__':
    root_url = "https://www.xicidaili.com/"
    start_url = [root_url + "wt/", root_url + "wn/"]
    pool = multiprocessing.Pool()
    for url in start_url:
        xx = XCDL_Spider(url)
        pool.apply_async(xx.start_request())
    # 关闭进程池
    pool.close()
    # 阻塞进程
    pool.join()
