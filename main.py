from init import *
import utils.documents as documents
import utils.images as images
import utils.str_consts as sconst
import utils.db as dbcon
import utils.search as search
from git import Repo
from utils.funcs import get_doc_list
from flask_login import login_required, current_user
import login
import env
import utils.perms


@app.route("/")
# @login_required
def main():
    '''
    메인 페이지 접속 시 html 전송
    '''
    return render_template("index.html")

@app.route("/" + env.GOOGLE_SITE_VERIFICATION)
def google_cert():
    return render_template(env.GOOGLE_SITE_VERIFICATION)


class DocApi:
    '''
    문서 조작과 관련된 API 클래스
    '''
    # 클라이언트에 현재 문서의 hash를 주고, 해당 해쉬로 checkout 해서 브랜치 만들고, 
    # 그 브랜치에서 수정 내용 반영해서 main 브랜치에 반영 후 push
    @staticmethod
    @app.route("/getdoc/<string:doc_name>&<string:doc_hash>", methods=['GET'])
    @app.route("/getdoc/<string:doc_name>", methods=['GET'])
    def get_doc(doc_name : str, doc_hash: str=None):
        return documents.get(doc_name, doc_hash)

    @staticmethod
    @app.route("/editdoc/<string:doc_name>", methods=['GET', "POST"])
    @login_required
    def edit_doc(doc_name : str):
        if request.method == 'GET':
            return sconst.INVALID_ACCESS

        res = request.get_json()
        redirect_check = dbcon.check_redirections(doc_name)
        if (redirect_check[0]):
            doc_name = redirect_check[1]
            edited_doc_title = doc_name
            return documents.edit(doc_name, res["content"], current_user.user_id, res["hash"], res["redirections"], edited_doc_title)

        else:
            return documents.edit(doc_name, res["content"], current_user.user_id, res["hash"], res["redirections"], res["doc_title"])

    @staticmethod
    @app.route("/deletedoc/<string:doc_name>", methods=["GET", "POST"])
    @login_required
    def delete_doc(doc_name : str):
        if request.method == 'GET':
            return sconst.INVALID_ACCESS

        res = request.get_json()
        return documents.edit(doc_name, sconst.DOC_DELETED, current_user.user_id, res["hash"])

    @staticmethod
    @app.route("/adddoc/<string:doc_name>", methods=['GET', 'POST'])
    @login_required
    def add_doc(doc_name : str):
        if request.method == 'GET':
            return dict(status=sconst.INVALID_ACCESS)

        res = request.get_json()
        return documents.add(doc_name, res, current_user.user_id)

    @staticmethod
    @app.route("/gethistory/<string:doc_name>&<int:start>&<int:end>")
    def get_history(doc_name, start, end):
        return documents.get_history(doc_name, start, end)
    
    @staticmethod
    @app.route("/diff/<string:doc_name>&<string:hash1>&<string:hash2>")
    def get_diff(doc_name, hash1, hash2):
        return documents.diff(doc_name, hash1, hash2)
    
    @staticmethod
    @login_required
    @app.route("/deletedoc/perm/<string:doc_name>")
    def delete_doc_perm(doc_name):
        if (not utils.perms.check_perm(current_user, "document", "REMOVE_PERMANENT")):
            return dict(status=sconst.NO_PERMISSION)
        
        return documents.delete_perm(doc_name)


class ImageApi:

    @staticmethod
    @app.route("/addimage/<string:image_name>", methods=['GET', 'POST'])
    @login_required
    def add_image(image_name):
        if request.method == 'GET':
            return sconst.INVALID_ACCESS
        
        if 'file' not in request.files:
            return dict(status=sconst.NO_FILE)
        
        file = request.files['file']
        return images.add(image_name, file)
    
    @staticmethod
    @app.route("/deleteimage/<string:image_name>", methods=['GET'])
    @login_required
    def delete_image(image_name):
        return images.delete(image_name)

    @staticmethod
    @app.route("/getimage/<string:image_name>", methods=['GET'])
    def get_image(image_name):
        return images.get(image_name)
    
class SearchApi:
    @staticmethod
    @app.route("/search/<string:to_search>", methods=['GET'])
    def search(to_search):
        return search.search(to_search)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
    # app.run(debug=True, port="5000")