from .funcs import get_doc_list
import utils.str_consts as sconst
import traceback

def search(to_search):
    try :
        to_search = to_search.lower()
        to_search = to_search.replace(" ", "")
        documents = get_doc_list("./documents")
        images = get_doc_list("./assets/images")
        images = ["image::"+ i.split(".")[0] for i in images]

        matched = []
        for title in documents:
            if to_search in title.lower().replace(" ", ""):
                matched.append(title)

        for title in images:
            if to_search in title.lower().replace(" ", ""):
                matched.append(title)

        return dict(status=sconst.SUCCESS, content=matched)
    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)
    