
import unittest
from bdd import BDD, BDDNode

class TestCalculations(unittest.TestCase):
    
    assignments1 = ({"X" : False, "Y" :True}, {"X" : False, "Y" :False})

    def test_is_leaf(self):
        leaf = BDDNode(value = False)
        self.assertTrue(leaf.isLeaf())
        
        leaf.variable = "X"
        self.assertFalse(leaf.isLeaf())
        
        leaf.value = None
        self.assertFalse(leaf.isLeaf())
        
    def test_copy_node(self):
        node1 = BDDNode(var = "X", assignments=self.assignments1)
        child1 = BDDNode(var = "Y")
        child2 = BDDNode(var= "Y")
        node1.negative_child = child1
        node1.positive_child = child2
        

if __name__ == '__main__':
    unittest.main()