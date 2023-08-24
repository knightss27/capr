#!/usr/bin/python
from os import system
import argparse
from lingpy import *
from lingpy.compare.partial import Partial
from lingpy import basictypes
from collections import defaultdict
from tabulate import tabulate
from copy import copy
from burmtools import *
from lingrex.colex import find_colexified_alignments, find_bad_internal_alignments
from lingrex.align import template_alignment
from lingrex.copar import *
from pathlib import Path


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [TSV_FILE]",
        description="Convert an aligned and segmented dataset to CAPR input form",
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version 0.0.1"
    )

    parser.add_argument("--from-aligned", action=argparse.BooleanOptionalAction)
    parser.add_argument("--pipeline", nargs="?")
    parser.add_argument("file")

    return parser


def from_primitive(file_name, pipeline_name="pipeline"):
    """Should take a primitive dataset (unaligned and unsegmented) and convert it.
    Currently relies heavily on Burmish-specific code, so is not factored out;
    should maybe even not be done by this program?
    """
    if not Path(
        f"./output/{pipeline_name}/stage2/{pipeline_name}-stage2-1-lexstat.tsv"
    ).exists():
        wl = Wordlist(filename=file_name)

        # parse the ipa
        if pipeline_name == "burmish":
            ipa_parse = {
                idx: burmish_parse(wl[idx, "ipa"], wl[idx, "doculect"]) for idx in wl
            }

            print(ipa_parse[1])

            wl.add_entries("tokens", ipa_parse, lambda tup: tup[0])
            wl.add_entries("structure", ipa_parse, lambda tup: tup[1])

        wl.output(
            "tsv",
            filename=f"./output/{pipeline_name}/stage1/{pipeline_name}-stage1-tmp",
        )

        # # dirty hack
        # # remove everything with �
        system(
            f"grep -v � ./output/{pipeline_name}/stage1/{pipeline_name}-stage1-tmp.tsv > ./output/{pipeline_name}/stage1/{pipeline_name}-stage1.tsv"
        )

        # Runs to generate COGIDS and cognates.
        # lexstat
        par = Partial(
            f"./output/{pipeline_name}/stage1/{pipeline_name}-stage1.tsv",
            segments="tokens",
        )
        get_scorer_kw = dict(runs=10000)
        par.get_scorer(**get_scorer_kw)
        par.partial_cluster(
            method="lexstat",
            threshold=0.6,
            cluster_method="single",
            post_processing=True,
            imap_mode=False,
            ref="cogids",
        )

        # check for alignments with missing structure mismatch and exclude them!
        excludes = set()
        for idx, tokens, structure in par.iter_rows("tokens", "structure"):
            for m, s in zip(tokens.n, basictypes.lists(structure).n):
                if len(m) != len(s):
                    excludes.add(idx)
        # create dictionary that can be read in as a wordlist
        D = {0: par.columns}
        for idx in par:
            if idx not in excludes:
                D[idx] = [par[idx, c] for c in D[0]]
        print("Excluded {0} words".format(len(excludes)))
        wl = Wordlist(D)

        wl.output(
            "tsv",
            filename=f"./output/{pipeline_name}/stage2/{pipeline_name}-stage2-1-lexstat",
            subset=True,
            cols=[
                "doculect",
                "concept",
                "glossid",
                "ipa",
                "tokens",
                "structure",
                "cogids",
            ],
            prettify=False,
        )

        from_aligned(
            f"./output/{pipeline_name}/stage2/{pipeline_name}-stage2-1-lexstat.tsv",
            pipline_name=pipeline_name,
            use_template_alignment=True,
        )


def from_aligned(file_name, pipline_name="pipeline", use_template_alignment=False):
    """Take a aligned and/or segmented input file and format it for CAPR."""

    print("Now running Alignments")
    alms = Alignments(
        file_name, ref=f"{'cogids' if use_template_alignment else 'cogid'}"
    )

    # maybe a working way to generate gloss ids?
    # would be good to link ever concept in the data to an id in the concepticon
    if not "glossid" in alms.columns:
        gloss_index = 1
        entered_ids = {}
        wl_glossids = {}
        for idx in alms:
            if not alms[idx, "concept"] in entered_ids:
                entered_ids[alms[idx, "concept"]] = gloss_index
                gloss_index += 1

            wl_glossids[idx] = entered_ids[alms[idx, "concept"]]
        alms.add_entries("glossid", wl_glossids, lambda idx: idx)

    if pipline_name == "germanic":
        # Set all concepts to English variants, removing data that does not have
        # an English counterpart...

        # NOTE: the concept is the proto-form, since we do not have semantic
        # reconstructions, so we need to embrace it here, and just go with this
        # form, I suggest, for this reason, no realy pipeline-specific code is
        # needed here
        pass


    ###
    # This function does not exist anymore...
    # print("Now running align_by_structure")
    # align_by_structure(par, segments='tokens', ref='cogids', structure='structure')
    ###

    if use_template_alignment and pipline_name == "burmish":
        # VERY Burmish specific stuff here...
        print("Starting template alignment")
        template_alignment(
            alms,
            ref="cogids",
            template="imMnNct",  ### This is what is listed as the 'template' default in the old `align_by_structure` method.
            structure="structure",
            fuzzy=True,
            segments="tokens",
        )
    
        print("Now running find_bad_internal_alignments")
        find_bad_internal_alignments(
            alms, ref=f"{'cogids' if use_template_alignment else 'cogid'}"
        )

        # generates cross ids
        print("Now running find_colexified_alignments")
        find_colexified_alignments(
            alms,
            cognates=f"{'cogids' if use_template_alignment else 'cogid'}",
            ref="crossids",
        )


        # Runs to generate CROSSIDS and ALIGNMENT, without COGIDS (thus the next step is to merge).
        print("Outputting aligned tsv")
        alms.output(
            "tsv",
            filename=f"./output/{pipline_name}/stage3/{pipline_name}-aligned-final",
            subset=True,
            cols=[
                "doculect",
                "concept",
                "glossid",
                "ipa",
                "tokens",
                "structure",
                "alignment",
                "crossids",
            ],
            prettify=False, # no "#" and spaces in code
            ignore="all" # no additional data
        )
    else:
        # we output all data, the new code to convert to json looks at the
        # header and can process datasets with columns that we don't need
        alms.output("tsv",
                    filename=f"./output/{pipline_name}/stage3/{pipline_name}-aligned-final",
                    prettify=False,
                    ignore="all"
                    )


parser = init_argparse()
args = parser.parse_args()

print(args)
fname = args.file
pname = fname.split("-")[0]

if args.pipeline:
    pname = args.pipeline

if args.from_aligned:
    from_aligned(fname, pname)
else:
    from_primitive(fname, pname)

# print(f"Pipeline '{pname}' completed!")

# from_aligned("germanic-data.tsv", "germanic-test")
# from_primitive("germanic-data.tsv", "germanic-test")
