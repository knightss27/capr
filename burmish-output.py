#!/usr/bin/python
from lingrex.copar import *
from lingpy import *
from lexibase.lexibase import *
from collections import defaultdict
from tabulate import tabulate
from burmtools import *
from merge_phonemes import merge_phonemes
from copy import copy

# languages = cop.cols
languages = ['Old_Burmese', 'Achang_Longchuan', 'Maru', 'Bola']
languages_title = ['OBurm', 'Acha-LC', 'Maru', 'Bola']
#languages = ['Old_Burmese', 'Achang_Longchuan', 'Maru']
#languages_title = ['OBurm', 'Acha-LC', 'Maru']
number_of_languages = len(languages)

# Replace unicode diacritics with ASCII equivalents for sending to the transducers
UNICODE_MACRON_UNDER = " ̱ "[1]
UNICODE_TILDE_OVER = " ̃"[1]
def replace_diacritics(s):
    return s.replace(UNICODE_MACRON_UNDER, '_').replace(UNICODE_TILDE_OVER, '~').replace('_~', '~_')


# fetch_syllable("mi ma mu", 1) → "ma"
def fetch_syllable(text, syllable_index):
    syllables = syllabize(text)
    return syllables[syllable_index]

def merge_phonemes_burmish(old_schema, old_tokens, debug=None):
    try:
        out = [merge_phonemes(str(sch), str(tk), 'i m r t', {'i': 'im', 'm':'m', 'r':'mnc', 't':'t'}) for sch, tk in zip(basictypes.lists(old_schema).n, basictypes.lists(old_tokens).n)]
        return (' + '.join([i for i,j in out]), ' + '.join([j for i,j in out]))
    except:
        print(debug)
        return ('','')

wl = Wordlist('./output/burmish-pipeline/stage2/burmish-stage2-2-aligned.tsv')
wl.add_entries('tmp_structure', 'structure,tokens', lambda x, y: merge_phonemes_burmish(x[y[0]], ' '.join(x[y[1]]), x)[0])
wl.add_entries('tmp_tokens', 'structure,tokens', lambda x, y: merge_phonemes_burmish(x[y[0]], ' '.join(x[y[1]]), x)[1])

columns = copy(wl.columns)
columns.remove('alignment')
columns.remove('structure')
columns.remove('tokens')

## Here we output a "temporary" (tmp) merged tsv between the stage 2-1 and 2-2 files, sorted by shared meaning.
## Only outputs a subset of the data for the languages defined at the top of the file.
## Reference: https://github.com/lingpy/lingpy/blob/44c027e88a7e6e8f96c32c4cddd7c19ea1902c14/src/lingpy/basic/wordlist.py#L861
wl.output('tsv', filename='./output/burmish-pipeline/stage2/burmish-stage2-tmp-merged', subset=True, rows={"doculect": " in " + str(languages)}, cols=columns)

## CoPaR = Correspondence Pattern Recognition class
cop = CoPaR('./output/burmish-pipeline/stage2/burmish-stage2-tmp-merged.tsv', ref='crossids', segments='tmp_tokens', fuzzy=True,
        structure='tmp_structure')

cop.get_sites()
cop.cluster_sites()
cop.sites_to_pattern()
cop.add_patterns()
# cop.load_patterns()

# dirty output in markdown
# get index for proto-burmish
bidx = cop.cols.index('Old_Burmese')

# sort the pattern output by Burmish rec
# get the patterns firstt into sorter
pburm = defaultdict(list)
for pattern, sites in cop.clusters.items():
    pburm[pattern[1][bidx]] += [(pattern, sites)]


## This part exports something...

text = ''

from foma import FST
fst_burmese = FST.load('./reconstruct/burmese.bin')
fst_achang = FST.load('./reconstruct/ngochang.bin')
fst_maru = FST.load('./reconstruct/maru.bin')
fsts = {'Old_Burmese': fst_burmese, 'Achang_Longchuan': fst_achang, 'Maru': fst_maru}

# Index from index in languages to index in cop.cols
languages_index = [cop.cols.index(l_name) for l_name in languages]

def convert_list_from_copcols_to_languages(l):
    return [l[languages_index[i]] for i in range(len(languages))]

for i, (sound, patterns) in enumerate(sorted(pburm.items())):
    text += '=== {1}: Old Burmese <<{0}>> ===\n'.format(sound, i+1)
    
    counter = 1
    for pattern, sites in patterns:

        pattern = pattern[1]
        try:
            displaypattern = convert_list_from_copcols_to_languages(list(pattern))
        except:
            raise ValueError(str(list(pattern)))
        
        text += '== Pattern {1}: {0} ==\n'.format(':'.join(displaypattern), str(counter))

        counter += 1

        table = [[''] + displaypattern]

        examples = 0

        # iterate over sites
        for site in sites:
            examples += 1
            crossid = site[0]
            if crossid in cop.msa['crossids']:
                # site[0] is crossid
                msa = cop.msa['crossids'][crossid]
                # make a taxon dictionary
                tmp = {t: i for i, t in enumerate(msa['taxa'])}
                evidence = [msa['seq_id']]


                for t in languages:
                    if t in tmp:
                        # look for the syllable id from the crossid
                        crossids = cop[msa['ID'][tmp[t]], 'crossids']
                        ipa = cop[msa['ID'][tmp[t]], 'ipa']
                        location = crossids.index(crossid)
                        evidence += [emphasize_syllable(ipa, location)]

                        the_syl = replace_diacritics(fetch_syllable(ipa, location))
                        if t in fsts:
                            reconst = list(fsts[t].apply_up(the_syl))
                            reconst = ['*' + w for w in reconst]
                            reconst_join = r'{\small ' + ', '.join(reconst) + r'}'
                        else:
                            reconst_join = ''
                    else:
                        evidence += ['Ø']
                table += [evidence]
            else:
                print('!!! Something bad happened with site', site[0])
                print([site[0] for x in languages])
                # table += [[site[0] for x in languages]]

        text += tabulate(table, headers=['ID'] + languages_title, tablefmt='fancy_grid')
        text += "\n\n"

with open('./output/burmish-output/burmish-patterns-table.txt', 'w') as f:
    f.write(text)