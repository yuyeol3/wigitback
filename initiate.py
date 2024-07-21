import os

def get_doc_list():
    res = os.listdir("documents")
    docs = set(res)
    return docs