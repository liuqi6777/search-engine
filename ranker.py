import os

from index.bsbi import BSBIIndex
from models.base_model import BaseScorer
from document import Document
from query import Query
from config import *


class Ranker:
    def __init__(self, index, model):
        """
        Parametes:
          index: BSBIIndex
          model: BaseScorer
        """
        self.index = index
        self.model = model
    
    def retrieve(self, query, k=None):
        results = self.index.retrieve(query)
        docs = []
        for res in results:
            with open(os.path.join(DOC_PROCESS_DIR, res)) as f:
                docs.append(Document(f))
        if isinstance(query, str):
            query = Query(query)
        docs = self.rank(query, docs)
        if k is None:
            return docs
        else:
            return docs[:k]
    
    def score(self, q, d):
        return self.model.get_score(q, d)
    
    def rank(self, q, doclist):
        return sorted(doclist, key=lambda d: self.score(q, d), reverse=True)
