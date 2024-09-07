from git import Repo, GitCommandError
import os
from utils.funcs import get_doc_list
import utils.str_consts as sconst
import utils.db as dbcon
import shutil
import traceback
import subprocess
import stat
from os import path
from flask_login import current_user
import bleach
from bleach.css_sanitizer import CSSSanitizer

# 레포 제거
def _rmrepo(target_path):
    for root, dirs, files in os.walk(target_path):  
        for dir in dirs:
            os.chmod(path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(path.join(root, file), stat.S_IRWXU)
    shutil.rmtree(target_path)


# 문서 읽어오기
def _getdoc(doc_name, doc_location):
    with open(f"./{doc_location}/{doc_name}/README.md", "r", encoding="utf8") as f:
        res = f.read()
        return res

# 문서 쓰기
def _writedoc(doc_name, doc_location, content):
    allowed_html_tags = [
        'table',
        'tr',
        'td',
        'thead',
        'tbody',
        'tfoot',
        'span',
        'a',
        'b',
        'code',
        'img',
        'svg',
        "path",
        "line",
        "rect",
        "circle",
        "sup",
        'blockquote'
    ]
    allowed_attributes = {
        'table': ['border', 'cellspacing', 'cellpadding', 'width', 'height'],
        'tr': ['align', 'valign', 'style'],
        'td': ['colspan', 'rowspan', 'align', 'valign', 'style', 'width', 'height'],
        'span': ['style', 'class'],
        'a': ['title', 'target', 'rel', 'name'],
        'b': [],  # 속성 허용하지 않음 (기본 텍스트 스타일 태그)
        'code': ['class'],  # 코드 블록에 클래스 적용 가능
        'img': ['src', 'alt', 'width', 'height', 'title'],
        'svg': ['width', 'height', 'viewBox', 'xmlns'],
        'path': ['d', 'fill', 'stroke', 'stroke-width'],
        'line': ['x1', 'x2', 'y1', 'y2', 'stroke', 'stroke-width'],
        'rect': ['x', 'y', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'rx', 'ry'],
        'circle': ['cx', 'cy', 'r', 'fill', 'stroke', 'stroke-width']
    }
    allowed_css_properties = [
        'color', 'font-size', 'font-weight', 'text-align', 'background-color',
        'width', 'height', 'border', 'padding', 'margin'
    ]
    css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_css_properties)

    with open(f"{doc_location}/{doc_name}/README.md", "w", encoding="utf8") as f:
        f.write(bleach.clean( 
            content , 
            tags=allowed_html_tags, 
            attributes=allowed_attributes, 
            css_sanitizer=css_sanitizer,
        
        ))



def _movedoc(pathsrc, pathdest):
    if (os.path.exists(pathdest)):
        return False
    
    try:
        shutil.copytree(pathsrc, pathdest)

        return True
    except Exception as err:
        traceback.print_exc()
        return False
    


def get(doc_name, doc_hash=None):
    redirect_check = dbcon.check_redirections(doc_name)
    if (redirect_check[0]):
        return dict(hash="", content=redirect_check[1], status=sconst.DOC_REDIRECT, doc_title=doc_name)
    
    docs = get_doc_list("./documents")
    if (doc_name == "" or doc_name not in docs):
        return dict(hash="", content="", status=sconst.DOC_NOT_EXIST)
    


    target_doc_repo = Repo(f"./documents/{doc_name}")
    head_commit = target_doc_repo.head.commit
    HEAD_HASH = head_commit.hexsha
    # 문서 해쉬가 지정되어 있지 않으면
    if (doc_hash is None):
        commit_hash = HEAD_HASH

        res = _getdoc(doc_name, "documents")
        if (res == sconst.DOC_DELETED): commit_hash = ""

        # 리다이렉션 목록 읽어오기
        redirections = ""
        if (".redirections" in get_doc_list(f"./documents/{doc_name}/")):  # .redirections 파일이 있는 경우에만 읽어오도록 하기
            with open(f"./documents/{doc_name}/.redirections", "r", encoding="utf8") as f:
                redirections = f.read()

        return dict(hash=commit_hash, content=res, status=sconst.SUCCESS, redirections=redirections, doc_title=doc_name, head_hash=HEAD_HASH)

    try:
        repo = Repo.clone_from("./documents/" + doc_name, "./edits/" + doc_name)
        repo.git.checkout(doc_hash)

        latest_content = _getdoc(doc_name, "documents")
        content = _getdoc(doc_name, "edits")
        if (latest_content == sconst.DOC_DELETED): doc_hash = ""

        redirections = ""
        if (".redirections" in get_doc_list(f"./edits/{doc_name}/")):  # .redirections 파일이 있는 경우에만 읽어오도록 하기
            with open(f"./edits/{doc_name}/.redirections", "r", encoding="utf8") as f:
                redirections = f.read()
        
        return dict(hash=doc_hash, content=content, status=sconst.SUCCESS, redirections=redirections, doc_title=doc_name, head_hash=HEAD_HASH)
        
    
    except Exception as err:
        traceback.print_exc()
        return dict(res="", status=sconst.UNKNOWN_ERROR)
    
    finally:
        _rmrepo(f"./edits/{doc_name}")
    

def add(doc_name, content, user_name):
    if (doc_name in get_doc_list("./documents")):
        return sconst.DOC_ALREADY_EXISTS

    try:
        doc_dir = "documents/" + doc_name
        os.mkdir(doc_dir)

        _writedoc(doc_name, "documents", content)

        abs_doc_dir = os.path.join(os.getcwd(), doc_dir)
        print(abs_doc_dir)


        command = [
            "git init",
            "git add .",
            "git commit -m \"FIRST COMMIT\""
        ]
        # 우분투인 경우 실행
        if (os.name == "posix"):
            command = [
                ["git", "init"],
                ["git", "add", "."],
                ["git", "commit", "-m", "FIRST COMMIT"]
            ]


        for cmd in command:
            subprocess.call(cmd, cwd=abs_doc_dir)

        edit(doc_name, content, user_name)

    except Exception as err:
        print(err)
        return dict(status=sconst.UNKNOWN_ERROR)
    
    return dict(status=sconst.SUCCESS)
 

def edit(doc_name, content, user_name, doc_hash=None, redirections=None, edited_doc_title=None):
    if (doc_name in get_doc_list("./edits")):
        return dict(status=sconst.DOC_EDIT_IN_PROGRESS)
    
    # 리다이렉션 문서인 경우 - 원본 문서가 편집되도록 하자

    redirect_check = dbcon.check_redirections(doc_name)
    if (redirect_check[0]):
        # 리다이렉션이면 원본 문서에 대한 권한 재확인해야 함
        if (dbcon.check_permission(redirect_check[1], current_user.user_type) is False):
            return dict(status=sconst.NO_PERMISSION)
        

        doc_name = redirect_check[1]
        edited_doc_title = doc_name

    # 이름 변경 처리부분
    DOC_NAME_CHANGING = False
    if (edited_doc_title is not None and doc_name != edited_doc_title):
        if (edited_doc_title not in get_doc_list("./documents") and 
            dbcon.check_redirections(edited_doc_title)[0] is not True
            ):
            # RM_TEMPFUNC = lambda : ""
            res = _movedoc(f"./documents/{doc_name}", f"./documents/{edited_doc_title}")

            # 성공한 경우
            if (res):
                to_remove = f"./documents/{doc_name}"
                RM_TEMPFUNC = lambda : _rmrepo(to_remove)  # 기본 문서 제거
                dbcon.update_redirections(doc_name, edited_doc_title)
                original_name_redirect = str(doc_name)
                redirections = str(doc_name) if redirections is None else redirections + "," + original_name_redirect
                doc_name = edited_doc_title
                DOC_NAME_CHANGING = True
        else:
            return dict(status=sconst.DOC_ALREADY_EXISTS)
    

    try:
        repo = Repo.clone_from("./documents/" + doc_name, "./edits/" + doc_name)
        
        if (doc_hash is not None and doc_hash != ""):
            repo.git.checkout(doc_hash)

        originRepo = Repo("documents/" + doc_name)
        originRepo.git.config('receive.denyCurrentBranch', 'warn')

        new_branch = repo.create_head("edit_branch")
        new_branch.checkout()

        _writedoc(doc_name, "edits", content)

        print(redirections)
        add_list = ["README.md", ".redirections"]
        if (redirections is not None):
            add_res = dbcon.add_redirections(doc_name, redirections)

            # 이름을 변경하는 중이면
            if (DOC_NAME_CHANGING):
                add_res.add(original_name_redirect)

            with open(f"./edits/{doc_name}/.redirections", "w", encoding="utf8") as f:
                f.write(",".join(add_res))
            
        else:
            with open(f"./edits/{doc_name}/.redirections", "w", encoding="utf8") as f:
                f.write("")

        repo.index.add(add_list)
        repo.index.commit(f"{user_name} updated {doc_name}")

        repo.heads.master.checkout()
        repo.git.merge('edit_branch')

        repo.delete_head("edit_branch", force=True)
        repo.remotes[0].push(force=True) 

        originRepo.git.reset("--hard")        

        dbcon.add_history(doc_name, user_name)

    except GitCommandError as err:
        print(err)
        to_return = dict(status=sconst.MERGE_CONFLICT)

        res = _getdoc(doc_name, "edits")
        to_return["content"] = res
        return to_return
    
    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)

    finally:
        repo.close()
        _rmrepo(f"./edits/{doc_name}")
        if (DOC_NAME_CHANGING):
            RM_TEMPFUNC()

    return dict(status=sconst.SUCCESS)

def get_history(doc_name, start=0, end=100):
    if (doc_name not in get_doc_list("./documents")):
        return dict(status=sconst.DOC_NOT_EXIST)
    
    try:
        repo = Repo("./documents/" + doc_name)
        commits = [
            dict(message=i.message, hash=i.hexsha, updated_time=i.committed_datetime)
            for i in repo.iter_commits('master')
        ]
        commits = commits[max(0, start):min(len(commits)-1, end)]

    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)

    finally:
        repo.close()

    return dict(status=sconst.SUCCESS, content=commits)

def diff(doc_name, hash1, hash2):
    if (doc_name not in get_doc_list("./documents")):
        return dict(status=sconst.DOC_NOT_EXIST)
    
    try:
        repo = Repo("./documents/" + doc_name)

        commit1 = repo.commit(hash1)
        commit2 = repo.commit(hash2)

        diff_content = repo.git.diff(commit1, commit2, "README.md")
        diff_content = diff_content.split("\n")

        return dict(status=sconst.SUCCESS, content=diff_content[4:])
        # print(diff_index)

        # for diff in diff_index.iter_change_type('M'):
        #     print("A blob:\n{}".format(diff.a_blob.data_stream.read().decode('utf-8')))
        #     print("B blob:\n{}".format(diff.b_blob.data_stream.read().decode('utf-8'))) 

        
    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)
    finally:
        repo.close()

    return dict(status=sconst.SUCCESS)