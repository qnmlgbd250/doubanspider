import requests
import re
from queue import Queue
from threading import Thread
import threading
import time
import csv

lock = threading.Lock()
HTML_QUEUE = Queue()
SID_QUEUE = Queue()
info_lists = []

class DoubanSpider(object):


    def __init__(self):
        self.url = 'https://movie.douban.com/people/216412178/collect'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'cookie': 'll="118282"; bid=3sEC5kpf9bc; douban-fav-remind=1; __utmz=30149280.1649592275.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _ga=GA1.2.1441050839.1649592004; dbcl2="216412178:3610rHJofMI"; push_noty_num=0; push_doumail_num=0; __utmv=30149280.21641; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1649680620%2C%22https%3A%2F%2Fwww.baidu.com%2Fs%3Fie%3DUTF-8%26wd%3D%25E8%25B1%2586%25E7%2593%25A3%22%5D; _pk_id.100001.8cb4=cf05602ccd82cc23.1647846958.5.1649681840.1649594873.; ck=CN1H; ap_v=0,6.0; __utmc=30149280; __utma=30149280.1441050839.1649592004.1649765916.1649767964.5; __utmt=1; __utmb=30149280.6.10.1649767964'
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
                print('第' + str(i) + '加入队列成功')
            else:
                print('请求页码数据失败')

    def get_every_page_movie_sid(self):
        print('获取每页电影sid线程启动')
        while not HTML_QUEUE.empty():
            html = HTML_QUEUE.get()
            sid_list = re.findall(r'id="list(\d+)"', html)
            for sid in sid_list:
                SID_QUEUE.put(sid)




    def get_every_page_movie_info(self):
        print('获取每页电影信息线程启动')
        while not SID_QUEUE.empty():
            info_list = []
            sid = SID_QUEUE.get()
            url = 'https://movie.douban.com/subject/' + sid + '/'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                movie_name = re.search(r'<span property="v:itemreviewed">(.*?)</span>', response.text).group(1)
                movie_score = re.search(r'<strong class="ll rating_num" property="v:average">(.*?)</strong>', response.text).group(1)
                movie_time = re.search(r'<span property="v:initialReleaseDate" content="(.*?)">', response.text).group(1)
                movie_style = re.findall(r'<span property="v:genre">(.*?)</span>', response.text)
                movie_director = re.findall(r'<meta property="video:actor" content="(.*?)" />', response.text)

                info_list.append(movie_name)
                info_list.append(movie_score if movie_score else '暂无评分')
                info_list.append(movie_time if movie_time else '暂无上映时间')
                info_list.append(' '.join(movie_style))
                info_list.append(' '.join(movie_director))
                info_lists.append(info_list)

                print(sid + '保存成功')
            else:
                print('保存数据失败')






if __name__ == '__main__':
    douban = DoubanSpider()
    douban.get_every_page_url()

    thred1_list = []
    for _ in range(1):
        t1 = Thread(target=douban.get_every_page_movie_sid)
        thred1_list.append(t1)
        t1.start()

    for t1_ in thred1_list:
        t1_.join()

    thred2_list = []
    for _ in range(20):
        t2 = Thread(target=douban.get_every_page_movie_info)
        t2.start()
        thred2_list.append(t2)

    for t2_ in thred2_list:
        t2_.join()

    with open('douban_movie.csv', 'a+', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['movie_name', 'movie_score', 'movie_time', 'movie_style', 'movie_director'])
        writer.writerows(info_lists)