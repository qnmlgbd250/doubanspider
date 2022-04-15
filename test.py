# -*- coding: utf-8 -*-
# @Time    : 2022/4/11 22:04
# @Author  : huni
# @Email   : zcshiyonghao@163.com
# @File    : test.py
# @Software: PyCharm
# from lxml import etree
#
# tree = etree.HTML('./test.html')
# li_list = tree.xpath('//*[@id="content"]/div[2]/div[1]/div[2]/div')
# print(li_list)

import re
import csv

sid = '30306570'
with open('douban_movie.csv','rt',encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    column = [row[0] for row in reader]

    print(column)