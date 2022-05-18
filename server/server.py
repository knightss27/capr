from flask import Flask, jsonify
from compile_lexicon_to_json import compile_to_json

app = Flask(__name__)

@app.route("/")
def hello_world():
    return jsonify(compile_to_json("../output/burmish-pipeline/stage2/burmish-stage2-tmp-merged.tsv"))