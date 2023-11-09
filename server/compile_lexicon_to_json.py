#!/usr/bin/python
# Compile Burmish lexicon
# Dependencies: Python ICU; Parsy
# Usage: Unix-ish

# Basic imports
import argparse
import csv
import fileinput
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from functools import reduce

from .disjointset import DisjointSet
from .foma import FST


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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
# If there is already "◦" or a space, use it to separate them
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


# emphasize_syllable("mi ma mu", 1) → "mi<ma>mu"
def emphasize_syllable(
    text, syllable_index, usual_formatting=None, emphatic_formatting=None
):
    syllables = syllabize(text)
    l = len(syllables)
    result = ""
    for i in range(l):
        if i == syllable_index:
            result = result + (emphatic_formatting or "<%s>") % syllables[i]
        else:
            result = result + (usual_formatting or "%s") % syllables[i]
    return result


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


def process_row(row, json_words, json_syllables, rows_of_crossid):
    if row["ID"].startswith("#"):
        # internal to lingpy
        return

    if row["CROSSIDS"]:
        crossids = row["CROSSIDS"].split(" ")
    else:
        eprint("SANITY: empty crossid: ", row["ID"])
        return

    word_id = "word-" + row["ID"]
    syllables = syllabize(row["IPA"])
    word_json = {
        "id": word_id,
        "doculect": row["DOCULECT"],
        "syllables": syllables,
        "gloss": row["CONCEPT"],
        "glossid": row["GLOSSID"],
    }
    json_words[word_id] = word_json

    syl_number = len(crossids)

    # Now we can loop on each syllable in the language
    for syl in range(syl_number):
        crossid = crossids[syl]

        # Put new information into crossid data
        syl_row = (syl, row)
        if not (crossid in rows_of_crossid):
            rows_of_crossid[crossid] = [syl_row]
        else:
            rows_of_crossid[crossid].append(syl_row)

        syllable_id = word_id + "-" + str(syl)

        syllable_json = dict(word_json)
        syllable_json["id"] = syllable_id
        syllable_json["wordId"] = word_id
        syllable_json["syllOrder"] = syl
        syllable_json["syllable"] = syllables[syl]

        json_syllables[syllable_id] = syllable_json


# Function: reorder_row_tuples
# Reorder the specific rows that are belong to the same CrossID for correct display
# For now, there are two things to do:
# (1) Old Burmese → Rangoon → remaining languages
# (2) sort by meaning
def sort_row_tuples(row_tuples, reconstructed_sense):
    # first step: sorting by languages
    # 1) sort by languages alphabetically
    row_tuples_sorted_by_languages = sorted(row_tuples, key=lambda x: x[1]["DOCULECT"])
    # 2) raise the languages we want to raise
    ob = [
        (syl, row)
        for (syl, row) in row_tuples_sorted_by_languages
        if row["DOCULECT"] == "Old_Burmese"
    ]
    rangoon = [
        (syl, row)
        for (syl, row) in row_tuples_sorted_by_languages
        if row["DOCULECT"] == "Rangoon"
    ]
    remaining = [
        (syl, row)
        for (syl, row) in row_tuples_sorted_by_languages
        if (row["DOCULECT"] != "Old_Burmese" and row["DOCULECT"] != "Rangoon")
    ]
    row_tuples_sorted_by_languages = ob + rangoon + remaining

    # second step: sorting by senses
    row_tuples_sorted_by_senses = sorted(
        row_tuples_sorted_by_languages, key=lambda x: x[1]["CONCEPT"]
    )
    return row_tuples_sorted_by_senses


def compile_transducers(transducer_txt):
    '''Takes a transducer as text, compiles it and returns a dict of doculects
    to transducer objects. The doculets are retrieved from the transducer text
    by parsing lines of the shape `save stack XXX.bin`'''
    doculects = [re.search('save stack ([\w-]+).bin', line).group(1)
                 for line in transducer_txt.splitlines()
                 if line.startswith('save stack')]

    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        eprint("Compiling FSTs (new)")
        with open("transducer.foma", "w", encoding="utf-8") as fp:
            fp.write(transducer_txt)
        output = subprocess.check_output(["foma",
                                          "-f",
                                          "transducer.foma"]).decode("UTF-8")
        eprint("\n".join(output.split("\n")[-5:]))

        fsts = {doculect: FST.load(doculect + ".bin")
                for doculect in doculects}

    eprint(fsts)
    eprint("FSTs loaded:", ", ".join(fsts))

    return fsts


def load_data_dict(path):
    ret = dict()

    # For some reason, Python sometimes can't find this file...
    with open(os.path.abspath(path)) as f:
        csvreader = csv.DictReader(
            filter(lambda row: row.strip() and not row.startswith('#'), f),
            dialect='excel-tab')
        for row in csvreader:
            ret[row['ID']] = row
    return ret


def get_boards(data_dict, cognate_col):
    doculects = sorted(set([row["DOCULECT"] for row in data_dict.values()]))
    boards = {
        "fstDoculects": doculects,
        "fstUp": {d: {} for d in doculects},
        "fstDown": {d: {} for d in doculects},
        "boards": {},
        "words": {},
        "columns": {},
        "syllables": {},
    }

    # fill data with content by iterating over the data_dict
    for row in data_dict.values():
        idx = f"word-{row['ID']}"
        boards["words"][idx] = {
            "id": idx,
            "doculect": row["DOCULECT"],
            # "syllables": [".".join(row["TOKENS"].split())],
            "syllables": [".".join(r.split(" "))
                          for r in row["TOKENS"].split(" + ")],
            # "syllables": syllabize(row["IPA"]),
            "gloss": row["CONCEPT"],
            "glossid": row["GLOSSID"],
        }


        for syl_idx, syllable in enumerate(boards["words"][idx]["syllables"]):
            syl_id = f"{idx}-{syl_idx}"
            boards["syllables"][syl_id] = {
                "id": syl_id,
                "doculect": row["DOCULECT"],
                "syllables": boards["words"][idx]["syllables"],
                "gloss": boards["words"][idx]["gloss"],
                "glossid": boards["words"][idx]["glossid"],
                "wordID": idx,
                "syllOrder": syl_idx,
                "syllable": syllable,
            }

            # eprint(syllable_ids)
            # column ids are in fact the cognate sets
            cogid = "column-" + row[cognate_col].split(" ")[syl_idx]
            if cogid in boards["columns"]:
                boards["columns"][cogid]["syllableIds"].append(syl_id)
            else:
                boards["columns"][cogid] = {"id": cogid,  # CHECK: "id" no need
                                            "syllableIds": [syl_id]}

    return boards


def load_transducer(transducer, pipeline_name, fst_path):
    if transducer != "internal":
        new_transducer = transducer
    else:
        # try and access the pipeline file in /fsts
        # if not present, uses fst_path (== refish.txt)
        if os.path.isfile(f"/usr/app/fsts/{pipeline_name}.txt"):
            fst_path = f"/usr/app/fsts/{pipeline_name}.txt"
            eprint(f"Found input transducer for {pipeline_name}")

        with open(fst_path, encoding="utf-8") as fst_file:
            new_transducer = fst_file.read()
    return new_transducer


def compile_to_json_full_cognates(
    path,
    transducer="internal",
    fst_path="/usr/app/refishing-fst.txt",
    cognate_col="COGIDS", #TODO: find out a good way of determ
):
    """
    Get the JSON from a wordlist file with "normal" cognates.

    Example
    -------

    compile_to_json_full_cognates(
        "pipeline/output/germanic/stage3/germanic-aligned-final.tsv",
        "Proto-Germanic", cognate_col="CROSSIDS")
    """

    # The name of the language "pipeline"
    # Should be the first word of your input file before a "-", i.e.
    # germanic-data.tsv --> germanic, burmish-data.tsv --> burmish
    pipeline_name = path.rsplit('.')[0].split("-")[0]
    eprint(f"Assuming pipeline name: {pipeline_name}")

    # Finding file path
    path = os.path.join('/usr/app/data', path)

    # Where we will put everything we read from the input data
    data_dict = load_data_dict(path)

    # create the board dictionary
    boards = get_boards(data_dict, cognate_col)

    # Now we start working with the transducers
    new_transducer = load_transducer(transducer, pipeline_name, fst_path)

    fsts = compile_transducers(new_transducer)
    # not particularly elegant, but that keeps compile_transducers cleaner
    # {'german': FST} => {'German': FST}
    fsts = {doculect: fsts[doculect.lower()]
            for doculect in boards['fstDoculects']
            if doculect.lower() in fsts}


    # For each cogid, we will create a list of the cognates to be transduced
    # Where it is a tuple of the cognate itself, plus the associated doculect
    # e.g. {102: [('j.uː.θ', 'English'), ('j.uː.ɡ.ə.n.t', 'Deutsch')], ...}
    rows_of_cognates = defaultdict(list)

    # Loop over each CROSSID (or COGIDS?) and add the relevant words
    for row in data_dict.values():
        idx = f"word-{row['ID']}"
        cogids_list = row[cognate_col].split(" ")

        # now we pretend to always be working with morphemes
        # eprint(cogids_list, row)

        # Now we're just making a list of all the syllables/morphemes
        for syl_idx, morph_cogid in enumerate(cogids_list):
            rows_of_cognates[morph_cogid].append(
                (boards["words"][idx]["syllables"][syl_idx], row['DOCULECT'])
            )
        
            # eprint(rows_of_cognates[morph_cogid])
    # Will hold something, TBD
    ds = DisjointSet()

    # TBD what this stuff does
    reconstructions_of_crossid = dict()
    strictness_of_crossid = dict()
    # ---
    sortkey_of_crossid = dict()
    first_crossid_of_reconstruction = dict()
    included_in_clean = set()
    # ---

    # Now go through each cogid we've collected to actually start running transducers
    for cogid, cogs in rows_of_cognates.items():
        # First, try to guess the reconstruction by the following rule:
        # 1. Collect all reconstructions for each language
        # 2. The intersection of all reconstructions is the most probable one
        reconstructions = defaultdict(set)
        first_form = False
        at_least_one = False

        # the cogids are not being split properly... TODO
        # eprint(cogid)
        # eprint(cogs)

        # For each word (with Burmish would be syllable) that shares a cogid/crossid
        for word, doculect in cogs:
            # eprint(word, cogs)

            if not first_form:
                # TBD what this is used for
                pass

            # If we have a transducer for this doculect
            if doculect in fsts:
                # Make the current syllable equal to the whole word, since we are
                # working with the Germanic data. Also add spaces so that Mattis'
                # transducer will work.

                syl = word.replace(".", "")

                # for burmish?  # yes
                syl = replace_diacritics_up(syl)

                # Apply the transducer upwards to this word (/syl/morpheme)
                recs = list(fsts[doculect].apply_up(syl))

                # eprint(recs)

                # Add the reconstructions to our record, whether or not they exist
                boards["fstUp"][doculect][word] = sorted(set(recs))

                # TBD
                # attested_reconstructions.update(rec)

                # Only worry about reconstructions when we have actually made one
                if len(recs) > 0:
                    at_least_one = True
                    reconstructions[doculect] |= set(recs)

        strict = True  # usage TBD

        # Here is where we will store all our reconstructions for this cogid/crossid
        cognate_reconstructions = []

        # If we have at least one reconstruction made (so we can make a board?)
        if at_least_one:
            strict = True
            cognate_reconstructions = list(set.intersection(*reconstructions.values()))

            if not cognate_reconstructions:
                strict = False
                # kinda lenient way of generating reconstructions
                # try and make intersection of every pair of doculects
                pairwise_intersections = [
                    set.intersection(reconstructions[a], reconstructions[b])
                    for a in reconstructions
                    for b in reconstructions
                    if a != b
                ]
                if pairwise_intersections:
                    cognate_reconstructions = list(set.union(*pairwise_intersections))
                else:
                    cognate_reconstructions = []

                cognate_reconstructions = ["*" + w for w in cognate_reconstructions]

            # print(cognate_reconstructions)

        # TODO: Actually go through what is written below and clean it up
        # I have not verified what a lot of this does in the same way I did the
        # lines above this comment

        reconstructions_of_crossid[cogid] = cognate_reconstructions
        strictness_of_crossid[cogid] = strict

        if cognate_reconstructions:
            sortkey_of_crossid[cogid] = (0, cognate_reconstructions[0])
        else:
            sortkey_of_crossid[cogid] = (1, str(first_form))

        # merge with disjoint sets
        ds.add(cogid, cogid)
        for reconst in cognate_reconstructions:
            if reconst not in first_crossid_of_reconstruction:
                first_crossid_of_reconstruction[reconst] = cogid
            else:
                ds.add(first_crossid_of_reconstruction[reconst], cogid)

        # Only output items when the reconstruction is reliable, i.e.
        # reconstruction present and based on more than one language, are printed
        # with the "--clean" flag
        if cognate_reconstructions and len(reconstructions) > 1:
            included_in_clean.add(cogid)

    display_crossids = sorted(
        ds.group.keys(), key=lambda cogid: sortkey_of_crossid[cogid]
    )

    # print(display_crossids)

    boardid_cntr = 1

    # Second round: print the actual content from display_crossids
    for major_crossid in display_crossids:
        # get crossids sharing the same reconstruction
        crossids = sorted(ds.group[major_crossid])

        # get reconstructions and strictness
        strict = all(strictness_of_crossid[crossid] for crossid in crossids)
        clean = any(crossid in included_in_clean for crossid in crossids)

        # If not included in "--clean", continue
        if not clean:
            # print("Not clean, skipping...")
            continue

        all_reconstructions = [
            set(reconstructions_of_crossid[crossid]) for crossid in crossids
        ]
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
            else:
                reconstructions = []

        board_id = "board-" + str(boardid_cntr)
        boardid_cntr += 1

        board_title = ", ".join(reconstructions)
        if len(board_title) > 12:
            board_title = board_title[:10] + "..."
        elif not board_title:
            board_title = "*?"

        board_columns = ["column-" + cid for cid in crossids]

        board_json = {
            "id": board_id,
            "title": board_title,
            "columnIds": board_columns,
        }
        # print(board_json)

        boards["boards"][board_id] = board_json

    return boards


# compile_to_json_full_cognates("./pipeline/output/germanic/stage3/germanic-aligned-final.tsv")


def compile_to_json(filepath):
    fst_burmese = FST.load("./reconstruct/burmese.bin")
    fst_achang = FST.load("./reconstruct/ngochang.bin")
    fst_maru = FST.load("./reconstruct/maru.bin")
    fst_bola = FST.load("./reconstruct/bola.bin")
    fsts = {
        "Old_Burmese": fst_burmese,
        "Achang_Longchuan": fst_achang,
        "Maru": fst_maru,
        "Bola": fst_bola,
    }

    # JSONs
    json_words = {}
    json_syllables = {}
    json_columns = {}
    json_boards = {}

    # caching fst_up and fst_down
    attested_reconstructions = set({})

    json_fst_doculects = [fst for fst in fsts]
    json_fst_up = {fst: {} for fst in fsts}
    json_fst_down = {fst: {} for fst in fsts}

    # Use fileinput to imitate standard UNIX utility behaviour
    csvreader = csv.DictReader(
        filter(
            lambda row: row.strip() and row[0] != "#",
            fileinput.input(files=filepath, mode="r"),
        ),
        dialect="excel-tab",
    )

    # rootid/crossid correspondence
    rows_of_crossid = {}  # dictionary of arrays of duples: syllable index, row
    protos_of_crossid = {}  # dictionary of sets of duples: syllable index, row

    # First round: guess the reconstruction and sort/merge the items to be printed
    # sort keys for crossid's getting the things in alphabetical order
    reconstructions_of_crossid = {}
    strictness_of_crossid = {}

    sortkey_of_crossid = {}
    first_crossid_of_reconstruction = {}
    included_in_clean = set([])

    eprint("Processing TSV rows...")
    for row in csvreader:
        process_row(row, json_words, json_syllables, rows_of_crossid)

    # ds holds the merging relationship of crossids
    ds = DisjointSet()

    # pylint: disable=consider-using-dict-items
    for crossid in rows_of_crossid.keys():
        # First, try to guess the reconstruction by the following rule:
        # 1. Collect all reconstructions for each language
        # 2. The intersection of all reconstructions is the most probable one
        reconsts = {}
        at_least_one = False
        first_form = False

        json_syllableids = []

        for syl, row in sort_row_tuples(rows_of_crossid[crossid], ""):
            json_syllableids.append("word-" + row["ID"] + "-" + str(syl))

            if not first_form:
                first_form = fetch_syllable(row["IPA"], syl)
            if row["DOCULECT"] in fsts:
                the_syl = replace_diacritics_up(fetch_syllable(row["IPA"], syl))
                rec = list(fsts[row["DOCULECT"]].apply_up(the_syl))

                json_fst_up[row["DOCULECT"]][the_syl] = sorted(set(rec))
                attested_reconstructions.update(rec)

                if rec:
                    # only record reconstructions when something *is* reconstructed
                    at_least_one = True
                    if row["DOCULECT"] not in reconsts:
                        reconsts[row["DOCULECT"]] = set(rec)
                    else:
                        reconsts[row["DOCULECT"]] = reconsts[row["DOCULECT"]].union(
                            set(rec)
                        )

        strict = True
        crossid_reconstructions = []

        if at_least_one:
            strict = True
            crossid_reconstructions = list(set.intersection(*reconsts.values()))

            if not crossid_reconstructions:
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
                    crossid_reconstructions = list(set.union(*pairwise_intersections))
                else:
                    crossid_reconstructions = []

            crossid_reconstructions = ["*" + w for w in crossid_reconstructions]

        # save data from crossid
        reconstructions_of_crossid[crossid] = crossid_reconstructions
        strictness_of_crossid[crossid] = strict

        if crossid_reconstructions:
            sortkey_of_crossid[crossid] = (0, crossid_reconstructions[0])
        else:
            sortkey_of_crossid[crossid] = (1, str(first_form))

        # merge with disjoint sets
        ds.add(crossid, crossid)
        for reconst in crossid_reconstructions:
            if reconst not in first_crossid_of_reconstruction:
                first_crossid_of_reconstruction[reconst] = crossid
            else:
                ds.add(first_crossid_of_reconstruction[reconst], crossid)

        # Only output items when the reconstruction is reliable, i.e.
        # reconstruction present and based on more than one language, are printed
        # with the "--clean" flag
        if crossid_reconstructions and len(reconsts) > 1:
            included_in_clean.add(crossid)

        # Output JSON
        column_id = "column-" + str(crossid)
        column_json = {"id": column_id, "syllableIds": json_syllableids}
        json_columns[column_id] = column_json

    # Sort crossids according to reconstruction / form
    # taken from ds
    display_crossids = sorted(
        ds.group.keys(), key=lambda crossid: sortkey_of_crossid[crossid]
    )

    boardid_cntr = 1

    # Second round: print the actual content from display_crossids
    for major_crossid in display_crossids:
        # get crossids sharing the same reconstruction
        crossids = sorted(ds.group[major_crossid])

        # get reconstructions and strictness
        strict = all([strictness_of_crossid[crossid] for crossid in crossids])
        clean = any([crossid in included_in_clean for crossid in crossids])

        # If not included in "--clean", continue
        if not clean:
            continue

        all_reconstructions = [
            set(reconstructions_of_crossid[crossid]) for crossid in crossids
        ]
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
            else:
                reconstructions = []

        board_id = "board-" + str(boardid_cntr)
        boardid_cntr += 1

        board_title = ", ".join(reconstructions)
        if len(board_title) > 12:
            board_title = board_title[:10] + "..."
        elif not board_title:
            board_title = "*?"

        board_columns = ["column-" + cid for cid in crossids]

        board_json = {
            "id": board_id,
            "title": board_title,
            "columnIds": board_columns,
        }
        json_boards[board_id] = board_json

    json_current_board = "board-1"

    # calculate json_fst_down
    for language in json_fst_doculects:
        for proto_form in sorted(attested_reconstructions):
            json_fst_down[language][proto_form] = sorted(
                set(
                    replace_diacritics_down(s)
                    for s in fsts[language].apply_down(proto_form)
                )
            )

    return {
        "fstDoculects": json_fst_doculects,
        "fstUp": json_fst_up,
        "fstDown": json_fst_down,
        "words": json_words,
        "syllables": json_syllables,
        "columns": json_columns,
        "boards": json_boards,
        "currentBoard": json_current_board,
    }
