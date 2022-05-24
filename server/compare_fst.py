#!/usr/bin/python
# Compile the cognate assignment result (JSON) to the LaTeX source file of correspondence pattern (Doug-style) with comparison of two different transducers
# Fixed-location files:
#   source.tsv: lexical data
# Standard input:
#   json containing:
#   langsUnderStudy: something like ['Maru', 'Old_Burmese', 'Bola']
#   oldTransducer: (Old version)
#   newTransducer: (New version)
#   board: (Board file)

# Constants
language_title = {'Old_Burmese': 'OBurm', 'Achang_Longchuan': 'Acha-LC', 'Xiandao': 'Acha-XD', 'Maru': 'Maru', 'Bola': 'Bola', 'Atsi': 'Atsi', 'Lashi': 'Lashi'}
fst_index = {'Old_Burmese': 'burmese', 'Achang_Longchuan': 'ngochang', 'Xiandao': 'xiandao', 'Maru': 'maru', 'Bola': 'bola', 'Atsi': 'atsi', 'Lashi': 'lashi'}

# Basic imports
import sys
import re
import json
import csv
from merge_phonemes import merge_phonemes
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
def replace_diacritics(s):
    return s.replace(UNICODE_MACRON_UNDER, '_').replace(UNICODE_TILDE_OVER, '~').replace('_~', '~_')

def replace_diacritics_forward(s):
    return s.replace('_', UNICODE_MACRON_UNDER).replace('~', UNICODE_TILDE_OVER)

# Convert a piece of text to its component syllables
# If there is alrady "◦" or a space, use it to separate them
# Otherwise, separate the tone letters other letters
def syllabize(text):
    split_result = re.split(r'([ ◦¹²³⁴⁵˩˨˧˦˥]+)', text)
    l = len(split_result)

    # There are two possibilities
    # 'a◦b◦' → ['a', '◦', 'b', '◦', '']
    # 'a◦b' → ['a', '◦', 'b']
    # Both of them are odd, but should be treated differently
    # At least, everything but the last can be done in the same way
    # (5-1)/2 = 2

    result = []
    for i in range((l-1) // 2):
        result.append(split_result[i*2] + split_result[i*2+1].strip('◦ '))
    # If last non-zero, then copy to result
    if split_result[l-1]:
        result.append(split_result[l-1])

    return result

def emphasize_syllable_raw(syllables, syllable_index, usual_formatting = None, emphatic_formatting = None):
    l = len(syllables)
    result = ''
    for i in range(l):
        if i == syllable_index:
            result = result + (emphatic_formatting or '<%s>') % syllables[i]
        else:
            result = result + (usual_formatting or '%s') % syllables[i]
    return result

# emphasize_syllable("mi ma mu", 1) → "mi<ma>mu"
def emphasize_syllable(text, syllable_index, usual_formatting = None, emphatic_formatting = None):
    return emphasize_syllable_raw(syllabize(text), syllable_index, usual_formatting, emphatic_formatting)

# fetch_syllable("mi ma mu", 1) → "ma"
def fetch_syllable(text, syllable_index):
    syllables = syllabize(text)
    return syllables[syllable_index]

# Convert internal language name to printed name
def print_language_name(name):
    if name == 'Old_Burmese':
        return 'OBur.'
    else:
        return name.replace('_', r'\_')

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
        word_id, _, n = syllable_id.rpartition('-')
        n = int(n)
        ipa = words[word_id]['syllables'][n]
        doculect = words[word_id]['doculect']

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
            pairwise_intersections = [set.intersection(reconsts[a], reconsts[b])
                    for a in reconsts for b in reconsts if a != b]
            if pairwise_intersections:
                inferred_reconstructions = list(set.union(*pairwise_intersections))
            else:
                inferred_reconstructions = []

    return (inferred_reconstructions, strict)


##### MAIN PROGRAM #####

# eprint('Program starts')

# Compile transducers
from foma import FST
import tempfile
import os
import subprocess

def compare_fst(input_json):
    # decode the input JSON
    # input_json = json.load(open('input-correspondence.json', 'r+'))

    # First field from JSON: langsUnderStudy
    langs_under_study = input_json['langsUnderStudy']
    number_of_languages = len(langs_under_study)

    # Board from JSON
    script_path = os.path.dirname(os.path.realpath(__file__))

    fsts_old = {}
    fsts_new = {}

    # Reading old transducers
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        eprint('Compiling FSTs (old)')
        eprint(input_json['oldTransducer'])
        with open('transducer.foma', 'w') as fp:
            fp.write(input_json['oldTransducer'])
        output = subprocess.check_output(['foma', '-f', 'transducer.foma']).decode('UTF-8')
        eprint('\n'.join(output.split('\n')[-5:]))
        for doculect_name in fst_index:
            if os.path.isfile(fst_index[doculect_name] + '.bin'):
                fsts_old[doculect_name] = FST.load(fst_index[doculect_name] + '.bin')
        os.chdir(script_path)
        eprint('FSTs loaded:', ', '.join(fsts_old))

    # Reader
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        eprint('Compiling FSTs (new)')
        with open('transducer.foma', 'w') as fp:
            fp.write(input_json['newTransducer'])
        output = subprocess.check_output(['foma', '-f', 'transducer.foma']).decode('UTF-8')
        eprint('\n'.join(output.split('\n')[-5:]))
        for doculect_name in fst_index:
            if os.path.isfile(fst_index[doculect_name] + '.bin'):
                fsts_new[doculect_name] = FST.load(fst_index[doculect_name] + '.bin')
        os.chdir(script_path)
        eprint('FSTs loaded:', ', '.join(fsts_new))

    # read the word CSV
    # import fileinput
    csvreader = csv.DictReader(filter(lambda row: row.strip() and row[0]!='#', open('./lexicon.tsv', 'r')), dialect='excel-tab')

    eprint('Processing TSV rows...')
    words = {}
    def process_row(row):
        if row['ID'].startswith('#'):
            # internal to lingpy
            return

        if row['CROSSIDS']:
            crossids = row['CROSSIDS'].split(' ')
        else:
            eprint('SANITY: empty crossid: ', row['ID'])
            return

        word_id = 'word-' + row['ID']
        syllables = syllabize(row['IPA'])
        syllables_parsed = [merge_phonemes(str(sch), str(tk), 'i m r t', {'i': 'im', 'm':'m', 'r':'mnNc', 't':'t'}) for sch, tk in zip(row['STRUCTURE'].split(' + '), row['TOKENS'].split(' + '))]

        word_json = {
                'id':word_id,
                'doculect': row['DOCULECT'],
                'syllables': syllables,
                'syllables_parsed': syllables_parsed,
                'gloss': row['CONCEPT'],
                'glossid': row['GLOSSID']}
        words[word_id] = word_json

    for row in csvreader:
        process_row(row)

    eprint('Processing boards...')
    input_board = input_json['board']

    columns = input_board['columns']
    boards = input_board['boards']

    # list indexed by languages and initials of columns containing a certain initial in a certain language
    # column_index['i']['Old_Burmese']['p'] -> [...]
    # column_index = {}

    # column_index['i']['p:p:p'] -> [...]
    column_index = {pos:{} for pos in 'imrt'}

    for board_id in boards:
        for column_id in boards[board_id]['columnIds']:
            if not columns[column_id]['syllableIds']:
                continue

            # First, guess the reconstruction
            inferred_reconstructions, strict_reconstructions = back_reconstruct_list(columns[column_id]['syllableIds'], fsts_old, words)

            # cnt[pos][doculect] → Counter of possibilities
            cnt = {}
            sylls = {}
            senses = {}

            for syllable_id in columns[column_id]['syllableIds']:
                word_id, _, n = syllable_id.rpartition('-')
                n = int(n)

                ipa = words[word_id]['syllables'][n]
                doculect = words[word_id]['doculect']
                gloss = words[word_id]['gloss']
                syllable_parsed = words[word_id]['syllables_parsed'][n]
                syllable_fields = list(zip(syllable_parsed[0].split(' '), syllable_parsed[1].split(' ')))

                for position, sound in syllable_fields:
                    if position not in cnt:
                        cnt[position] = {}
                        sylls[position] = {}
                        senses[position] = {}
                    if doculect not in cnt[position]:
                        cnt[position][doculect] = Counter()
                        sylls[position][doculect] = {}
                        senses[position][doculect] = {}
                    if sound not in sylls[position][doculect]:
                        sylls[position][doculect][sound] = []
                        senses[position][doculect][sound] = []
                    cnt[position][doculect][sound] += 1
                    sylls[position][doculect][sound].append(ipa)
                    senses[position][doculect][sound].append(gloss)

            for position in cnt:
                # generate the information needed for displaying a corr. chart
                description = []
                most_common_ipas = []
                shared_senses = []

                # Some flags that impact display
                last_doculect_present = False
                any_non_last_doculect_present = False

                for doculect in langs_under_study:
                    if doculect in cnt[position]:
                        if doculect == langs_under_study[-1]:
                            last_doculect_present = True
                        else:
                            any_non_last_doculect_present = True

                        most_common_sound = cnt[position][doculect].most_common()[0][0]
                        most_common_ipa = Counter(sylls[position][doculect][most_common_sound]).most_common()[0][0]
                        description.append(most_common_sound)
                        most_common_ipas.append(most_common_ipa)
                        shared_senses.extend(senses[position][doculect][most_common_sound])
                    else:
                        description.append('-')
                        most_common_ipas.append('--')
                description = ':'.join(description)

                most_common_gloss = '?'
                if shared_senses:
                    most_common_gloss = Counter(shared_senses).most_common()[0][0]

                column_info = {'column_id': column_id,
                        'most_common_gloss': most_common_gloss,
                        'most_common_ipas': most_common_ipas,
                        'last_doculect_present': last_doculect_present,
                        'any_non_last_doculect_present': any_non_last_doculect_present,
                        'old_fst_reconstructions': (inferred_reconstructions, strict_reconstructions),
                        'new_fst_reconstructions': back_reconstruct_list(columns[column_id]['syllableIds'], fsts_new, words)}
                if description not in column_index[position]:
                    column_index[position][description] = []
                column_index[position][description].append(column_info)

    text = ''

    pos_name = {'i': 'Initial', 'm': 'Medial', 'r': 'Rime', 't': 'Tone'}
    json_chapters = {}

    for pos in column_index:
        text += '=====' + pos_name[pos] + ' Correspondence =====\n'
        json_chapters[pos] = []
        for description in sorted(column_index[pos]):
            if not column_index[pos][description] or not column_index[pos][description][0]['last_doculect_present'] or not column_index[pos][description][0]['any_non_last_doculect_present']:
                continue

            text += "=== %s: %s ===\n" % (pos_name[pos], description)

            this_section = {'title': "=== %s: %s ===\n" % (pos_name[pos], description)}
            rows = []

            for column in column_index[pos][description]:
                this_row = {}

                # first row: gloss & IPA's
                this_row['gloss'] = column['most_common_gloss']
                this_row['ipas'] = column['most_common_ipas']

                # second row: old reconstructions
                row = []
                inferred_reconstructions, strict_reconstructions = column['old_fst_reconstructions']
                if inferred_reconstructions:
                    rec_str = ', '.join(['*' + w for w in inferred_reconstructions])
                    if not strict_reconstructions:
                        rec_str += '?'
                    this_row['old_reconstruction'] = rec_str
                
                old_reconstruction_matched = False
                new_reconstruction_matched = False

                for i in range(len(langs_under_study)):
                    doculect = langs_under_study[i]
                    under_study = i == len(langs_under_study) - 1
                    rec = []
                    if doculect in fsts_old and column['most_common_ipas'][i] != '--':
                        the_syl = replace_diacritics(column['most_common_ipas'][i])
                        rec = list(set(fsts_old[doculect].apply_up(the_syl)))

                    if rec:
                        rec_strs = []
                        for w in rec:
                            if w in inferred_reconstructions:
                                rec_strs.append(r'_*' + w + '_')
                                if under_study:
                                    old_reconstruction_matched = True
                            else:
                                rec_strs.append('*' + w)
                        rec_str = ', '.join(rec_strs)
                        row.append(rec_str)
                    else:
                        row.append('')
                        if doculect in fsts_old and inferred_reconstructions and i == len(langs_under_study) - 1:
                            # forward projection for the language under study
                            fwd_recs = []
                            for w in inferred_reconstructions:
                                fwd_recs.extend(list(fsts_old[doculect].apply_down(w)))
                            fwd_recs = [replace_diacritics_forward(w) for w in set(fwd_recs)]
                            row[-1] = r'≠ †%s' % (', '.join(fwd_recs))

                this_row['old_reconstructions'] = row

                # third row: new reconstructions
                row = []
                inferred_reconstructions, strict_reconstructions = column['new_fst_reconstructions']
                if inferred_reconstructions:
                    rec_str = ', '.join(['*' + w for w in inferred_reconstructions])
                    if not strict_reconstructions:
                        rec_str += '?'
                    this_row['new_reconstruction'] = rec_str
                
                for i in range(len(langs_under_study)):
                    doculect = langs_under_study[i]
                    under_study = i == len(langs_under_study) - 1
                    rec = []
                    if doculect in fsts_new and column['most_common_ipas'][i] != '--':
                        the_syl = replace_diacritics(column['most_common_ipas'][i])
                        rec = list(set(fsts_new[doculect].apply_up(the_syl)))

                    if rec:
                        rec_strs = []
                        for w in rec:
                            if w in inferred_reconstructions:
                                rec_strs.append(r'_*' + w + '_')
                                if i == len(langs_under_study) - 1:
                                    new_reconstruction_matched = True
                            else:
                                rec_strs.append('*' + w)
                        rec_str = ', '.join(rec_strs)
                        row.append(rec_str)
                    else:
                        row.append('')
                        if doculect in fsts_new and inferred_reconstructions and i == len(langs_under_study) - 1:
                            # forward projection for the language under study
                            fwd_recs = []
                            for w in inferred_reconstructions:
                                fwd_recs.extend(list(fsts_new[doculect].apply_down(w)))
                            fwd_recs = [replace_diacritics_forward(w) for w in set(fwd_recs)]
                            row[-1] = r'≠ †%s' % (', '.join(fwd_recs))

                this_row['new_reconstructions'] = row

                this_row['status'] = ''
                if old_reconstruction_matched and not new_reconstruction_matched:
                    this_row['status'] = 'frowning'
                elif (not old_reconstruction_matched) and new_reconstruction_matched:
                    this_row['status'] = 'smiling'

                rows.append(this_row)

            this_section['rows'] = rows
            json_chapters[pos].append(this_section)

    return {'chapters': json_chapters}
