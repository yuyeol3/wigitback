from init import *
import utils.documents as documents
from git import Repo
from utils.funcs import get_doc_list
from flask_login import login_required
from login import login, logout

# 클라이언트에 현재 문서의 hash를 주고, 해당 해쉬로 checkout 해서 브랜치 만들고, 
# 그 브랜치에서 수정 내용 반영해서 main 브랜치에 반영 후 push
@app.route("/getdoc/<string:doc_name>", methods=['GET'])
def get_doc(doc_name : str):
    docs = get_doc_list("./documents")
    if (doc_name == "" or doc_name not in docs):
        return {"hash":"", "content":"doc-not-exist"}
    
    target_doc_repo = Repo(f"./documents/{doc_name}")
    head_commit = target_doc_repo.head.commit
    commit_hash = head_commit.hexsha

    with open(f"./documents/{doc_name}/README.md", "r", encoding="utf8") as f:
        res = f.read()
        # res = json.dumps(res)
        return {"hash":commit_hash,"content":res}


@app.route("/editdoc/<string:doc_name>", methods=['GET', "POST"])
@login_required
def edit_doc(doc_name : str):
    if request.method == 'GET':
        return "Invalid Access"

    res = request.get_json()
    print(res)
    return documents.edit(doc_name, res["content"], res["hash"])


@app.route("/adddoc/<string:doc_name>", methods=['GET', 'POST'])
def add_doc(doc_name : str):
    if request.method == 'GET':
        return "Invalid Access"

    res = request.get_json()
    print(res)
    com_res = documents.add(doc_name, res)
    return com_res

@app.route("/")
# @login_required
def main():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")