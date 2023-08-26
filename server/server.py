from os import abort
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from functools import wraps
from compile_lexicon_to_json import compile_to_json, compile_to_json_full_cognates
from refish import refish
from compare_fst import compare_fst

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


# /new-board gives us the compiled format of our source material after it has been run through Lexstat
@app.route("/new-board")
def new_board():
    return compile_to_json_full_cognates("./pipeline/output/germanic/stage3/germanic-aligned-final.tsv")
    # return compile_to_json("./pipeline/output/burmish-pipeline/stage2/burmish-aligned-final.tsv")


# /refish-board returns the output of the refishing algorithm for cognate reassignment 
@app.route("/refish-board", methods=["POST"])
@with_json("columns", "boards", "syllables", "fstDoculects", "transducer")
def refish_board(json_body):
    if (json_body['transducer'] == 'internal'):
        del json_body['transducer']

    new_board = refish(json_body)
    return new_board


# /compare-fst returns the correspondence patterns for the transducer interface
@app.route("/compare-fst", methods=["POST"])
@with_json("langsUnderStudy", "oldTransducer", "newTransducer", "board")
def compare(json_body):
    print(json_body['langsUnderStudy'])
    return compare_fst(json_body)
