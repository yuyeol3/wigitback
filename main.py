from flask import Flask, render_template, url_for, request, redirect
import mimetypes
from initiate import get_doc_list
import json
import documents


mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

app = Flask(__name__, static_folder="assets", template_folder="./")

@app.route("/")
def main():
    return render_template("index.html")

# 클라이언트에 현재 문서의 hash를 주고, 해당 해쉬로 checkout 해서 브랜치 만들고, 
# 그 브랜치에서 수정 내용 반영해서 main 브랜치에 반영 후 push
@app.route("/getdoc/<string:doc_name>", methods=['GET'])
def get_doc(doc_name : str):
    docs = get_doc_list("./documents")
    if (doc_name == "" or doc_name not in docs):
        return ""
    
    with open(f"documents/{doc_name}/README.md", "r", encoding="utf8") as f:
        res = f.read()
        # res = json.dumps(res)
        return res

@app.route("/editdoc/<string:doc_name>", methods=['GET', "POST"])
def edit_doc(doc_name : str):
    if request.method == 'GET':
        return "Invalid Access"

    res = request.get_json()
    print(res)
    return "Success"

@app.route("/adddoc/<string:doc_name>", methods=['GET', 'POST'])
def add_doc(doc_name : str):
    if request.method == 'GET':
        return "Invalid Access"

    res = request.get_json()
    print(res)
    com_res = documents.add(doc_name, res)
    return com_res


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")