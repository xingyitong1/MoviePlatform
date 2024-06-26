import csv
import requests
import threading
import json
from requests.exceptions import RequestException
from datetime import datetime
import random
import os
import 分割导演
import 分割演员
import 各个类型的电影
import 各个地区各个类型的电影
import convert_to_json


# define number 10
def fetch_data(url, headers, retries=5, timeout=30):
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                print('OK')
                return response.json()
        except RequestException as e:
            print(f"请求失败：{e}")
    return None


if __name__ == '__main__':
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
    }

    random_numbers = random.sample(range(20000, 99999), 10)

    # 构建URL列表
    urls = [
        "http://front-gateway.mtime.com/library/movie/detail.api?tt=1712711802529&movieId={}&locationId=290".format(i)
        for i in random_numbers
    ]

    results = []
    threads = []

    for url in urls:
        thread = threading.Thread(target=lambda: results.append(fetch_data(url, head)))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    movies_info = []  # 存储电影信息的列表
    actors_info = {}  # 存储演员信息的字典，以电影名称和年份作为键
    for result in results:
        if result is not None and isinstance(result, dict) and 'data' in result and isinstance(result['data'],
                                                                                               dict) and 'basic' in \
                result['data']:
            movie_data = result['data']['basic']

            # 提取导演信息
            director_data = movie_data.get('director')
            if director_data:
                director_info = {
                    '导演名称': director_data.get('name', ''),
                    '导演英文名称': director_data.get('nameEn', ''),
                    '导演图片链接': director_data.get('img', ''),
                }
            else:
                director_info = {
                    '导演名称': '',
                    '导演英文名称': '',
                    '导演图片链接': '',
                }

            # 提取演员信息
            actor_data = movie_data.get('actors', [])
            movie_name = movie_data.get('name', '')
            movie_year = movie_data.get('releaseDate', '')[:4] if movie_data.get('releaseDate') else None
            movie_en = movie_data.get('nameEn', '')
            actors_info_key = (movie_name, movie_en, movie_year)
            actors_info[actors_info_key] = []

            for actor in actor_data:
                actor_info = {
                    '演员名称': actor.get('name', ''),
                    '演员英文名称': actor.get('nameEn', ''),
                    '演员图片链接': actor.get('img', ''),
                }
                actors_info[actors_info_key].append(actor_info)

            # 提取上线时间并转换格式
            date_info = movie_data.get('releaseDate', '')
            if date_info:
                date = datetime.strptime(date_info, "%Y%m%d").date().isoformat()
            else:
                date = None

            # 提取电影基本信息
            movie_info = {
                '电影名称': movie_data.get('name', ''),
                '英文名称': movie_data.get('nameEn', ''),
                '评分': movie_data.get('overallRating', 0),
                '上映状态': "已上映" if movie_data.get('isEReleased', 0) == 1 else "未上映",
                '上线时间': date,
                '上线地区': movie_data.get('releaseArea', ''),
                '类型': ', '.join(movie_data.get('type', [])) if isinstance(movie_data.get('type', []), list) else '',
                '电影链接': movie_data.get('url', ''),
                '图片链接': movie_data.get('img', ''),
                '导演信息': json.dumps(director_info, ensure_ascii=False),
            }

            # 将电影信息加入列表
            movies_info.append(movie_info)
    folder_name = "csv_files"
    os.makedirs(folder_name, exist_ok=True)
    # 电影信息写入CSV文件
    movies_info_file = os.path.join(folder_name, 'movies_info.csv')
    with open(movies_info_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=movies_info[0].keys())
        writer.writeheader()
        writer.writerows(movies_info)

    # 演员信息写入CSV文件
    actors_info_file = os.path.join(folder_name, 'actors_info.csv')
    with open(actors_info_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['电影名称', '英文名称', '年份', '演员信息'])
        writer.writeheader()
        for key, value in actors_info.items():
            movie_name, movie_en, movie_year = key
            # 检查电影名称和年份是否为空，设置为None
            if not movie_name:
                movie_name = None
            if not movie_year:
                movie_year = None
            if not movie_en:
                movie_en = None
            writer.writerow(
                {'电影名称': movie_name, '英文名称': movie_en, '年份': movie_year,
                 '演员信息': json.dumps(value, ensure_ascii=False)})

    print("电影信息已保存到", movies_info_file)
    print("演员信息已保存到", actors_info_file)
    分割导演.split1()
    分割演员.split2()
    各个地区各个类型的电影.count1()
    各个类型的电影.count2()
    convert_to_json.convert_to_json()
