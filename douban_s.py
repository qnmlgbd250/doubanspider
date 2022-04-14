# -*- coding: utf-8 -*-
# @Time    : 2022/4/11 21:26
# @Author  : huni
# @Email   : zcshiyonghao@163.com
# @File    : douban_s.py
# @Software: PyCharm
import requests
from lxml import etree
import re
import os
from threading import Thread
from queue import Queue
from urllib import parse


class CrawlInfo(Thread):
    def __init__(self, url_queue, html_queue):
        Thread.__init__(self)
        self.url_queue = url_queue
        self.html_queue = html_queue

    def run(self):
        while self.url_queue.empty() == False:
            url = self.url_queue.get()
            resp = requests.get(url = url, headers = headers)
            if resp.status_code == 200:
                self.html_queue.put(resp.text)


class ParseInfo(Thread):
    def __init__(self, html_queue, href_queue):
        Thread.__init__(self)
        self.html_queue = html_queue
        self.href_queue = href_queue

    def run(self):
        while self.html_queue.empty() == False:
            html_one = self.html_queue.get()
            sid_list = re.findall(r'id="list(\d+)"', str(html_one))
            for sid in sid_list:
                self.href_queue.put(sid)



            # page_n = int(tree1.xpath('//*[@id="pageNum"]/a[1]/text()')[0][1:-3])
            # title = tree1.xpath('/html/head/title/text()')[0]
            # href0 = tree1.xpath('/html/head/link[2]/@href')[0]
            # title_path = m_path + f'/{title}'
            # if not os.path.exists(title_path):
            #     os.mkdir(title_path)
            # for i in range(1, page_n + 1):
            #     if i == 1:
            #         every_href = href0
            #     else:
            #         every_href = href0.replace('.html', f'_{i}.html')
            #     resp2 = requests.get(url = every_href, headers = headers)
            #     # 处理中文乱码问题
            #     resp2_text = resp2.text.encode('ISO-8859-1').decode('utf-8')
            #     tree2 = etree.HTML(resp2_text)
            #     src_list = tree2.xpath('/html/body/div[6]//@src')
            #     for src in src_list:
            #         jpg_data = requests.get(url = src, headers = headers).content
            #         jpg_name = src.split("/")[-1]
            #         name_path = title_path + f'/{jpg_name}'
            #         with open(name_path, 'wb') as fp:
            #             fp.write(jpg_data)
            #             print(jpg_name, '下载完成')


if __name__ == '__main__':
    url_queue = Queue()
    html_queue = Queue()
    href_queue = Queue()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Cookie': 'll="118282"; bid=3sEC5kpf9bc; douban-fav-remind=1; _vwo_uuid_v2=D0D4FF79D0BB004C8992BB26C577110FB|2d96a9c2db1c7d308c3c1a2ec9f9308c; __utmc=30149280; __utmc=223695111; __utmz=30149280.1649592275.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=30149280.1441050839.1649592004.1649592004.1649592275.2; _ga=GA1.2.1441050839.1649592004; _gid=GA1.2.1598784901.1649592300; __utmz=223695111.1649592313.4.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=%E8%B1%86%E7%93%A3%E7%BD%91; __utmb=223695111.0.10.1649592313; __utma=223695111.758129777.1649592077.1649592129.1649592313.4; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1649592365%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; ap_v=0,6.0; dbcl2="216412178:3610rHJofMI"; ck=CN1H; push_noty_num=0; push_doumail_num=0; __utmt=1; __utmv=30149280.21641; __utmb=30149280.18.10.1649592275; _pk_id.100001.4cf6=8791788188d02010.1649592365.1.1649593129.1649592365.'
    }

    # m_path = './图图岛'
    # if not os.path.exists(m_path):
    #     os.mkdir(m_path)
    for i in range(1, 26):
        start = (i - 1) * 15
        href = f'https://movie.douban.com/people/216412178/collect?start={start}&sort=time&rating=all&filter=all&mode=list'
        url_queue.put(href)

    crawl_list = []
    for i in range(5):
        Crawl = CrawlInfo(url_queue, html_queue)
        crawl_list.append(Crawl)
        Crawl.start()

    for crawl in crawl_list:
        crawl.join()

    parse_list = []
    for i in range(5):
        parse = ParseInfo(html_queue,href_queue)
        parse_list.append(parse)
        parse.start()

    for parse in parse_list:
        parse.join()
