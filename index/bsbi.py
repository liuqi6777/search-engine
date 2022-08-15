"""
Copy from *Stanford CS276: Information Retrieval and Web Search* Programming assignment #1
 - URL: https://web.stanford.edu/class/cs276/
"""


import contextlib
import heapq
import os
import sys
import pickle as pkl

sys.path.append('..')

import jieba

from utils.id_map import IdMap
from .inverted_index import InvertedIndexIterator, InvertedIndexWriter, InvertedIndexMapper


class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map(IdMap): For mapping terms to termIDs
    doc_id_map(IdMap): For mapping relative paths of documents to docIDs
    data_dir(str): Path to data
    output_dir(str): Path to output index files
    index_name(str): Name assigned to index
    postings_encoding: Encoding used for storing the postings.
        The default (None) implies UncompressedPostings
    """

    def __init__(self, data_dir, output_dir, index_name="BSBI", postings_encoding=None):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Store names of intermediate indices
        self.intermediate_indices = []

    def save(self):
        """Dumps doc_id_map and term_id_map into output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pkl.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pkl.dump(self.doc_id_map, f)

    def load(self):
        """Loads doc_id_map and term_id_map from output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
            self.term_id_map = pkl.load(f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
            self.doc_id_map = pkl.load(f)

    def index(self):
        """Base indexing code

        This function loops through the data directories,
        calls parse_block to parse the documents
        calls invert_write, which inverts each block and writes to a new index
        then saves the id maps and calls merge on the intermediate indices
        """
        for block_dir_relative in sorted(next(os.walk(self.data_dir))[1]):
            td_pairs = self.parse_block(block_dir_relative)
            index_id = 'index_' + block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, self.postings_encoding, self.output_dir) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
        self.save()
        with InvertedIndexWriter(self.index_name, self.postings_encoding, self.output_dir) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(InvertedIndexIterator(index_id, self.postings_encoding, self.output_dir))
                           for index_id in self.intermediate_indices]
                self.merge(indices, merged_index)

    def parse_block(self, block_dir_relative):
        """Parses a tokenized text file into termID-docID pairs

        Parameters
        ----------
        block_dir_relative : str
            Relative Path to the directory that contains the files for the block

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block

        Should use self.term_id_map and self.doc_id_map to get termIDs and docIDs.
        These persist across calls to parse_block
        """
        # Begin your code
        block_dir_absolute = self.data_dir + os.path.sep + block_dir_relative
        doc_list = sorted(os.listdir(block_dir_absolute))
        res = []
        for doc in doc_list:
            doc_id = self.doc_id_map[os.path.join(block_dir_relative, doc)]
            with open(os.path.join(block_dir_absolute, doc), 'r') as f:
                text = f.read().strip()
                for term in text.split():
                    res.append((self.term_id_map[term], doc_id))
        return res

    @staticmethod
    def invert_write(td_pairs, index):
        """Inverts td_pairs into postings_lists and writes them to the given index

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index on disk corresponding to the block
        """
        td_pairs = sorted(td_pairs)
        postings_lists = {}
        for term_id, doc_id in td_pairs:
            if term_id not in postings_lists.keys():
                postings_lists[term_id] = [doc_id]
            elif doc_id not in postings_lists[term_id]:
                postings_lists[term_id].append(doc_id)
        for term_id, postings_list in postings_lists.items():
            index.append(term_id, sorted(postings_list))

    @staticmethod
    def merge(indices, merged_index):
        """Merges multiple inverted indices into a single index

        Parameters
        ----------
        indices: List[InvertedIndexIterator]
            A list of InvertedIndexIterator objects, each representing an
            iterable inverted index for a block
        merged_index: InvertedIndexWriter
            An instance of InvertedIndexWriter object into which each merged
            postings list is written out one at a time
        """
        curr_term = -1
        curr_list = []
        for term_id, postings_list in heapq.merge(*indices, key=lambda x: x[0]):
            # print(self.term_id_map.id_to_str[term_id], term_id, postings_list)
            if term_id != curr_term:
                if curr_term != -1:
                    merged_index.append(curr_term, sorted(list(set(curr_list))))
                    # print(curr_term, sorted(list(set(curr_list))))
                curr_term = term_id
                curr_list = []
            curr_list += postings_list
        merged_index.append(curr_term, sorted(list(set(curr_list))))

    def retrieve(self, query):
        """Retrieves the documents corresponding to the conjunctive query
        
        Parameters
        ----------
        query: str
            Space separated list of query tokens
            
        Result
        ------
        List[str]
            Sorted list of documents which contains each of the query tokens. 
            Should be empty if no documents are found.
        
        Should NOT throw errors for terms not in corpus
        """
        if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
            self.load()

        queries = jieba.lcut(query.strip())
        if len(queries) == 0:
            return set()
        print(queries)
        term_ids = [self.term_id_map[q] for q in queries]
        with InvertedIndexMapper(self.index_name, directory=self.output_dir, 
                                 postings_encoding=self.postings_encoding) as mapper:
            ret = set()
            for i in range(len(term_ids)):
                ret = ret | set(mapper[term_ids[i]])
        return [self.doc_id_map[x] for x in ret]
        
        
if __name__ == '__main__':
    from config import *
    BSBI_instance = BSBIIndex(data_dir='../'+DOC_TEXT_DIR, output_dir='../'+INDEX_DIR)
    BSBI_instance.index()
