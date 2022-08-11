import json
import requests
import getpass
from urllib.parse import urljoin
from tqdm import tqdm

# Your Search Engine Function
from search_engine import evaluate

base_url = 'http://183.174.228.82:8080/'

def input_idx():
    idx = input('学号：')
    assert len(idx) == 10, '学号长度必须为 10'
    return idx

def input_passwd():
    passwd = getpass.getpass('助教code (直接回车以进入调试模式，不计分)：')
    if passwd == '':
        print('=== 调试模式 ===')
    return passwd

def login(idx, passwd):
    url = urljoin(base_url, 'login')
    r = requests.post(url, data={'idx': idx, 'passwd': passwd})
    r_dct = eval(r.text)
    queries = r_dct['queries']
    if r_dct['mode'] == 'illegal':
        raise ValueError('助教密码错误，请勿尝试破解密码等非法手段，本次行为已被记录')
    print(f'{len(queries)} queries.')
    return queries

def send_ans(idx, passwd, urls):
    url = urljoin(base_url, 'mrr')
    r = requests.post(url, data={'idx': idx, 'passwd': passwd, 'urls': json.dumps(urls)})
    r_dct = eval(r.text)
    if r_dct['mode'] == 'illegal':
        raise ValueError('助教密码错误，请勿尝试破解密码等非法手段，本次行为已被记录')
    return r_dct['mode'], r_dct['mrr']

def main():
    idx = input_idx()
    passwd = input_passwd()
    queries = login(idx, passwd)

    tot_urls = []
    for query in tqdm(queries, desc='Searching:'):
        urls = evaluate(query)
        tot_urls.append(urls)

    print('等待服务器相应...', flush=True)
    mode, mrr = send_ans(idx, passwd, tot_urls)
    print(f'您的 MRR 评测结果为 [{mrr}], [{mode}] 模式')

if __name__ == '__main__':
    main()
