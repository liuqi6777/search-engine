import jieba
import numpy as np
import sqlite3
import requests
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
from inverted_index import Posting


# 获取查询词对应的posting
def get_postings_list(query_term: str) -> list:

    conn = sqlite3.connect('..\\Data\\inverted_index2.db')
    c = conn.cursor()
    sql = "select * from inverted_index where term='%s'" % query_term
    c.execute(sql)
    res = c.fetchone()
    conn.commit()
    conn.close()

    if res is None:
        raise KeyError

    return res


# 计算余弦得分，返回排序后的列表
def cosine_scores(query_term: str, k: int or None = None) -> list:

    scores = defaultdict(lambda: 0.)  # 保存分数
    doc_length = defaultdict(lambda: 0.)
    print(query_term)
    query_terms = Counter(term for term in jieba.cut(query_term) if term != ' ')  # 对查询进行分词
    # print(query_terms)
    for q in query_terms:
        try:
            term, df, postings_list = get_postings_list(q)
            idf = np.log(num_pages / df)
            postings_list = postings_list.split('\n')[1:]
            w_tq = (1 + np.log(query_terms[q]))

            for p in postings_list:
                p = eval(p)
                posting = Posting(p[0], p[1], p[2], p[3])
                w_td = (1 + np.log(posting.tf)) * idf
                if posting.in_title == 1:
                    w_td = w_td * 1.2
                scores[posting.docid] += w_td * w_tq
                doc_length[posting.docid] = posting.ld
        except KeyError:
            pass

    results = [(docid, score / max(doc_length[docid], 20)) for docid, score in scores.items()]
    results.sort(key=lambda x: -x[1])
    return results[:k]


# 获取摘要
def get_abstract(query_term: str, text: str) -> str:

    queries = jieba.lcut(query_term)

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


# 搜索函数，返回包含结果信息的列表
def search(query_term: str, k: int or None = None) -> list:

    top_scores = cosine_scores(query_term, k=k)
    doc_ids = [docid for docid, _ in top_scores]
    results = []
    for docid in doc_ids:

        url = docid2url[docid]
        r = requests.get(url)
        r.encoding = 'utf-8'
        text = r.text
        soup = BeautifulSoup(text, 'html.parser')

        title = str(soup.find('title'))[7:-8].replace('<br>', '')
        contents = ' '.join([tag.string for tag in soup.find_all('p') if tag.string is not None])

        if contents is None or contents == '':
            contents = ' '.join([string for string in soup.stripped_strings if string is not None])

        abstract = get_abstract(query_term, contents)

        for q in jieba.lcut(query_term.replace(' ', '')):

            title = title.replace(q, '<span style="color:red">'+q+'</span>')
            abstract = abstract.replace(q, '<span style="color:red">'+q+'</span>')

        result = {'url': url, 'title': title, 'abstract': abstract}

        results.append(result)

    return results


docid2url = {}
num_pages = 0


# 初始化
def initialize():
    """

    """
    global docid2url, num_pages

    with open('..\\Data\\urls.txt', 'r', encoding='utf-8') as f:
        docid2url = {int(line.split(',')[0]): line.split(',')[1].strip() for line in f.readlines()}

    num_pages = len(docid2url)

    jieba.initialize()

    # print('搜索引擎准备完毕！')


if __name__ == '__main__':

    initialize()
