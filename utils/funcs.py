import os

def get_doc_list(path):
    res = os.listdir(path)
    docs = set(res)
    return docs
