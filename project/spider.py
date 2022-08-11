from bs4 import BeautifulSoup
import requests
import urllib.parse as parse
import time
import re
import os
from url_normalize import url_normalize


# 获取url对应的html文本
def fetch_url(url: str, headers: dict) -> str or None:

    try:
        r = requests.get(url, headers=headers)
        r.encoding = 'utf-8'
        r.raise_for_status()
        if re.search(r"window\.location\.href='.+index\.htm';", r.text) is not None:
            return None
        else:
            return r.text

    except requests.HTTPError:
        return None


# 提取html文本内的所有链接
def extract_urls(html_content: str, dir: str = None) -> set:

    urls = set()
    soup = BeautifulSoup(html_content, 'html.parser')

    for anchor in soup.find_all('a'):
        href = anchor.get('href')
        if href != '' or href is not None:
            # 把相对链接转化为绝对链接
            url = parse.urljoin(dir, href)
            url = url_normalize(url)
            if url[-4:] == '.doc' or url[-4:] == '.pdf' or url[-4:] == '.xls' or \
                    url[-5:] == '.xlsx' or url[-5:] == '.docx' or url[-4:] == '.rar' or \
                    url[-4:] == '.zip' or url.find('.jpg') != -1 or url.find('.asp') != -1 or \
                    url[-4:] == '.ppt' or url.find('download') != -1 or url.find('.png') != -1:
                continue

            if url not in urls:
                urls.add(url)

    return urls


# 读取html文件
def read_html(html_file: str, encoding: str = 'utf-8') -> str:

    with open(html_file, 'r', encoding=encoding) as f:
        html_text = f.read()
    return html_text


# 提取html文本内的标题
def extract_title(html_content: str) -> str:

    soup = BeautifulSoup(html_content, 'html.parser')

    return str(soup.find('title'))[7:-8].replace('<br>', '')


# 提取html文本内的所有文本
def extract_contents(html_content: str) -> list:

    result = list()
    soup = BeautifulSoup(html_content, 'html.parser')

    for string in soup.strings:
        result.append(string)

    return result


# 把html文件内的所有文本内容输出到txt文件中
def html_to_txt(html_file: str, txt_file: str) -> None:
    text = extract_contents(read_html(html_file))
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.writelines(text)


seed_urls = {
    'http://jiaowu.ruc.edu.cn/',
    'http://ctd.ruc.edu.cn/web/',
    'http://fangxue.ruc.edu.cn/web/',
    'http://iss.ruc.edu.cn/',
    'http://xsc.ruc.edu.cn/'
}


# 判断是否为需要抓取的目标url
def is_in_task(url: str) -> bool:
    for seed in seed_urls:
        if url.startswith(seed):
            return True
    return False


# 爬虫
def bfs():
    count = 0
    queue = []
    all_urls = set()
    visited_urls = set()
    html_path = '..\\data\\html\\'

    for url in seed_urls:
        if url not in all_urls:
            queue.append(url)
            all_urls.add(url)

    wait_time = 0.5
    headers = {'user-agent': 'my-app/0.0.1'}

    txt = open('urls.txt', 'w')

    while len(queue) > 0:
        url = queue.pop(0)
        visited_urls.add(url)

        if wait_time > 0:
            print("No.{}：等待{}秒后开始抓取页面：{}".format(count, wait_time, url))
            time.sleep(wait_time)

        html_text = fetch_url(url, headers=headers)
        if html_text is None:
            print('Failed to Crawl the Page.')
            continue

        url_sets = extract_urls(html_text, url)
        for new_url in url_sets:
            # 判断新url是否重复
            if new_url not in all_urls and is_in_task(new_url):
                queue.append(new_url)
                all_urls.add(new_url)

        # 保存当前html_doc，防止被封锁
        count = count + 1
        path = html_path + str(count) + ".html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write('<!-- url: %s -->\n' % url)
            f.write(html_text)
            f.close()
        txt.write('{},{}\n'.format(count, url))


if __name__ == '__main__':
    bfs()

    # all_file = os.listdir('..\\data\\html')
    # for file in all_file:
    #     if os.path.splitext(file)[1] == '.html':
    #         t = os.path.join('..\\data\\txt', os.path.splitext(file)[0]+'.txt')
    #         html_to_txt(os.path.join('..\\data\\html', file), t)
    print('Finished!')
