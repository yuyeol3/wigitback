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

def add(doc_name, content):
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

    except Exception as err:
        print(err)
        return sconst.UNKNOWN_ERROR
    
    return sconst.SUCCESS
 

def edit(doc_name, content, doc_hash):
    if (doc_name in get_doc_list("./edits")):
        return {"status":sconst.DOC_EDIT_IN_PROGRESS}

    try:
        repo = Repo.clone_from("./documents/" + doc_name, "./edits/" + doc_name)
        repo.git.checkout(doc_hash)

        originRepo = Repo("documents/" + doc_name)
        originRepo.git.config('receive.denyCurrentBranch', 'warn')

        new_branch = repo.create_head("edit_branch")
        new_branch.checkout()

        with open("./edits/" + doc_name + "/README.md", "w", encoding="utf8") as f:
            f.write(content)

        repo.index.add("README.md")
        repo.index.commit(f"update {doc_name}")

        repo.heads.main.checkout()
        repo.git.merge('edit_branch')

        repo.delete_head("edit_branch", force=True)
        repo.remotes[0].push(force=True) 

        originRepo.git.reset("--hard")        

    except GitCommandError as err:
        print(err)
        to_return =  { "status" : "merge conflict" }

        with open("./edits/" + doc_name + "/README.md", "r", encoding="utf8") as f:
            to_return["content"] = f.read()

        return to_return
    
    except Exception as err:
        traceback.print_exc()
        {"status" : sconst.UNKNOWN_ERROR}

    finally:
        repo.close()
        _rmrepo(f"./edits/{doc_name}")
        # shutil.rmtree(f"./edits/{doc_name}/.git", ignore_errors=False )
        # shutil.rmtree("./edits/" + doc_name, ignore_errors=False )




    return {"status" : sconst.SUCCESS}