from threading import Thread
from git import Repo, GitCommandError
import os
from initiate import get_doc_list
import str_consts as sconst

def add(doc_name, content):
    if (doc_name in get_doc_list("./documents")):
        return sconst.DOC_ALREADY_EXISTS

    try:
        doc_dir = "./documents/" + doc_name
        os.mkdir(doc_dir)

        with open(doc_dir + "/README.md", "w", encoding="utf8") as f:
            f.write(content)

        repo = Repo.init(doc_dir)
        repo.index.add(os.listdir(doc_dir))
        repo.index.commit("FIRST COMMIT")

    except Exception as err:
        print(err)
        return sconst.UNKNOWN_ERROR
    
    return sconst.SUCCESS
 

def edit(doc_name, content):
    if (doc_name in get_doc_list("./edits")):
        return sconst.DOC_EDIT_IN_PROGRESS

    try:
        repo = Repo.clone_from("./documents/" + doc_name, "./edits/")

        new_branch = repo.create_head("edit_branch")
        new_branch.checkout()

        with open("./edits/" + doc_name + "/README.md", "w", encoding="utf8") as f:
            f.write(content)

        repo.index.add("README.md")
        commit_res = repo.index.commit(f"update {doc_name}")

        repo.heads.master.checkout()

        repo.git.merge('edit_branch')
    except GitCommandError as err:
        to_return =  {
            "status" : "merge conflict"
        }

        with open("./edits/" + doc_name + "/README.md", "r", encoding="utf8") as f:
            to_return["content"] = f.read()

        return to_return
    
    finally:
        os.rmdir("./edits/" + doc_name)

    return sconst.SUCCESS