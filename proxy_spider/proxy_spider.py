# -*- coding: utf-8 -*-
import requests
import time
import os
import signal
import random
import multiprocessing
from bs4 import BeautifulSoup


class XCDL_Spider(object):
    """
    爬取西刺代理网站，并保存至文件
    """
    def __init__(self):
        # 爬取网站的url
        self.url = "https://www.xicidaili.com/"
        self.start_url = [self.url + "wt/", self.url + "wn/"]
        # 初始页码
        self.http_page = 1
        self.https_page = 1
        # 保存文件的地址
        self.http_file = "http_proxy.txt"
        self.https_file = "https_proxy.txt"

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
        self.headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
        }

    def get_page(self, url, page=1):
        """
        发起请求并返回页面
        :param url: 要爬取得网站
        :param page: 页码
        :return: 网页源码
        """
        try:
            time.sleep(3)
            response = requests.get(url + str(page), headers=self.headers)
            if response.status_code == "200":
                return response.text
            else:
                print("返回异常：", response.status_code)
        except Exception as e:
            print("进入网站失败。。。", e)
            return None

    def get_proxy(self, content, flag):
        """
        提取网页中的ip和端口，并写入本地文件
        :param content: 得到的网页源码
        :param flag: IP类型
        :return:
        """
        soupIP = BeautifulSoup(content, 'lxml')
        trs = soupIP.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            # print(tds)
            # 只需要高匿代理
            if tds[4].text.strip() != "高匿":
                continue
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            ipType = tds[5].text.strip()
            if ipType == 'HTTP':
                res = 'http://' + ip + ':' + port
                print('http://' + ip + ':' + port)
                # 将爬取到的代理写入文件
                self.write_http_proxy(res)
            else:
                res = 'https://' + ip + ':' + port
                print('https://' + ip + ':' + port)
                # 将爬取到的代理写入文件
                self.write_https_proxy(res)
        # 爬取下一页
        self.next_page(flag)

    def start_request(self, url):
        """
        根据IP类型得到网页源码，并提取IP和port信息
        :param url: 网站地址
        :return:
        """
        ipType = url.split('/')[-2]
        if ipType == "wt":
            print(ipType + '/' + str(self.http_page))
            content = self.get_page(url, self.http_page)
            if content:
                self.get_proxy(content, ipType)
            else:
                # 进入网站异常，立即关闭进程
                print("进入网站异常")
                os.kill(os.getpid(), sig=signal.SIGKILL)
        elif ipType == "wn":
            print(ipType + '/' + str(self.https_page))
            content = self.get_page(url, self.https_page)
            if content:
                self.get_proxy(content, ipType)
            else:
                # 进入网站异常，立即关闭进程
                print("进入网站异常")
                os.kill(os.getpid(), sig=signal.SIGKILL)
        else:
            print("输入的url有误！")

    def next_page(self, flag):
        """
        翻页，爬取下一页
        :param flag: IP类型
        :return:
        """
        if flag == "wt":
            self.http_page += 1
        elif flag == "wn":
            self.https_page += 1
        self.start_request(self.url + flag + '/')

    def write_http_proxy(self, proxy):
        """
        保存http代理信息到本地文件
        :param proxy: http代理信息
        :return:
        """
        path = os.path.join(os.path.abspath('.'), "data")
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + '/' + self.http_file, 'a', encoding='utf-8') as http_file:
            http_file.write(proxy + '\n')

    def write_https_proxy(self, proxy):
        """
        保存https代理信息到本地文件
        :param proxy: https代理信息
        :return:
        """
        path = os.path.join(os.path.abspath('.'), "data")
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + '/' + self.https_file, 'a', encoding='utf-8') as https_file:
            https_file.write(proxy + '\n')

    def main(self):
        """
        主进程
        :return:
        """
        # 设置头信息
        self.set_headers()
        # 创建进程池
        pool = multiprocessing.Pool(2)
        for url in self.start_url:
            # 启动进程
            pool.apply_async(func=self.start_request, args=(url,))
        # 关闭进程池
        pool.close()
        # 阻塞进程
        pool.join()


if __name__ == '__main__':
    xx = XCDL_Spider()
    xx.main()

