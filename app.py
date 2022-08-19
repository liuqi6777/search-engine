import pickle as pkl
import time
import jieba

from flask import Flask, request, render_template

from ranker import Ranker
from index.bsbi import BSBIIndex
from models import TFIDFModel, BM25
from models.idf import Idf, BM25Idf
from config import *


app = Flask(__name__)

bsbi = BSBIIndex(data_dir=DOC_TEXT_DIR, output_dir=INDEX_DIR)
bsbi.load()
# bsbi.index()
# idf = Idf(INDEX_DIR)
idf = BM25Idf(INDEX_DIR)
# model = TFIDFModel(idf, bsbi)
model = BM25(idf, bsbi, average_dl=50)

ranker = Ranker(index=bsbi, model=model)

with open('doc/url.dict', 'rb') as f:
    url_id_map = pkl.load(f)


def show_results(doc, query):
    url = doc.url
    title = doc.title
    abstract = doc.body
    if len(abstract) > 80:
        abstract = abstract[:80] + '...'
    for q in jieba.lcut(query.replace(' ', '')):
        title = title.replace(q, '<span style="color:red">'+q+'</span>')
        abstract = abstract.replace(q, '<span style="color:red">'+q+'</span>')
    return {'url': url, 'title': title, 'abstract': abstract}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['GET'])
def query():
    global docs, key
    key = request.args['key']
    start = time.process_time()
    docs = ranker.retrieve(key)
    num_docs = len(docs)
    curr_page = int(request.args.get('page', 1))
    pagination = {
        'curr_page': curr_page,
        'num_pages': num_docs // RESULTS_PER_PAGE + 1,
        'start': max(curr_page - 3, 1),
        'end': min(curr_page + 3, num_docs // RESULTS_PER_PAGE + 1)
    }
    results = [show_results(doc, key) for doc in docs[(curr_page-1)*RESULTS_PER_PAGE:curr_page*RESULTS_PER_PAGE]]
    end = time.process_time()
    use_time = round(end - start, ndigits=2)
    return render_template('res.html',
                           key=key, 
                           results=results, 
                           num=num_docs,
                           pagination=pagination,
                           time=use_time)


# gunicorn -w 4 -b 0.0.0.0:5000 app:app
if __name__ == '__main__':
    app.run(debug=True)
