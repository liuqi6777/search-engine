class Document:
    """
    Store useful information of a document. 
    """
    def __init__(self, url):
        self.url = url
        self.title = None
        self.headers = None
        self.body_length = 0
        self.pagerank = 0
        self.anchors = None
        
    def __str__(self):
        return self.url
    
    __repr__ = __str__
