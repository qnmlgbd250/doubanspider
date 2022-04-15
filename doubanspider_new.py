# -*- coding: utf-8 -*-
# @Time    : 2022/4/14 22:17
# @Author  : huni
# @Email   : zcshiyonghao@163.com
# @File    : doubanspider_new.py
# @Software: PyCharm
import requests
import re
import redis
from queue import Queue
from threading import Thread
import threading
import csv

HTML_QUEUE = Queue()
SID_QUEUE = Queue()
info_lists = []


class DoubanSpider_new(object):
    def __init__(self):
        self.redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1, decode_responses=True)
        self.redis_conn = redis.Redis(connection_pool=self.redis_pool)

        self.url = 'https://movie.douban.com/people/216412178/collect'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'cookie': 'bid=jWW9x2iQ-Cs; douban-fav-remind=1; ll="118282"; push_noty_num=0; push_doumail_num=0; _vwo_uuid_v2=D3717E91728222C73EB143CFBEEEF5340|ccd202c5cdc46b612bd4f89715292687; dbcl2="216412178:3610rHJofMI"; __utmv=30149280.21641; __utma=30149280.957401677.1649945701.1649945701.1649983377.2; __utmz=30149280.1649983377.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.620959253.1649983377.1649983377.1649983377.1; __utmz=223695111.1649983377.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ct=y; ck=CN1H; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1649988290%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2F216412178%2F%3F_i%3D9988286jWW9x2i%22%5D; _pk_ses.100001.4cf6=*; _pk_id.100001.4cf6=6c8d5bdfc0625dba.1649638407.7.1649988293.1649985190.'
        }

    def get_every_page_url(self):
        print('获取每页html线程启动')
        for i in range(1, 26):
            start = (i - 1) * 30
            params = {
                'start': start,
                'sort': 'time',
                'filter': 'all',
                'mode': 'list',
                'tags_sort': 'count'
            }
            response = requests.get(self.url, params=params, headers=self.headers)
            if response.status_code == 200:
                HTML_QUEUE.put(response.text)
                print('第' + str(i) + '页加入队列成功')
            else:
                print('请求页码数据失败')

    def get_every_page_movie_sid(self):
        print('获取每页电影sid线程启动')
        while not HTML_QUEUE.empty():
            html = HTML_QUEUE.get()
            sid_list = re.findall(r'id="list(\d+)"', html)
            for sid in sid_list:
                self.redis_conn.lpush('sid_list', str(sid))
            print(str(sid_list) + '电影sid列表加入队列成功')
        print('当前队列获取总数：' + str(self.redis_conn.llen('sid_list')))

    def get_every_page_movie_info(self):
        print('获取每页电影信息线程启动')
        while self.redis_conn.llen('sid_list') > 0:
            info_list = []
            sid = self.redis_conn.rpop('sid_list')
            url = 'https://movie.douban.com/subject/' + sid + '/'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                movie_name = re.search(r'<span property="v:itemreviewed">(.*?)</span>', response.text).group(1)
                movie_score = re.search(r'<strong class="ll rating_num" property="v:average">(.*?)</strong>',
                                        response.text).group(1)
                movie_time = re.search(r'<span property="v:initialReleaseDate" content="(.*?)">', response.text).group(
                    1)
                movie_style = re.findall(r'<span property="v:genre">(.*?)</span>', response.text)
                movie_director = re.findall(r'<meta property="video:actor" content="(.*?)" />', response.text)

                info_list.append(sid)
                info_list.append(movie_name)
                info_list.append(movie_score if movie_score else '暂无评分')
                info_list.append(movie_time if movie_time else '暂无上映时间')
                info_list.append(' '.join(movie_style))
                info_list.append(' '.join(movie_director))
                info_lists.append(info_list)

                print(sid + '保存成功')
            else:
                print('保存数据失败')
                self.redis_conn.lpush('sid_list', str(sid))
                print(f'{sid}>>重新放入队列')
                break

    def find_fish(self):
        with open('douban_movie.csv', 'rt', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            column = [row[0] for row in reader]
        while True:
            sid = self.redis_conn.rpop('sid_list')
            if str(sid) not in column:
                print(sid + '>>没有找到')
                break
            else:
                continue





if __name__ == '__main__':
    douban = DoubanSpider_new()
    douban.get_every_page_url()

    thred1_list = []
    for _ in range(10):
        t1 = Thread(target=douban.get_every_page_movie_sid)
        thred1_list.append(t1)
        t1.start()

    for t1_ in thred1_list:
        t1_.join()

    # thred2_list = []
    # for _ in range(25):
    #     t2 = Thread(target=douban.get_every_page_movie_info)
    #     t2.start()
    #     thred2_list.append(t2)
    #
    # for t2_ in thred2_list:
    #     t2_.join()
    #
    # with open('douban_movie.csv', 'a+', encoding='utf-8',newline='') as file:
    #     writer = csv.writer(file)
    #     # writer.writerow(['movie_sid','movie_name', 'movie_score', 'movie_time', 'movie_style', 'movie_director'])
    #     writer.writerows(info_lists)
