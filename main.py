from flask import Flask, render_template, url_for, request, redirect
import mimetypes
from initiate import get_doc_list
import json

DOCS = get_doc_list()

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

app = Flask(__name__, static_folder="assets", template_folder="./")

@app.route("/")
def main():
    return render_template("index.html")


@app.route("/getdoc/<string:doc_name>", methods=['GET'])
def get_doc(doc_name : str):
    global DOCS
    DOCS = get_doc_list()
    if (doc_name == "" or doc_name not in DOCS):
        return redirect("/")
    
    with open(f"documents/{doc_name}/README.md", "r", encoding="utf8") as f:
        res = f.read()
        res = json.dumps(res)
        return res


if __name__ == "__main__":
    app.run(debug=False, port="5000")