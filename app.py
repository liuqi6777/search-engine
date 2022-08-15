import json
import os
import pickle as pkl
import jieba

from flask import Flask, request, render_template

from ranker import Ranker
from index.bsbi import BSBIIndex
from models.base_model import TFIDFModel, BoolScorer
from models.bm25 import BM25
from models.idf import Idf, BM25Idf
from config import *


app = Flask(__name__)

bsbi = BSBIIndex(data_dir=DOC_TEXT_DIR, output_dir=INDEX_DIR)
bsbi.load()
# bsbi.index()
# print('INDEX LOADED..')
# idf = Idf(INDEX_DIR)
idf = BM25Idf(INDEX_DIR)
# model = BoolScorer(idf)
# model = TFIDFModel(idf, bsbi)
model = BM25(idf, bsbi, average_dl=50)

ranker = Ranker(index=bsbi, model=model)

with open('doc/url.dict', 'rb') as f:
    url_id_map = pkl.load(f)


def show_results(doc, query):
    url = doc.url
    title = doc.title
    for q in jieba.lcut(query.replace(' ', '')):
        title = title.replace(q, '<span style="color:red">'+q+'</span>')
        # abstract = abstract.replace(q, '<span style="color:red">'+q+'</span>')
    return {'url': url, 'title': title, 'abstract': ''}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['GET'])
def query():
    key = request.args['key']
    docs = ranker.retrieve(key, k=10)
    results = [show_results(doc, key) for doc in docs]
    return render_template('res.html', key=key, results=results, num=len(results))


# gunicorn -w 4 -b 0.0.0.0:5000 app:app
if __name__ == '__main__':
    app.run(debug=True)
