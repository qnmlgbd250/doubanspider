import csv
info_lists = [['不速来客',6.6,'2021-10-22(中国大陆)','喜剧 悬疑,范伟 窦骁 张颂文 朱珠 梁超 胡明 高尚 蔡鹭 东方晓'],['误杀2',5.7,'2021-12-17(中国大陆)','剧情 犯罪','肖央 任达华 文咏珊 陈雨锶 宋洋 李治廷 张世 尹子维 姜皓文 陈昊 周楚濋 王昊泽 强巴才丹']]
with open('douban_movie_test.csv', 'a+', encoding='utf-8',newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['movie_name', 'movie_score', 'movie_time', 'movie_style', 'movie_director'])
    writer.writerows(info_lists)