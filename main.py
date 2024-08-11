from init import *
import utils.documents as documents
import utils.str_consts as sconst
from git import Repo
from utils.funcs import get_doc_list
from flask_login import login_required, current_user
from login import login, logout

# 클라이언트에 현재 문서의 hash를 주고, 해당 해쉬로 checkout 해서 브랜치 만들고, 
# 그 브랜치에서 수정 내용 반영해서 main 브랜치에 반영 후 push
@app.route("/getdoc/<string:doc_name>&<string:doc_hash>", methods=['GET'])
@app.route("/getdoc/<string:doc_name>", methods=['GET'])
def get_doc(doc_name : str, doc_hash: str=None):
    return documents.get(doc_name, doc_hash)


@app.route("/editdoc/<string:doc_name>", methods=['GET', "POST"])
@login_required
def edit_doc(doc_name : str):
    if request.method == 'GET':
        return sconst.INVALID_ACCESS

    res = request.get_json()
    return documents.edit(doc_name, res["content"], current_user.user_id, res["hash"])

@app.route("/deletedoc/<string:doc_name>", methods=["GET", "POST"])
@login_required
def delete_doc(doc_name : str):
    if request.method == 'GET':
        return sconst.INVALID_ACCESS

    res = request.get_json()
    return documents.edit(doc_name, sconst.DOC_DELETED, current_user.user_id, res["hash"])

@app.route("/adddoc/<string:doc_name>", methods=['GET', 'POST'])
@login_required
def add_doc(doc_name : str):
    if request.method == 'GET':
        return sconst.INVALID_ACCESS

    res = request.get_json()
    com_res = documents.add(doc_name, res, current_user.user_id)
    return com_res

@app.route("/gethistory/<string:doc_name>&<int:start>&<int:end>")
def get_history(doc_name, start, end):
    return documents.get_history(doc_name, start, end)

@app.route("/")
# @login_required
def main():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")