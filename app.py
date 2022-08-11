from flask import Flask, request, render_template

from ranker import Ranker
from config import *


app = Flask(__name__)


ranker = Ranker(index_dir=INDEX_DIR, model='tf-idf')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['GET'])
def query():
    key = request.args.get('key')
    doc_ids = ranker.retrieval(key, k=10)
    results = [{'url': '', 'title': '', 'abstract': ''} for _ in range(10)]
    return render_template('res.html', key=key, results=results, num=len(results))


if __name__ == '__main__':
    app.run(debug=True)
