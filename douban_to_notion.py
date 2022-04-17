# -*- coding: utf-8 -*-
# @Time    : 2022/4/17 15:33
# @Author  : huni
# @Email   : zcshiyonghao@163.com
# @File    : douban_to_notion.py
# @Software: PyCharm
# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import json

base_url = "https://book.douban.com/top250?start="
headers = {
    'user-agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'
}


def get_page_content(url):
    page_content = requests.get(url, headers = headers)
    soup = BeautifulSoup(page_content.text, 'html.parser')
    books = soup.find_all("table")
    return books


def get_info(book):
    douban_url = book.find('a')['href']
    cover_url = book.find('img')['src']
    title = book.find("div", class_ = "pl2").find('a').getText().strip()
    title = orgnize_title(title)
    title_en = ''
    preview = ''
    try:
        span = book.find("div", class_ = "pl2").find_all('span')
        title_en = span[len(span) - 1].getText().strip()
        if title_en[0] == ':':
            title_en = ''
    except:
        pass
    book_infos = book.find("p", class_ = "pl").getText().strip()
    author, press = get_auth_press_details(book_infos)
    score = book.find("span", class_ = "rating_nums").getText().strip()
    try:
        preview = book.find("span", class_ = "inq").getText().strip()
    except:
        pass

    return title, title_en, cover_url, author, press, score, preview, douban_url


def orgnize_title(title):
    title_contents = title.split(':')
    real_title = ''
    idx = 0
    for title_content in title_contents:
        if idx > 0:
            real_title += ':'
        real_title += title_content.strip()
        idx += 1
    return real_title


def get_auth_press_details(info_str):
    info = info_str.split("/")
    author = ''
    press = ''
    if len(info) == 4:  # no translater
        author = info[0]
        press = info[1]
    elif len(info) >= 5:  # contain translater
        author = info[0]
        press = info[2]
    return author, press


def get_json_body(db_id, title, title_en, cover_url, author, press, score, preview, no, douban_url):
    notion_data = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "鍚嶇О": {
                "title": [
                    {
                        "text": {
                            "content": "绾㈡ゼ姊�"
                        }
                    }
                ]
            },
            "灏侀潰": {
                "files": [
                    {
                        "type": "external",
                        "name": "test",
                        "external": {"url": "https://img9.doubanio.com/view/subject/s/public/s1070959.jpg"}
                    }
                ]
            },
            "鍘熺増鍚嶇О": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "English"
                        }
                    }]
            },
            "浣滆€�": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "English"
                        }
                    }]
            },
            "璞嗙摚璇勫垎": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "8.6"
                        }
                    }]
            },
            "绠€杩�": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "jianshu"
                        }
                    }]
            },
            "鍑虹増绀�": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "press"
                        }
                    }]
            },
            "No": {
                "number": 1234
            },
            "璞嗙摚閾炬帴": {
                "url": "https://notion.so/notiondevs"
            }
        }
    }

    update_title_prop(notion_data, '鍚嶇О', title)
    update_file_prop(notion_data, '灏侀潰', cover_url)
    update_rich_text_prop(notion_data, '鍘熺増鍚嶇О', title_en)
    update_rich_text_prop(notion_data, '浣滆€�', author)
    update_rich_text_prop(notion_data, '璞嗙摚璇勫垎', score)
    update_rich_text_prop(notion_data, '绠€杩�', preview)
    update_rich_text_prop(notion_data, '鍑虹増绀�', press)
    update_num_prop(notion_data, 'No', no)
    update_url_prop(notion_data, '璞嗙摚閾炬帴', douban_url)

    notoin_data_json = json.dumps(notion_data)

    return notoin_data_json


def update_title_prop(notion_data, prop_name, content):
    notion_data['properties'][prop_name]['title'][0]['text']['content'] = content


def update_file_prop(notion_data, prop_name, content):
    notion_data['properties'][prop_name]['files'][0]['external']['url'] = content


def update_rich_text_prop(notion_data, prop_name, content):
    notion_data['properties'][prop_name]['rich_text'][0]['text']['content'] = content


def update_url_prop(notion_data, prop_name, content):
    notion_data['properties'][prop_name]['url'] = content


def update_num_prop(notion_data, prop_name, content):
    notion_data['properties'][prop_name]['number'] = content


def send_to_notion(body, notion_secret):
    notion_url = "https://api.notion.com/v1/pages"

    notion_headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + notion_secret
    }

    response = requests.request("POST", notion_url, data = body, headers = notion_headers)


# get db_id and notion_secret
db_id = input("Enter your database_id: \n")
notion_secret = input("Enter your Notion secret: \n")

# start scrape
index = 1
for start in range(0, 226, 25):
    url = base_url + str(start)
    books_soup = get_page_content(url)
    for book in books_soup:
        # get book details
        title, title_en, cover_url, author, press, score, preview, douban_url = get_info(book)

        # send book details to Notion
        notion_json_body = get_json_body(db_id, title, title_en, cover_url, author, press, score, preview, index,
                                         douban_url)
        send_to_notion(notion_json_body, notion_secret)
        index += 1

    print("Sent first " + str(start + 25) + " books to Notion.")

