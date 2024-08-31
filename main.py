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


@app.route("/")
# @login_required
def main():
    '''
    메인 페이지 접속 시 html 전송
    '''
    return render_template("index.html")


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

        # 권한 확인
        if dbcon.check_permission(doc_name, current_user.user_type) is False:
            return dict(status=sconst.NO_PERMISSION)


        res = request.get_json()
        return documents.edit(doc_name, res["content"], current_user.user_id, res["hash"], res["redirections"], res["doc_title"])

    @staticmethod
    @app.route("/deletedoc/<string:doc_name>", methods=["GET", "POST"])
    @login_required
    def delete_doc(doc_name : str):
        if request.method == 'GET':
            return sconst.INVALID_ACCESS

        if dbcon.check_permission(doc_name, current_user.user_type) is False:
            return dict(status=sconst.NO_PERMISSION)


        res = request.get_json()
        return documents.edit(doc_name, sconst.DOC_DELETED, current_user.user_id, res["hash"])

    @staticmethod
    @app.route("/adddoc/<string:doc_name>", methods=['GET', 'POST'])
    @login_required
    def add_doc(doc_name : str):
        if request.method == 'GET':
            return sconst.INVALID_ACCESS

        if dbcon.check_permission(doc_name, current_user.user_type) is False:
            return dict(status=sconst.NO_PERMISSION)


        res = request.get_json()
        com_res = documents.add(doc_name, res, current_user.user_id)
        return com_res

    @staticmethod
    @app.route("/gethistory/<string:doc_name>&<int:start>&<int:end>")
    def get_history(doc_name, start, end):
        return documents.get_history(doc_name, start, end)


class ImageApi:

    @staticmethod
    @app.route("/addimage/<string:image_name>", methods=['GET', 'POST'])
    @login_required
    def add_image(image_name):
        if request.method == 'GET':
            return sconst.INVALID_ACCESS
        
        if dbcon.check_permission(image_name, current_user.user_type) is False:
            return dict(status=sconst.NO_PERMISSION)

        if 'file' not in request.files:
            return dict(status=sconst.NO_FILE)
        
        file = request.files['file']
        return images.add(image_name, file)
    
    @staticmethod
    @app.route("/deleteimage/<string:image_name>", methods=['GET'])
    @login_required
    def delete_image(image_name):
        if dbcon.check_permission(image_name, current_user.user_type) is False:
            return dict(status=sconst.NO_PERMISSION)
        
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