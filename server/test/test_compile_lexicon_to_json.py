import unittest

from server import compile_lexicon_to_json


class TestGetSharedReconstructions(unittest.TestCase):
    def test_strict_ancestor(self):
        recs_a = {'dzit', 'dzut'}
        recs_b = {'dzut', 'tsut'}
        recs_c = {'dzut', 'dzud'}
        shared, strict = compile_lexicon_to_json.get_shared_reconstructions(
            [recs_a, recs_b, recs_c]
        )
        self.assertTrue(strict)
        self.assertEqual(['dzut'], shared)

    def test_non_strict_ancestor(self):
        recs_a = {'dzit', 'dzut'}
        recs_b = {'dzut', 'tsut'}
        recs_c = {'dzud'}  # dzut isn't a possible reconstruction in lect c
        shared, strict = compile_lexicon_to_json.get_shared_reconstructions(
            [recs_a, recs_b, recs_c]
        )
        self.assertFalse(strict)
        self.assertEqual(['*dzut'], shared)
