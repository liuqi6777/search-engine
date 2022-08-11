from search import cosine_scores

with open('..\\Data\\urls.txt', 'r', encoding='utf-8') as f:
    docid2url = {int(line.split(',')[0]): line.split(',')[1].strip() for line in f.readlines()}
num_pages = len(docid2url)


def evaluate(query_term: str) -> list:
    top_scores = cosine_scores(query_term, k=20)
    url_list = [docid2url[docid] for docid, _ in top_scores][:20]

    while len(url_list) < 20:
        url_list.append(url_list[-1])

    assert len(url_list) == 20

    return url_list
