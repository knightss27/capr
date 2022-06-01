# CAPR - Server

The server comprises three central linguistic tasks:
- Compiling pipeline outputs into JSON for the Svelte interface.
- "Refishing" new cognates after transducer/board improvements.
- Comparing transducers for use with the FST editor / debugger.

Each of these tasks are accomplished with code found in their respective files:
- `compile_lexicon_to_json.py`
- `refish.py`
- `compare_fst.py`

And found at the respective routes for the server:
| Route | Method | Request Body | Response |
| :---- | :----- | :----------- | :------- |
| /new-board | GET | | `{ boards, columns, currentBoard, fstIndex, maxColumn, searchColumns, syllables, words, fstDoculects, fstDown, fstUp }` |
| /refish-board | POST | `{ columns, boards, transducer }` | `{ columns, boards }` |
| /compare-fst | POST | `{ langsUnderStudy, oldTransducer, newTransducer, board }` | `{ chapters, missing_transducers, errors }` |

If you are trying to use the API by itself, please reference the Svelte code (i.e. [this](https://github.com/knightss27/capr/blob/0ca6fe5d063f4f297487b9aa34ac66a3dedf0a24/cognate-app/src/App.svelte#L49)) to see what types of data should be sent.

To run, you will likely need to install (via `pip`) `lingpy, lingrex, lexibase, flask`
.

To run for development:
```
export FLASK_APP=server
flask run
```

To run for production (you will have to install `gunicorn`):
```
gunicorn server:app
```