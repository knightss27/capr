import os
from os.path import isfile, join
from flask import Flask, Response, jsonify, request, abort
from flask_cors import CORS
from functools import wraps
from compile_lexicon_to_json import compile_to_json, compile_to_json_full_cognates
from refish import refish
from compare_fst import compare_fst
import glob

app = Flask(__name__)
CORS(app)

def _resp(success: bool, message: str, data: object = None):
    """
    Return a JSON API response
    :param success: did the request succeed?
    :param message: what happened?
    :param data: any application specific data
    """

    return Response({
        "meta": {
            "success": success,
            "message": message
        },
        "data": data
    }, mimetype="application/json")

def with_json(*outer_args):
    """
    Get JSON API request body
    :param outer_args: *args (str) of JSON keys
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _json_body = {}
            for arg in outer_args:
                if not request.json:
                    return _resp(False, "JSON body must not be empty")
                val = request.json.get(arg)
                if val != None and val != "":
                    _json_body[arg] = val
                else:
                    return _resp(False, "Required argument " + arg + " is not defined.")
            return func(*args, **kwargs, json_body=_json_body)

        return wrapper

    return decorator

# /list-inputs returns all input file names
@app.route("/list-inputs")
def list_inputs():
    files = [f.split("/")[-1] for f in glob.glob("/usr/app/data/*.tsv")]
    return {"inputs": files}

# /get-transducers will return the text of a transducer file if it exists with
# the given name in /fsts
@app.route("/get-transducers", methods=["POST"])
@with_json("name")
def get_transducer(json_body):
    files = [f.split("/")[-1] for f in glob.glob("/usr/app/fsts/*.txt")]
    
    new_transducer = ""
    if json_body["name"] in files:
        new_transducer = ""
        with open(os.path.join("/usr/app/fsts/", json_body["name"]), encoding="utf-8") as fst_file:
            new_transducer = fst_file.read()
    return {
        "name": json_body["name"],
        "transducer": new_transducer
        }

# /new-board gives us the compiled format of our source material after it has been run through Lexstat
@app.route("/new-board", methods=["POST"])
@with_json("dataPath", "transducer")
def new_board(json_body):
    if json_body["dataPath"]:
        return compile_to_json_full_cognates(json_body["dataPath"], json_body["transducer"])

    return compile_to_json_full_cognates("./pipeline/output/germanic/stage3/germanic-aligned-final.tsv")

# /refish-board returns the output of the refishing algorithm for cognate reassignment 
@app.route("/refish-board", methods=["POST"])
@with_json("columns", "boards", "syllables", "fstDoculects", "transducer")
def refish_board(json_body):
    if (json_body['transducer'] == 'internal'):
        del json_body['transducer']

    board = refish(json_body)
    return board


# /compare-fst returns the correspondence patterns for the transducer interface
@app.route("/compare-fst", methods=["POST"])
@with_json("langsUnderStudy", "oldTransducer", "newTransducer", "board")
def compare(json_body):
    print(json_body['langsUnderStudy'])
    return compare_fst(json_body)
