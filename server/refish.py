#!/usr/bin/python

## Single # = Xun Gong's notes
## Double ## = Seth Knights's notes

## For disabling eprints that are unecessary
production = True

# Constants
language_title = {
    "Old_Burmese": "OBurm",
    "Achang_Longchuan": "Acha-LC",
    "Xiandao": "Acha-XD",
    "Maru": "Maru",
    "Bola": "Bola",
    "Atsi": "Atsi",
    "Lashi": "Lashi",
}
fst_index = {
    "Old_Burmese": "burmese",
    "Achang_Longchuan": "ngochang",
    "Xiandao": "xiandao",
    "Maru": "maru",
    "Bola": "bola",
    "Atsi": "atsi",
    "Lashi": "lashi",
}

# Basic imports
import sys
import re
import json
import csv
from functools import reduce
from collections import Counter
from tabulate import tabulate

##### ROUTINES #####


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()


# Replace unicode diacritics with ASCII equivalents for sending to the transducers
UNICODE_MACRON_UNDER = " ̱ "[1]
UNICODE_TILDE_OVER = " ̃"[1]


def replace_diacritics_up(s):
    return (
        s.replace(UNICODE_MACRON_UNDER, "_")
        .replace(UNICODE_TILDE_OVER, "~")
        .replace("_~", "~_")
    )


def replace_diacritics_down(s):
    return s.replace("_", UNICODE_MACRON_UNDER).replace("~", UNICODE_TILDE_OVER)


# Convert a piece of text to its component syllables
# If there is alrady "◦" or a space, use it to separate them
# Otherwise, separate the tone letters other letters
def syllabize(text):
    split_result = re.split(r"([ ◦¹²³⁴⁵˩˨˧˦˥]+)", text)
    l = len(split_result)

    # There are two possibilities
    # 'a◦b◦' → ['a', '◦', 'b', '◦', '']
    # 'a◦b' → ['a', '◦', 'b']
    # Both of them are odd, but should be treated differently
    # At least, everything but the last can be done in the same way
    # (5-1)/2 = 2

    result = []
    for i in range((l - 1) // 2):
        result.append(split_result[i * 2] + split_result[i * 2 + 1].strip("◦ "))
    # If last non-zero, then copy to result
    if split_result[l - 1]:
        result.append(split_result[l - 1])

    return result


def emphasize_syllable_raw(
    syllables, syllable_index, usual_formatting=None, emphatic_formatting=None
):
    l = len(syllables)
    result = ""
    for i in range(l):
        if i == syllable_index:
            result = result + (emphatic_formatting or "<%s>") % syllables[i]
        else:
            result = result + (usual_formatting or "%s") % syllables[i]
    return result


# emphasize_syllable("mi ma mu", 1) → "mi<ma>mu"
def emphasize_syllable(
    text, syllable_index, usual_formatting=None, emphatic_formatting=None
):
    return emphasize_syllable_raw(
        syllabize(text), syllable_index, usual_formatting, emphatic_formatting
    )


# fetch_syllable("mi ma mu", 1) → "ma"
def fetch_syllable(text, syllable_index):
    syllables = syllabize(text)
    return syllables[syllable_index]


# Convert internal language name to printed name
def print_language_name(name):
    if name == "Old_Burmese":
        return "OBur."
    else:
        return name.replace("_", r"\_")


# Compute the projected reconstruction from a bunch of syllable_id's and a certain fst
# syllable_ids: syllable_id's of the syllables in a class, as defined contra "words"
# fsts: different sets of fst
# words: given here in order not to abuse global variables
# Return values: (inferred_reconstructions, strict)
def back_reconstruct_list(syllable_ids, fsts, words):
    reconsts = {}
    at_least_one = False
    first_form = False

    for syllable_id in syllable_ids:
        word_id, _, n = syllable_id.rpartition("-")
        n = int(n)
        ipa = words[word_id]["syllables"][n]
        doculect = words[word_id]["doculect"]

        if not first_form:
            first_form = ipa
        if doculect in fsts:
            the_syl = replace_diacritics(ipa)
            rec = list(fsts[doculect].apply_up(the_syl))
            if rec:
                # only record reconstructions when something *is* reconstructed
                at_least_one = True
                if doculect not in reconsts:
                    reconsts[doculect] = set(rec)
                else:
                    reconsts[doculect] = reconsts[doculect].union(set(rec))

    strict = True
    inferred_reconstructions = []

    if at_least_one:
        strict = True
        inferred_reconstructions = list(set.intersection(*reconsts.values()))

        if not inferred_reconstructions:
            strict = False
            # kinda lenient way of generating reconstructions
            # try and make intersection of every pair of doculects
            pairwise_intersections = [
                set.intersection(reconsts[a], reconsts[b])
                for a in reconsts
                for b in reconsts
                if a != b
            ]
            if pairwise_intersections:
                inferred_reconstructions = list(set.union(*pairwise_intersections))
            else:
                inferred_reconstructions = []

    return (inferred_reconstructions, strict)


##### MAIN PROGRAM #####

import argparse

# Compile transducers
from foma import FST
import tempfile
import os
import subprocess

from disjointset import DisjointSet


def refish(jsonfile, csvfile="lexicon.tsv", fstfile="refishing-fst.txt"):
    # Board from JSON
    script_path = os.path.dirname(os.path.realpath(__file__))

    fsts_new = {}
    new_transducer = ""

    eprint("Processing json input...")
    if isinstance(jsonfile, dict):
        eprint("Parsing board as inputted JSON")

        if "transducer" in jsonfile:
            eprint("Using user provided transducer")
            new_transducer = jsonfile["transducer"]
        else:
            eprint("Using default transducer")
            with open(fstfile) as fst_file:
                new_transducer = fst_file.read()

        input_board = jsonfile
    else:
        eprint("Parsing board as file")
        input_board = json.load(open(jsonfile, "r+"))

        # Read and compile the FST
        with open(fstfile) as fst_file:
            new_transducer = fst_file.read()

    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        eprint("Compiling FSTs (new)")
        with open("transducer.foma", "w") as fp:
            fp.write(new_transducer)
        output = subprocess.check_output(["foma", "-f", "transducer.foma"]).decode(
            "UTF-8"
        )
        eprint("\n".join(output.split("\n")[-5:]))
        for doculect_name in fst_index:
            if os.path.isfile(fst_index[doculect_name] + ".bin"):
                fsts_new[doculect_name] = FST.load(fst_index[doculect_name] + ".bin")
        os.chdir(script_path)
        eprint("FSTs loaded:", ", ".join(fsts_new))

    # read the word CSV
    input_syllables = {}

    # import fileinput
    def process_row(row):
        if row["ID"].startswith("#"):
            # internal to lingpy
            return

        word_id = "word-" + row["ID"]
        sylls = syllabize(row["IPA"])

        # Now we can loop on each syllable in the language
        for syl in range(len(sylls)):
            # Put new information into crossid data
            syllable_id = word_id + "-" + str(syl)
            syllable_row = {
                "id": syllable_id,
                "doculect": row["DOCULECT"],
                "syllable": sylls[syl],
                "glossid": row["GLOSSID"],
            }
            input_syllables[syllable_id] = syllable_row

    with open(fstfile) as csv_file:
        csvreader = csv.DictReader(
            filter(lambda row: row.strip() and row[0] != "#", open(csvfile, "r")),
            dialect="excel-tab",
        )
        eprint("Processing TSV rows...")
        words = {}
        for row in csvreader:
            process_row(row)

    old_columns = input_board["columns"]
    old_boards = input_board["boards"]

    json_boards = {}  # new ones to be produced

    # Before we begin, it's useful to compile a reverse index, detailing to which board a certain column belongs in the old
    old_board_of_column = dict()
    new_board_of_column = dict()

    for board_id in old_boards:
        for column_id in old_boards[board_id]["columnIds"]:
            old_board_of_column[column_id] = board_id

    # Let's try and take a look at the whole thing first
    # json.dump(old_board_of_column, sys.stdout, indent=2)

    ### FIRST ROUND FISHING
    # Use strict cognacy-semantic relations to merge columns together
    # If two columns share something with the same reconstruction & same glossid, they should be merged tout court

    # We first use a disjoint set to compute the transitive closure of the relationship "share a strict etymon somehow not recognized by lingpy"
    ds_round1 = DisjointSet()
    first_column_of_gr = {}  # indexed by (glossid, reconstruction)

    # We process each cognate set with ID "column_id"
    for column_id in input_board["columns"]:
        ds_round1.add(column_id, column_id)

        for syllable_id in input_board["columns"][column_id]["syllableIds"]:
            syllable = input_syllables[syllable_id]
            if syllable["doculect"] in fsts_new:
                the_syl = replace_diacritics_up(syllable["syllable"])
                reconstructions = list(fsts_new[syllable["doculect"]].apply_up(the_syl))
                for rec in reconstructions:
                    if (rec, syllable["glossid"]) not in first_column_of_gr:
                        first_column_of_gr[(rec, syllable["glossid"])] = column_id
                    else:
                        ds_round1.add(
                            first_column_of_gr[(rec, syllable["glossid"])], column_id
                        )

    equivclasses = ds_round1.group.keys()
    for equivclass_id in equivclasses:
        columns = sorted(ds_round1.group[equivclass_id])
        # how to merge columns? Simple: be conservative, don't merge them
        if len(columns) > 1:
            if not production:
                eprint(columns)
            for col in columns:
                # prepare a report
                report = []
                for syl_id in old_columns[col]["syllableIds"]:
                    syl = input_syllables[syl_id]
                    report.append(syl["glossid"] + syl["syllable"])
                if not production:
                    eprint(", ".join(report))

    new_columns = {}
    new_column_of_old_column = {}

    # TODO: not done yet, so restore input_columns for now
    input_columns = old_columns

    ### SECOND ROUND FISHING
    # TODO: need to work on new_columns instead of whatever it works on
    # use the new transducers to unite the cognate sets into boards
    reconstructions_of_column = {}
    strictness_of_column = {}

    first_column_of_reconstruction = {}
    sortkey_of_column = {}
    included_in_clean = set([])

    # ds holds the merging relationship of columns
    ds = DisjointSet()

    # We process each cognate set with ID "column_id"
    for column_id in input_board["columns"]:
        reconsts = {}  # indexed by doculect
        at_least_one = False
        first_form = False  # will contain any daughter-language form, so as to provide a board title in the case of no available reconstruction

        for syllable_id in input_board["columns"][column_id]["syllableIds"]:
            syllable = input_syllables[syllable_id]

            if not first_form:
                first_form = syllable["syllable"]

            if syllable["doculect"] in fsts_new:
                the_syl = replace_diacritics_up(syllable["syllable"])
                rec = list(fsts_new[syllable["doculect"]].apply_up(the_syl))

                if rec:
                    # Now at least one syllable-form in the cognate set has a reconstruction!
                    at_least_one = True
                    # Add the reconstruction to that of other word-forms in the same language reconstructed to the same root
                    if syllable["doculect"] not in reconsts:
                        reconsts[syllable["doculect"]] = set(rec)
                    else:
                        reconsts[syllable["doculect"]] = reconsts[
                            syllable["doculect"]
                        ].union(set(rec))

        strict = True
        column_reconstructions = []

        if at_least_one:
            strict = True
            # first, try an intersection of 'em all together
            column_reconstructions = list(set.intersection(*reconsts.values()))
            # if this doesn't work, at least one lg WITH reconstruction refuse to adopt to the common reconstruction
            if not column_reconstructions:
                strict = False
                # kinda lenient way of generating reconstructions
                # the union of the intersections of every pair of doculects
                pairwise_intersections = [
                    set.intersection(reconsts[a], reconsts[b])
                    for a in reconsts
                    for b in reconsts
                    if a != b
                ]
                if pairwise_intersections:
                    column_reconstructions = list(set.union(*pairwise_intersections))
                else:
                    column_reconstructions = []

            # add some asterisks for fun
            column_reconstructions = ["*" + w for w in column_reconstructions]

        # Now "column_reconstructions" contains a reasonable guess for what should be reconstructed to this cognate set, put them into the global variables
        reconstructions_of_column[column_id] = column_reconstructions
        strictness_of_column[column_id] = strict
        if column_reconstructions:
            sortkey_of_column[column_id] = (0, column_reconstructions[0])
        else:
            sortkey_of_column[column_id] = (1, str(first_form))

        # Merge with every cognate set that share at least one reconstruction
        ds.add(column_id, column_id)
        for reconst in column_reconstructions:
            if reconst not in first_column_of_reconstruction:
                first_column_of_reconstruction[reconst] = column_id
            else:
                ds.add(first_column_of_reconstruction[reconst], column_id)

        # Compute reliability
        # Reliable := reconstruction present and based on more than one language
        if column_reconstructions and len(reconsts) > 1:
            included_in_clean.add(column_id)

    # Sort crossids according to reconstruction / form
    # taken from ds
    equivclasses = sorted(
        ds.group.keys(), key=lambda column_id: sortkey_of_column[column_id]
    )

    created_board_counter = 1

    # Second round: print the actual content from display_crossids
    # TODO: need to work on new_columns instead of whatever it works on
    ## Takes the list of grouped columns, decides whether to make a board, then names the board.
    for equivclass_id in equivclasses:
        # get columns in the equivalent class
        columns = sorted(ds.group[equivclass_id])

        # get strictness and cleanness
        strict = all([strictness_of_column[col] for col in columns])
        clean = any([col in included_in_clean for col in columns])
        # if not at least one of the columns clean, doesn't get to be a board
        ## IMPORTANT!: This is the cutting down of the putative boards into manageable amounts, I believe...
        if not clean:
            continue

        # A new board, yeah!
        board_id = "board-" + str(created_board_counter)
        created_board_counter += 1

        # Enable reverse query "new_board_of_column"
        for col in columns:
            new_board_of_column[col] = board_id

        # Now, compute a board title
        all_reconstructions = [set(reconstructions_of_column[col]) for col in columns]
        reconstructions = list(set.intersection(*all_reconstructions))
        if not reconstructions:
            strict = False
            pairwise_intersections = [
                set.intersection(all_reconstructions[a], all_reconstructions[b])
                for a in range(len(all_reconstructions))
                for b in range(len(all_reconstructions))
                if a != b
            ]
            if pairwise_intersections:
                reconstructions = list(set.union(*pairwise_intersections))
            else:  # impossible
                reconstructions = []

        if not reconstructions:
            board_title = "*???"
        else:
            board_title = ", ".join(reconstructions)
            if len(board_title) > 12:
                board_title = board_title[:10] + "..."
            if not strict:
                board_title += "?"

        board_json = {
            "id": board_id,
            "title": board_title,
            "columnIds": columns,
        }
        json_boards[board_id] = board_json

    json_current_board = "board-1"

    # Reboarding status & last resource conservative reboarding
    for column_id in list(input_columns.keys()):
        if not input_columns[column_id]["syllableIds"]:
            # empty column, can be deleted w/o problem
            del input_columns[column_id]
            continue

        if column_id not in old_board_of_column and column_id in new_board_of_column:
            # recently fished
            input_columns[column_id]["refishingStatus"] = "new"
        elif column_id in old_board_of_column and column_id not in new_board_of_column:
            if "refishingStatus" in input_columns[column_id]:
                del input_columns[column_id]["refishingStatus"]
            # make a last-ditch effort to put it somewhere
            input_columns[column_id]["refishingStatus"] = "deadfish"
            if column_id not in new_board_of_column:
                if not input_columns[column_id]["syllableIds"]:
                    continue  # empty column, don't complain
                # let's seek the its old boardmates
                boardmates = old_boards[old_board_of_column[column_id]]["columnIds"]
                new_board_of_any = False
                for boardmate in boardmates:
                    if boardmate in new_board_of_column:
                        new_board_of_any = new_board_of_column[boardmate]
                        continue
                if new_board_of_any:
                    if not production:
                        eprint(
                            column_id,
                            str(reconstructions_of_column[column_id]),
                            "reassigned to",
                            new_board_of_any,
                            json_boards[new_board_of_any]["title"],
                        )
                    json_boards[new_board_of_any]["columnIds"].append(column_id)
        else:
            # no change, let's not clobber the interface
            if "refishingStatus" in input_columns[column_id]:
                del input_columns[column_id]["refishingStatus"]

    eprint("Successful refishing.")
    return {"columns": input_columns, "boards": json_boards}
