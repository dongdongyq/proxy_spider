# -*- coding: utf-8 -*-
import requests
import random
import threading


class ProxyPool(object):
    def __init__(self, url, path, available_path):
        # 用来验证的网站
        self.url = url
        self.ipType = url.split(':')[0]
        # 代理ip存放的文件地址
        self.path = path
        # 可用代理保存到的地址
        self.available_path = available_path
        # 打开要保存的文件
        self.available_file = open(self.available_path, 'w', encoding='utf-8')
        # 使用多线程
        self.thread = []
        # 线程锁
        self.lock = threading.Lock()
        # 设置头信息
        self.headers = self.set_headers()

    def set_headers(self):
        """
        设置请求头信息
        :return:
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

    def read_proxy(self):
        """
        读取文件中的每个代理ip，并验证其是否可用
        :return:
        """
        with open(self.path, 'r', encoding='utf-8') as fp:
            for proxy in fp.readlines():
                proxy = proxy.strip()
                print(proxy)
                # 使用多线程验证
                t = threading.Thread(target=self.verify_proxy, args=(proxy,))
                self.thread.append(t)

    def verify_proxy(self, proxy):
        """
        验证代理IP是否可用，如果可用则另存为文件
        :param proxy: 代理IP
        :return:
        """
        try:
            response = requests.get(self.url,
                                    headers=self.headers,
                                    proxies={self.ipType: proxy},
                                    timeout=10,
                                    allow_redirects=True)
            print(response.status_code)
            if response.status_code == 200:
                # 使用线程锁，保证写操作不出现问题
                if self.lock.acquire():
                    self.save_available_proxy(proxy)
                    self.lock.release()
        except Exception as e:
            print(e)

    def save_available_proxy(self, proxy):
        """
        将可用代理IP保存到文件
        :param proxy: 可用代理IP
        :return:
        """
        self.available_file.write(proxy + '\n')

    def main(self):
        """
        主函数
        :return:
        """
        # 读取代理IP
        self.read_proxy()
        # 启动多线程
        for t in self.thread:
            t.start()
        # 等待线程结束
        for t in self.thread:
            t.join()
        # 关闭文件
        self.available_file.close()


if __name__ == '__main__':
    # 用来验证的网站
    http_url = "http://www.xicidaili.com/"
    https_url = "https://www.xicidaili.com/"
    # 代理ip存放的文件地址
    http_path = r"D:\python_project\github_spider\proxy_spider\data\http_proxy.txt"
    https_path = r"D:\python_project\github_spider\proxy_spider\data\https_proxy.txt"
    # 可用代理保存到的地址
    http_available_path = r"D:\python_project\github_spider\proxy_spider2\data\available_http_proxy.txt"
    https_available_path = r"D:\python_project\github_spider\proxy_spider2\data\available_https_proxy.txt"

    # http_proxy_pool = ProxyPool(http_url, http_path, http_available_path)
    https_proxy_pool = ProxyPool(https_url, https_path, https_available_path)

    # http_proxy_pool.main()
    https_proxy_pool.main()

