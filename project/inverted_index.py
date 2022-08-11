import os
import jieba
import jieba.analyse
import numpy as np
import sqlite3
from collections import defaultdict, Counter
from spider import extract_title, extract_contents


class Posting:

    def __init__(self, docid: int = 0, tf: int = 0, ld: float = 0., in_title: int = 0):
        self.docid = docid
        self.tf = tf
        self.ld = ld
        self.in_title = in_title

    def __repr__(self):
        return "(%d, %d, %f, %d)" % (self.docid, self.tf, self.ld, self.in_title)

    def __str__(self):
        return "(%d, %d, %f, %d)" % (self.docid, self.tf, self.ld, self.in_title)

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return "(%d, %d, %f, %d)" % (self.docid, self.tf, self.ld, self.in_title)


# 判断词是否需要加入倒排索引
def is_need(word: str) -> bool:

    if word in stop_words:
        return False
    else:
        return True


stop_words = []
term_docid_pairs = []
doc_length = {}
inverted_index = defaultdict(lambda: [Posting(0)])


# 构造倒排索引并储存到数据库
def save_inverted_index():
    all_html_files = [file for file in os.listdir('..\\Data\\html')]

    # 依次打开每个保存正文信息的文本文件，分词，构造term_docid_pairs
    global term_docid_pairs, doc_length, inverted_index
    doc_length[0] = 0.
    for filename in all_html_files:
        with open(os.path.join('..\\Data\\html', filename), encoding='utf-8') as f:
            html_text = f.read()

            title = extract_title(html_text)
            contents = extract_contents(html_text)

            docid = int(os.path.splitext(filename)[0])

            terms = [term for term in jieba.cut(''.join(contents)) if is_need(term)]

            for term in terms:
                in_title = 1 if title.find(term) != -1 else 0
                term_docid_pairs.append((term, docid, in_title))

        # 统计tf
        term_counts = np.array(list(Counter(terms).values()))
        log_tf = 1 + np.log(term_counts)
        doc_length[docid] = np.sqrt(np.sum(log_tf ** 2))

    term_docid_pairs = sorted(term_docid_pairs)

    for term, docid, in_title in term_docid_pairs:
        postings_list = inverted_index[term]
        if docid != postings_list[-1].docid:
            postings_list.append(Posting(docid, 1, doc_length[docid], in_title))
        else:
            postings_list[-1].tf += 1

    conn = sqlite3.connect('..\\Data\\inverted_index2.db')
    c = conn.cursor()

    c.execute('''DROP TABLE IF EXISTS inverted_index''')
    c.execute('''CREATE TABLE inverted_index
                 (term TEXT PRIMARY KEY, df INTEGER, postings TEXT)''')

    for key, value in inverted_index.items():
        postings_list = '\n'.join(map(str, value))
        t = (key, len(value)-1, postings_list)
        c.execute("INSERT INTO inverted_index VALUES (?, ?, ?)", t)

    conn.commit()
    conn.close()


if __name__ == '__main__':

    # with open('..\\Data\\百度停用词表.txt', 'r', encoding='utf-8') as fin:
    #     stop_words = fin.readlines()
    #
    # save_inverted_index()
    pass
