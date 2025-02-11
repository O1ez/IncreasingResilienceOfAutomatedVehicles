
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
            
    #tests made:
    # Node:
    # isLeaf()
    # copyNode()
    # build() in various ways
    # 
    # BDD:
    # reduce Leafs
    # reduce common children

    
    

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
        
    def test_node_equals_false(self):
        # x and y bdd
        root = BDDNode(var = "X")
        child = BDDNode(var ="Y")
        leaf_true = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = child
        root.negative_child = leaf_false
        child.positive_child = leaf_true
        child.negative_child = leaf_false
        
        # x or y bdd
        root1 = BDDNode(var = "X")
        child1 = BDDNode(var ="Y")
        leaf_true1 = BDDNode(value=True)
        leaf_false1 = BDDNode(value=False)
        root1.positive_child = leaf_true1
        root1.negative_child = child1
        child1.positive_child = leaf_true1
        child1.negative_child = leaf_false1
        
        self.assertNotEqual(root, root1)
        
    def test_node_equals_true(self):
        root = BDDNode(var = "X")
        child = BDDNode(var ="Y")
        leaf_true = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = child
        root.negative_child = leaf_false
        child.positive_child = leaf_true
        child.negative_child = leaf_false
        
        root1 = BDDNode(var = "X")
        child1 = BDDNode(var ="Y")
        leaf_true1 = BDDNode(value=True)
        leaf_false1 = BDDNode(value=False)
        root1.positive_child = child1
        root1.negative_child = leaf_false1
        child1.positive_child = leaf_true1
        child1.negative_child = leaf_false1
        
        self.assertEqual(root, root1)
        
        
    def test_copy_node(self):
        node1 = BDDNode(var = "X")
        node1.is_alt = False
        self.assertEqual(node1, node1.copy_node(False))
        
        node2 = BDDNode(var = "Y")
        node2.is_alt = True
        self.assertEqual(node2, node2.copy_node(False))
        
        node3 = BDDNode(value=False)
        self.assertEqual(node3, node3.copy_node(False))
        
        
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

    def test_build_X_or_Y(self):
        # example X and Y reduced
        expression_X_or_Y = "X or Y"
        variables_X_Y = ["X", "Y"]
        bdd_XorY = BDD(expression_X_or_Y, variables_X_Y, build_new=False)
        root = BDDNode(var="X")
        child = BDDNode(var="Y")
        leaf_true = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = leaf_true
        root.negative_child = child
        child.positive_child = leaf_true
        child.negative_child = leaf_false
        bdd_XorY.root = root

        bdd1 = BDD("X or Y", ["X", "Y"])
        bdd1.reduce()
        self.assertEqual(bdd1, bdd_XorY)
        
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
        self.assertEqual(bdd1, bdd2)   
        
    def test_reduce_remove_duplicate_subgraph(self):
        bdd1 = BDD("", ["X", "Y", "Z"], build_new=False)
        root1 = BDDNode(var = "X")
        child_y1 = BDDNode(var ="Y")
        child_y2 = BDDNode(var ="Y")
        child_z1 = BDDNode(var="Z")
        child_z2 = BDDNode(var="Z")
        child_z3 = BDDNode(var="Z")
        child_z4 = BDDNode(var="Z")
        leaf_f = BDDNode(value=False)
        leaf_t = BDDNode(value=True)
        root1.negative_child = child_y1
        root1.positive_child = child_y2
        bdd1.root = root1
        #duplicate 1
        child_y1.negative_child = child_z1
        child_y1.positive_child = child_z2
        child_z1.negative_child = leaf_f
        child_z1.positive_child = leaf_t
        child_z2.negative_child = leaf_t
        child_z2.positive_child = leaf_f
        #duplicate 2
        child_y2.negative_child = child_z3
        child_y2.positive_child = child_z4
        child_z3.negative_child = leaf_f
        child_z3.positive_child = leaf_t
        child_z4.negative_child = leaf_t
        child_z4.positive_child = leaf_f
        
        bdd2 = BDD("", ["X", "Y", "Z"], build_new=False)
        root2 = BDDNode(var = "X")
        child2_y1 = BDDNode(var ="Y")
        child2_z1 = BDDNode(var="Z")
        child2_z2 = BDDNode(var="Z")
        leaf2_f = BDDNode(value=False)
        leaf2_t = BDDNode(value=True)
        root2.negative_child = child2_y1
        root2.positive_child = child2_y1
        #duplicate only once
        child2_y1.negative_child = child2_z1
        child2_y1.positive_child = child2_z2
        child2_z1.negative_child = leaf2_f
        child2_z1.positive_child = leaf2_t
        child2_z2.negative_child = leaf2_t
        child2_z2.positive_child = leaf2_f
        bdd2.root = root2
        
        bdd1._BDD__remove_duplicate_subgraph(bdd1.root, [])
        self.assertEqual(bdd1, bdd2)
        
if __name__ == '__main__':
    unittest.main()