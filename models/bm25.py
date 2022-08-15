from .base_model import BaseScorer


class BM25(BaseScorer):
    def __init__(self, idf, index, average_dl, k1=1.2, b=0.75):
        super().__init__(idf, index)
        self.average_dl = average_dl
        self.k1 = k1
        self.b = b
        
    def get_score(self, q, d):
        score = 0
        for t in q:
            idf = self.idf.get_idf(self.index.term_id_map[t])
            tf = d.body_tf.get(t, 0)
            dl = d.length
            score += idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * (dl / self.average_dl)))
        print(d.title, score)
        return score
