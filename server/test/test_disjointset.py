import unittest

from server.disjointset import DisjointSet


class TestDisjointSet(unittest.TestCase):
    def test_add_one_element(self):
        ds = DisjointSet()
        ds.add(1, 1)
        self.assertEqual({1}, ds.get(1))

    def test_add_several_disjoint_elements(self):
        ds = DisjointSet()
        ds.add(1, 1)
        ds.add(2, 2)
        self.assertEqual({1}, ds.get(1))
        self.assertEqual({2}, ds.get(2))

    def test_add_several_joint_elements(self):
        ds = DisjointSet()
        ds.add(1, 1)
        ds.add(2, 1)
        self.assertEqual({1, 2}, ds.get(1))
        self.assertEqual({1, 2}, ds.get(2))
