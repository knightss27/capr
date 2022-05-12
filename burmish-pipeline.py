#!/usr/bin/python
from os import system
from lingpy import *
from lingpy.compare.partial import Partial
from collections import defaultdict
from tabulate import tabulate
from copy import copy
from burmtools import *
from lingrex.colex import find_colexified_alignments
from lingrex.align import template_alignment
from lingrex.copar import *

wl = Wordlist('burmish-primitive-2000-with-ob.tsv')

# parse the ipa
ipa_parse = {idx:burmish_parse(wl[idx, 'ipa'], wl[idx, 'doculect']) for idx in wl}
wl.add_entries('tokens', ipa_parse, lambda tup: tup[0])
wl.add_entries('structure', ipa_parse, lambda tup: tup[1])
wl.output('tsv', filename='burmish-stage1-tmp')

# dirty hack
# remove everything with �
system('grep -v � burmish-stage1-tmp.tsv > burmish-stage1.tsv')

# Runs to generate COGIDS and cognates.
# lexstat
par = Partial('burmish-stage1.tsv', segments='tokens')
get_scorer_kw = dict(runs=10000)
par.get_scorer(**get_scorer_kw)
par.partial_cluster(method='lexstat', threshold=0.6, cluster_method='single', post_processing=True, imap_mode=False, ref='cogids')
par.output('tsv', filename='burmish-stage2-1-lexstat', subset=True, cols=['doculect', 'concept', 'glossid', 'ipa', 'tokens', 'structure', 'cogids'])

###
# This function does not exist anymore...
#print("Now running align_by_structure")
#align_by_structure(par, segments='tokens', ref='cogids', structure='structure')
###

print("Now running Alignments")
alms = Alignments("burmish-stage2-1-lexstat.tsv", ref='cogids')

template_alignment(alms,
                   ref='cogids',
                   template='imMnNct', ### This is what is listed as the 'template' default in the old `align_by_structure` method.
                   structure = 'structure',
                   fuzzy=True,
                   segments='tokens')

print("Now running find_colexified_alignments")
find_colexified_alignments(alms, cognates='cogids', ref='crossids')


# Runs to generate CROSSIDS and ALIGNMENT, without COGIDS (thus the next step is to merge).
print("Outputting aligned tsv")
alms.output('tsv', filename='burmish-stage2-2-aligned', subset=True, cols=['doculect', 'concept', 'glossid', 'ipa', 'tokens', 'structure', 'alignment', 'crossids'])
