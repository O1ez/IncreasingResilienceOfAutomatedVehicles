from __future__ import annotations
from typing import Optional
from copy import deepcopy
from gmpy2 import mpq

class BDDNode:
    def __init__(self, var=None, negative_child: Optional[BDDNode] = None, negative_probability: mpq = None, positive_child: Optional[BDDNode] = None, positive_probability: mpq = None, value=None, assignment: Optional[list[dict]] = None, is_alt = False):
        self.var = var  # The variable for decision (None for terminal nodes)
        self.negative_child = negative_child
        self.negative_probability = negative_probability
        self.positive_child = positive_child
        self.positive_probability = positive_probability
        self.value = value  # Terminal value (True or False for leaf nodes)
        self.is_alt = is_alt
        if assignment is None:
            self.assignment = []
        else:
            self.assignment = assignment
        self.drawn = False

    def isLeaf(self):
        # Check if the node is a terminal node (leaf with True/False)
        return self.value is not None
    
    def hasChildren(self):
        return self.negative_child or self.positive_child

    def reduce(self, overarching_tree: BDD):
        temp_bdd = BDD(overarching_tree.expression, overarching_tree.variables, False)
        temp_bdd.root = self
        temp_bdd.reduce()
    
    #TODO: replace copy node in BDDNode   
    def __copy_node(self, replacer: str) -> BDDNode:
        var = None
        value = None
        if self.isLeaf():
            value = self.value
        else:
            var = self.var + replacer
        node_assignment_copy = self.assignment.copy()
        for i in range(len(node_assignment_copy)):
            node_assignment_copy[i] = {k+replacer: v for k, v in node_assignment_copy[i].items()}
        return BDDNode(var = var, value=value, assignment=node_assignment_copy)

    def __eq__(self, other):
        if other is None or not isinstance(other, BDDNode):
            return False
        if self.isLeaf() and other.isLeaf():
            assignments_match = True
            for dic in self.assignment:
                if dic not in other.assignment:
                    assignments_match = False
                    break
            return self.value == other.value and assignments_match
        return (
                self.var == other.var and
                self.negative_child == other.negative_child and
                self.positive_child == other.positive_child
        )

    def __hash__(self):
        # Hash für Leaf-Nodes basierend auf ihrem Wert, ansonsten auf (var, left, right)
        if self.isLeaf():
            return hash(self.value)
        return hash((self.var, self.negative_child, self.positive_child))
    
    def __copy__(self):
        return type(self)(self.var, self.negative_child, self.positive_child, self.value)
    
    def __deepcopy__(self, memo): # memo is a dict of id's to copies
        id_self = id(self)        # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.var, memo), 
                deepcopy(self.negative_child, memo),
                deepcopy(self.positive_child, memo),
                deepcopy(self.negative_probability, memo),
                deepcopy(self.positive_probability, memo),
                deepcopy(self.value, memo),)
            memo[id_self] = _copy
        return _copy
