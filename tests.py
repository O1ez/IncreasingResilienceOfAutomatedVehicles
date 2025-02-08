
import glob
import os
import shutil
import unittest
from bdd import BDD, BDDNode

# deletes all files from the out folder 
def delete_all_files_from_out():
    files = glob.glob('out/*')
    for obj in files:
        if os.path.isfile(obj):
            os.remove(obj)
        elif os.path.isdir(obj):
            shutil.rmtree(obj)

class TestCalculations(unittest.TestCase):
    assignments1 = ({"X" : False, "Y" :True}, {"X" : False, "Y" :False})
    delete_all_files_from_out()
    
    #BDDNode
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
        
    def test_build_X_and_Y(self):
        #example X and Y reduced
        expression_X_and_Y = "X and Y"
        variables_X_Y =["X", "Y"]
        bdd_XandY = BDD(expression_X_and_Y, variables_X_Y, build_new=False)
        root = BDDNode(var = "X")
        child = BDDNode(var ="Y")
        leaf_true = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = child
        root.negative_child = leaf_false
        child.positive_child = leaf_true
        child.negative_child = leaf_false
        bdd_XandY.root = root
        
        bdd1 = BDD("X and Y", ["X", "Y"])
        bdd1.reduce()
        self.assertEqual(bdd1, bdd_XandY)
        
    def test_build_X(self):
        #example X
        expression_X = "X"
        variables_X = ("X")
        bdd_X = BDD(expression_X, variables_X, build_new=False)
        root = BDDNode(var = "X")
        leaf_true = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = leaf_true
        root.negative_child = leaf_false
        bdd_X.root = root
        
        bdd = BDD("X", ("X"))
        bdd.reduce()
        
        self.assertEqual(bdd, bdd_X) 
        
    def test_reduce_merge_leafs(self):
        #example X and Y with merged leafs
        bdd1 = BDD("X and Y", ["X", "Y"], build_new=False)
        root = BDDNode(var = "X")
        child_1 = BDDNode(var ="Y")
        child_2 = BDDNode(var = "Y")
        child_3 = BDDNode(value=False)
        child_4 = BDDNode(value=True)
        root.positive_child = child_1
        root.negative_child = child_2
        child_1.positive_child = child_4
        child_1.negative_child = child_3
        child_2.positive_child = child_3
        child_2.negative_child = child_3
        bdd1.root = root 
        
        #example X and Y unreduced
        bdd2 = BDD("X and Y", ["X", "Y"], build_new=False)
        root = BDDNode(var = "X")
        child_1 = BDDNode(var ="Y")
        child_2 = BDDNode(var = "Y")
        child_3 = BDDNode(value=False)
        child_4 = BDDNode(value=False)
        child_5 = BDDNode(value=False)
        child_6 = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = child_1
        root.negative_child = child_2
        child_1.positive_child = child_6
        child_1.negative_child = child_3
        child_2.positive_child = child_4
        child_2.negative_child = child_5
        bdd2.root = root
        bdd2._BDD__merge_leafs(bdd2.root)
        
        self.assertEqual(bdd1, bdd2)
        
    def test_reduce_remove_equivalent_child_nodes(self):
        #example X and Y without removed equivalent child nodes
        # x
        #---y
        #   ____ |
        #   ---- z
        #        ---- 0
        #        ____ 1    
        #___0
        
        bdd1 = BDD("X and Z", ["X", "Y", "Z"], build_new=False)
        root = BDDNode(var = "X")
        child_y = BDDNode(var ="Y")
        child_z = BDDNode(var="Z")
        child_f1 = BDDNode(value = False)
        child_f2 = BDDNode(value = False)
        child_t = BDDNode(value=True)
        root.positive_child = child_f1
        root.negative_child = child_y
        child_y.positive_child = child_z
        child_y.negative_child = child_z
        child_z.positive_child = child_t
        child_z.negative_child = child_f2
        bdd1.root = root
        
        #removed y
        bdd2 = BDD("X and Z", ["X", "Y", "Z"], build_new=False)
        root = BDDNode(var = "X")
        child_z = BDDNode(var="Z")
        child_f1 = BDDNode(value = False)
        child_f2 = BDDNode(value = False)
        child_t = BDDNode(value=True)
        root.positive_child = child_f1
        root.negative_child = child_z
        child_z.positive_child = child_t
        child_z.negative_child = child_f2
        bdd2.root = root

        bdd1._BDD__remove_equivalent_child_nodes(bdd1.root)
        self.assertEqual(bdd1, bdd2)
        
    def test_reduce_remove_equivalent_child_nodes_root(self):
        bdd1 = BDD("X and Y", ["X", "Y"], build_new=False)
        root = BDDNode(var = "X")
        child_y = BDDNode(var ="Y")
        child_f = BDDNode(value=False)
        child_t = BDDNode(value=True)
        root.positive_child = child_y
        root.negative_child = child_y
        child_y.positive_child = child_t
        child_y.negative_child = child_f
        bdd1.root = root
        
        bdd2 = BDD("X and Y", ["X", "Y"], build_new=False)
        root = BDDNode(var = "Y")
        child_f = BDDNode(value=False)
        child_t = BDDNode(value=True)
        root.positive_child = child_t
        root.negative_child = child_f
        bdd2.root = root
        
        bdd1._BDD__remove_equivalent_child_nodes(bdd1.root)
        bdd1.generateDot("a")
        bdd2.generateDot("b")
        self.assertEqual(bdd1, bdd2)   
        
if __name__ == '__main__':
    unittest.main()