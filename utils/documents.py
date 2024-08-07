from git import Repo, GitCommandError
import os
from utils.funcs import get_doc_list
import utils.str_consts as sconst
import shutil
import traceback
import subprocess
import stat
from os import path

def _rmrepo(target_path):
    for root, dirs, files in os.walk(target_path):  
        for dir in dirs:
            os.chmod(path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(path.join(root, file), stat.S_IRWXU)
    shutil.rmtree(target_path)

def get(doc_name, doc_hash=None):
    docs = get_doc_list("./documents")
    if (doc_name == "" or doc_name not in docs):
        return dict(hash="", content="", status=sconst.DOC_NOT_EXIST)
    

    if (doc_hash is None):
        target_doc_repo = Repo(f"./documents/{doc_name}")
        head_commit = target_doc_repo.head.commit
        commit_hash = head_commit.hexsha

        with open(f"./documents/{doc_name}/README.md", "r", encoding="utf8") as f:
            res = f.read()
            return dict(hash=commit_hash, content=res, status=sconst.SUCCESS)

    try:
        repo = Repo.clone_from("./documents/" + doc_name, "./edits/" + doc_name)
        repo.git.checkout(doc_hash)

        with open(f"./edits/{doc_name}/README.md", "r", encoding="utf8") as f:
            res = f.read()
            return dict(hash=doc_hash, content=res, status=sconst.SUCCESS)
    except Exception as err:
        traceback.print_exc()
        return dict(res="", status=sconst.UNKNOWN_ERROR)
    
    finally:
        _rmrepo(f"./edits/{doc_name}")
    
    


def add(doc_name, content, user_name):
    if (doc_name in get_doc_list("./documents")):
        return sconst.DOC_ALREADY_EXISTS

    try:
        doc_dir = "documents\\" + doc_name
        os.mkdir(doc_dir)

        with open(doc_dir + "/README.md", "w", encoding="utf8") as f:
            f.write(content)

        abs_doc_dir = os.path.join(os.getcwd(), doc_dir)
        print(abs_doc_dir)
        command = [
            "git init",
            "git add .",
            "git commit -m \"FIRST COMMIT\""
        ]

        for cmd in command:
            subprocess.call(cmd, cwd=abs_doc_dir)
        # print(return_code)
        # repo.index.add(os.listdir(doc_dir))
        # repo.index.commit("FIRST COMMIT")

        edit(doc_name, content, user_name)

    except Exception as err:
        print(err)
        return sconst.UNKNOWN_ERROR
    
    return sconst.SUCCESS
 

def edit(doc_name, content, user_name, doc_hash=None,):
    if (doc_name in get_doc_list("./edits")):
        return dict(status=sconst.DOC_EDIT_IN_PROGRESS)

    try:
        repo = Repo.clone_from("./documents/" + doc_name, "./edits/" + doc_name)
        
        if (doc_hash is not None and doc_hash != ""):
            repo.git.checkout(doc_hash)

        originRepo = Repo("documents/" + doc_name)
        originRepo.git.config('receive.denyCurrentBranch', 'warn')

        new_branch = repo.create_head("edit_branch")
        new_branch.checkout()

        with open("./edits/" + doc_name + "/README.md", "w", encoding="utf8") as f:
            f.write(content)

        repo.index.add("README.md")
        repo.index.commit(f"{user_name} updated {doc_name}")

        repo.heads.main.checkout()
        repo.git.merge('edit_branch')

        repo.delete_head("edit_branch", force=True)
        repo.remotes[0].push(force=True) 

        originRepo.git.reset("--hard")        

    except GitCommandError as err:
        print(err)
        to_return = dict(status=sconst.MERGE_CONFLICT)

        with open("./edits/" + doc_name + "/README.md", "r", encoding="utf8") as f:
            res = f.read()
            to_return["content"] = res
            print(res)

        return to_return
    
    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)

    finally:
        repo.close()
        _rmrepo(f"./edits/{doc_name}")
        # shutil.rmtree(f"./edits/{doc_name}/.git", ignore_errors=False )
        # shutil.rmtree("./edits/" + doc_name, ignore_errors=False )
    
    return dict(status=sconst.SUCCESS)

def get_history(doc_name, start=0, end=100):
    if (doc_name not in get_doc_list("./documents")):
        return sconst.DOC_NOT_EXIST
    
    try:
        repo = Repo("./documents/" + doc_name)
        commits = [dict(message=i.message, hash=i.hexsha) for i in repo.iter_commits('main')]
        commits = commits[max(0, start):min(len(commits)-1, end)]

    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)

    finally:
        repo.close()

    return dict(status=sconst.SUCCESS, content=commits)