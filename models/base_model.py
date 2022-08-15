import jieba
import math

from collections import Counter


class BaseScorer:
    """ An abstract class for a scorer. 
        Implement query vector and doc vector.
        Needs to be extended by each specific implementation of scorers.
    """
    def __init__(self, idf, index):
        self.idf = idf
        self.index = index

    def get_score(self, q, d):
        """ Score each document for each query.
        Args:
            q (Query): the Query
            d (Document) :the Document
        """        
        raise NotImplementedError
    
    
class BoolScorer(BaseScorer):
    def get_score(self, q, d):
        return 1
    
    
class TFIDFModel(BaseScorer):
    def get_score(self, q, d):
        # q_terms = set()
        dl = d.length + 1
        score = [self.idf.get_idf(self.index.term_id_map[t]) * (math.log(d.body_tf.get(t, 0) + 1)) / dl for t in q]
        score = sum(score)
        print(d.title, score)
        return score
