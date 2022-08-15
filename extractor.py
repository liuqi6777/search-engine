import pickle as pkl
import os
import math
import jieba
import json
from collections import Counter

from tqdm import tqdm
from bs4 import BeautifulSoup

from config import *

doc_dir = DOC_ROW_DIR
output_dir = DOC_TEXT_DIR
process_dir = DOC_PROCESS_DIR

with open('doc/baidu_stopwords.txt') as f:
    stopwords = set(f.readlines())

# 提取html文本内的标题
def extract_title(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    title = soup.find('title')
    if title is None:
        return ''
    title = title.text.strip()
    return title

# 提取html文本内的所有正文文本
def extract_body(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    body = []
    tags = soup.find_all('p')
    for tag in tags:
        body.extend(tag.stripped_strings)
    return '\n'.join(body)

def extract_abstract(html_content, query):
    queries = jieba.lcut(query)
    soup = BeautifulSoup(html_content, 'lxml')
    text = ' '.join([string for string in soup.stripped_strings if string is not None])
    beg = len(text)
    for q in queries:
        if beg > text.find(q):
            beg = text.find(q)
    if beg > 30:
        beg = beg - 30
    else:
        beg = 0
    abstract = '...' + text[beg:beg+80] + '...'
    return abstract
    
def word_filter(word):
    return len(word) > 1 and word not in stopwords


if __name__ == '__main__':
    docs = os.listdir(doc_dir)
    docs_num = len(docs)
    
    blocks_num = 10
    block_size = math.ceil(docs_num / blocks_num)
    
    with open('doc/url.dict', 'rb') as f:
        urls = pkl.load(f)
    # print(len(urls))

    for i in range(blocks_num):
        block_docs = docs[i * block_size:(i + 1) * block_size]
        block_folder = str(i) + '/'
        try:
            os.mkdir(os.path.join(process_dir, block_folder))
        except FileExistsError:
            pass
        try:
            os.mkdir(os.path.join(output_dir, block_folder))
        except FileExistsError:
            pass
        for doc in tqdm(block_docs):
            with open(os.path.join(doc_dir, doc), 'r', encoding='utf-8') as f:
                content = f.read()
            doc_id = int(os.path.splitext(doc)[0])
            title = extract_title(content)
            body = extract_body(content)
            url = urls[doc_id]
            
            body_terms = [word for word in jieba.cut(body) if word_filter(word)]
            title_terms = [word for word in jieba.cut(title) if word_filter(word)]
            
            # words = []
            # words.extend(filter(word_filter, jieba.lcut(title)))
            # words.extend(filter(word_filter, jieba.lcut(body)))
            # with open(os.path.join(output_dir, block_folder, str(doc_id)), 'w', encoding='utf-8') as f:
            #     f.write(' '.join(words))

            with open(os.path.join(process_dir, block_folder, str(doc_id)), 'w', encoding='utf-8') as f:
                doc_info = {
                    'doc_id': doc_id,
                    'url': url,
                    'title': title,
                    'body': body,
                    'dl': len(body_terms),
                    'title-tf': Counter(title_terms),
                    'body-tf': Counter(body_terms)
                }
                json.dump(doc_info, f, ensure_ascii=False)
                
