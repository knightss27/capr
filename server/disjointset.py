class DisjointSet():
    '''This works like a disjoint set internally, but the operations are
    somewhat weird, as add() plays both the role of adding a new set and of
    merging, and there is (was) no way to find aside from accessing the
    internals of the data structure. This is still WIP.'''
    def __init__(self):
        self._leader = {}  # maps a member to the group's leader
        self.group = {}  # maps a group leader to the group (which is a set)

    def add(self, a, b):
        leader_a = self._leader.get(a)
        leader_b = self._leader.get(b)
        if leader_a is None:
            if leader_b is None:
                self.group[a] = {a, b}
                self._leader[a] = self._leader[b] = a
            else:
                self.add(b, a)
        else:
            if leader_b is None:
                self.group[leader_a].add(b)
                self._leader[b] = leader_a
            else:
                if leader_a == leader_b:
                    return  # nothing to do

                group_a = self.group[leader_a]
                group_b = self.group[leader_b]
                if len(group_a) < len(group_b):
                    self.add(b, a)
                else:
                    # move B's group to A's group
                    group_a |= group_b
                    del self.group[leader_b]
                    for k in group_b:
                        self._leader[k] = leader_a

    def get(self, elt):
        return self.group[self._leader[elt]]
