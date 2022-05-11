#!/usr/bin/python
# Compile Burmish lexicon
# Dependencies: Python ICU; Parsy
# Usage: Unix-ish

# Basic imports
import sys
import re
from functools import reduce
from foma import FST

# Lingpy-ish imports
from segments import Profile, Tokenizer

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Convert Old Burmese reconstruction from the TSV format to the format to be displayed
# 55 → H
# 53 → X
# 22 → Ø
# consonant4 → Ø
# no tone → error
def print_reconstruction(text, formatting = None, error_text = None):
    if re.search('[^ptk]⁵⁵$', text):
        return (formatting or '%s') % (text[:-2] + 'H')
    elif re.search('[^ptk]⁵³$', text):
        return (formatting or '%s') % (text[:-2] + 'X')
    elif re.search('[^ptk]²²$', text):
        return (formatting or '%s') % (text[:-2])
    elif re.search('[ptksc]⁴$', text):
        return (formatting or '%s') % (text[:-1])
    else:
        return (error_text or '[PBurm tone notation not understood: %s]') % text

# Convert a piece of text to its component syllables
# If there is alrady "◦" or a space, use it to separate them
# Otherwise, separate the tone letters other letters
def syllabize(text):
    split_result = re.split(r'([ ◦¹²³⁴⁵]+)', text)
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

# emphasize_syllable("mi ma mu", 1) → "mi<ma>mu"
def emphasize_syllable(text, syllable_index, usual_formatting = None, emphatic_formatting = None):
    syllables = syllabize(text)
    l = len(syllables)
    result = ''
    for i in range(l):
        if i == syllable_index:
            result = result + (emphatic_formatting or '<%s>') % syllables[i]
        else:
            result = result + (usual_formatting or '%s') % syllables[i]
    return result

def transform_glottality_burmish(l):
    new_l = []
    glottality = False
    for s in l:
        if '\U00000330' in s: # right notation: under tilde
            glottality = True
            new_l += [s.replace('\U00000330', '')]
        elif '\U00000331' in s: # wrong notation: under macron 
            glottality = True
            new_l += [s.replace('\U00000331', '')]
        else:
            new_l += [s]
    if glottality:
        new_l[0] = 'ˀ' + new_l[0]
    return new_l

doculects = ['Old_Burmese', 'Rangoon', 'Achang_Longchuan', 'Xiandao', 'Atsi', 'Bola', 'Lashi', 'Maru']
id_of_doculect = {doculects[i]: i for i in range(len(doculects))}

# Whether a language gets its orthoprofile by traditional method or transducers (filename)
orthoprofile_transducer = ['burmese', False, False, False, False, False, False, False]

orthoprofile_filenames = ['profile-Written_Burmese.tsv', 'profile-Rangoon.tsv', 'profile-Achang.tsv', 'profile-Xiandao.tsv', 'profile-Atsi.tsv', 'profile-Bola.tsv', 'profile-Lashi.tsv', 'profile-Maru.tsv']
tokenizers = [Tokenizer(profile = Profile.from_file('orthoprofiles/' + fn)) for fn in orthoprofile_filenames]

transducer = {}
transducer_template = {}

def burmish_parse(w, language):
    transducer_name = orthoprofile_transducer[id_of_doculect[language]]
    if transducer_name:
        # Do it the new way, by transducer-based thingie
        # Check if transducers are present
        if transducer_name not in transducer:
            transducer[transducer_name] = FST.load('../reconstruct/' + transducer_name + '-ortho.bin')
            transducer_template[transducer_name] = FST.load('../reconstruct/' + transducer_name + '-ortho-template.bin')

        syllabized_w = syllabize(w)
        # parse every syllable, now every syllable contains
        result_tokens = []
        result_structure = []
        for syl in syllabized_w:
            res = list(transducer[transducer_name].apply_down(syl))
            if res:
                result_tokens += [res[0]]
                result_structure += [list(transducer_template[transducer_name].apply_down(syl))[0]]
            else:
                result_tokens = ['�']
                result_structure += ['�']
        return (' + '.join(result_tokens), ' + '.join(result_structure))

    tokenizer = tokenizers[id_of_doculect[language]]
    def parse_syllable(syl):
        tokens = tokenizer(syl, column='CLPA').split(' ')
        structure = tokenizer(syl, column='Structure').split(' ')
        # add glottal stop initially
        if structure[0] != 'i':
            tokens = ['/ʔ'] + tokens
            structure = ['i'] + structure
        # apply glottality transformation
        tokens = transform_glottality_burmish(tokens)
        return (' '.join(tokens), ' '.join(structure))

    syllabized_w = syllabize(w)
    # parse every syllable, now every syllable contains
    result_tokens = []
    result_structure = []
    for syl in syllabized_w:
        token, structure = parse_syllable(syl)
        result_tokens += [token]
        result_structure += [structure]
    return (' + '.join(result_tokens), ' + '.join(result_structure))
