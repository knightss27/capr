# ("a b c", "A B C", "a c", {"a": "ab", "c": "bc"}) -> ["a c", "AB BC"]
# ("a", "A", "a c", {"a": "ab", "c": "bc"}) -> ["a", "A"]
# presumes that every actual structure schema is the substring of some maximal schema
def merge_phonemes(old_schema, old_tokens, new_max_schema, rules):
    # convert the old content to a dictionary
    breakup_old_schema = old_schema.split(' ')
    breakup_old_tokens = old_tokens.split(' ')

    try:
        assert(len(breakup_old_schema) == len(breakup_old_tokens))
    except:
        raise ValueError('Something is extremely wrong! "%s", "%s"' % (old_schema, old_tokens))
        return('', '')

    old_dict=dict()
    for i in range(len(breakup_old_schema)):
        old_dict[breakup_old_schema[i]] = breakup_old_tokens[i]

    # calculate the output
    breakup_new_max_schema = new_max_schema.split(' ')
    output = []

    # try to calculate the result of merging for every item of the maximal new structure schema
    for s in breakup_new_max_schema:
        output_token = ''
        for ss in rules[s]:
            if ss in old_dict:
                letter = old_dict[ss]
                if '/' in letter:
                    letter = letter.split('/')[1]
                output_token += letter
        # add to output if the result is non-empty
        if output_token:
            output += [(s, output_token)]

    output_indices = ' '.join(o[0] for o in output)
    output_tokens = ' '.join(o[1] for o in output)
    return (output_indices, output_tokens)
