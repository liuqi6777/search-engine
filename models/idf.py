import os
import pickle as pkl
import math


class Idf:
    def __init__(self, index_dir):
        """Build an idf dictionary"""
        try:
            with open(os.path.join(index_dir, "docs.dict"), 'rb') as f:
                docs = pkl.load(f)
            self.total_doc_num = len(docs)
            print("Total Number of Docs is", self.total_doc_num)

            with open(os.path.join(index_dir, "terms.dict"), 'rb') as f:
                terms = pkl.load(f)
            self.total_term_num = len(terms)
            print("Total Number of Terms is", self.total_term_num)

            with open(os.path.join(index_dir, 'BSBI.dict'), 'rb') as f:
                self.postings_dict, termsID = pkl.load(f)

            self.idf = {}
            for term_id in termsID:
                self.idf[term_id] = self._idf_func(term_id)
        except FileNotFoundError:
            print("doc_dict_file / term_dict_file Not Found!")

    def get_idf(self, term = None):
        """Return idf of return idf of a term, whether in or not in built dictionary.
        Args:
            term(str) : term to return its idf
        Return(float): 
            idf of the term
        """
        return self.idf.get(term, 0)
    
    def _idf_func(self, term_id):
        return math.log(self.total_doc_num / self.postings_dict[term_id][1])
    
    
class BM25Idf(Idf):
    def _idf_func(self, term_id):
        N = self.total_doc_num
        n_q = self.postings_dict[term_id][1]
        return math.log((N - n_q + 0.5) / (n_q + 0.5) + 1)
