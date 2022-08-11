from flask import Flask, request, render_template
from search import initialize, search


app = Flask(__name__,
            template_folder='..\\templates',
            static_folder='..\\static',
            static_url_path='')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['GET'])
def query():
    key = request.args.get('key')

    results = search(key, k=10)

    return render_template('res.html', key=key, results=results, num=len(results))


if __name__ == '__main__':

    initialize()

    app.run(debug=True)
