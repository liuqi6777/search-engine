import json


class Document:
    """
    Store useful information of a document. 
    """
    def __init__(self, fp=None):
        self.doc_id = None
        self.url = ''
        self.title = None
        self.headers = None
        self.body_length = 0
        self.pagerank = 0
        self.anchors = None
        
        if fp is not None:
            self.load(fp)
        
    def __str__(self):
        return self.url
    
    __repr__ = __str__
    
    def load(self, fp):
        doc_info = json.load(fp)
        self.doc_id = doc_info['doc_id']
        self.url = doc_info['url']
        self.title = doc_info['title']
        self.body = doc_info['body']
        self.title_tf = doc_info['title-tf']
        self.body_tf = doc_info['body-tf']
        self.length = doc_info['dl']        
