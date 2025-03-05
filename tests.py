import glob
import os
import shutil
import unittest
from bdd import BDD, BDDNode
from gmpy2 import mpq

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
        bdd1.generateDot("0")
        self.assertEqual(bdd1, bdd_XandY)

    def test_build_X_or_Y(self):
        # example X or Y reduced
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
        bdd1.generateDot("1")
        self.assertEqual(bdd1, bdd_XorY)
        
    def test_build_X(self):
        #example X
        expression = "X"
        variables = ["X"]
        bdd = BDD(expression, variables, build_new=False)
        root = BDDNode(var = "X")
        leaf_true = BDDNode(value=True)
        leaf_false = BDDNode(value=False)
        root.positive_child = leaf_true
        root.negative_child = leaf_false
        bdd.root = root
        
        bdd1 = BDD("X", ["X"])
        bdd1.generateDot("2")
        
        self.assertEqual(bdd, bdd1) 
        #leafs need to be the same object as the ones safed in BDD
        self.assertEqual(id(bdd1.root.negative_child), id(bdd1.leafs[False]))
        self.assertEqual(id(bdd1.root.positive_child), id(bdd1.leafs[True]))
        
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
        root.positive_child.parents.append(root)
        root.negative_child = child_2
        root.negative_child.parents.append(root)
        child_1.positive_child = child_6
        child_1.positive_child.parents.append(child_1)
        child_1.negative_child = child_3
        child_1.negative_child.parents.append(child_1)
        child_2.positive_child = child_4
        child_2.positive_child.parents.append(child_2)
        child_2.negative_child = child_5
        child_2.negative_child.parents.append(child_2)
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
        root.positive_child.parents.append(root)
        root.negative_child = child_y
        root.negative_child.parents.append(root)
        child_y.positive_child = child_z
        child_y.positive_child.parents.append(child_y)
        child_y.negative_child = child_z
        child_y.negative_child.parents.append(child_y)
        child_z.positive_child = child_t
        child_z.positive_child.parents.append(child_z)
        child_z.negative_child = child_f2
        child_z.negative_child.parents.append(child_z)
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
        
        bdd1.generateDot("test1")
        bdd2.generateDot("test2")

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
        #see generated dot for visulization of BDD
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
        bdd1.generateDot("example_duplicate_subtree")
        
        #duplicate subtrees have been reduced 
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
        
    def test_negate(self):
        #example X
        bdd1 = BDD("X", ["X"])
        
        #example not X
        expression2 = "not X"
        variables2 = ["X"]
        bdd2 = BDD(expression2, variables2, build_new=False)
        root2 = BDDNode(var = "X")
        leaf_true2 = BDDNode(value=True)
        leaf_false2 = BDDNode(value=False)
        root2.positive_child = leaf_false2
        root2.negative_child = leaf_true2
        bdd2.root = root2
        
        bdd1_n = bdd1.negate()
        self.assertEqual(bdd1_n, bdd2)
        
    def test_apply_or(self):
        #example X and Y reduced
        bdd1.root = root1        
        expression_1 = "X and Y"
        variables_1 =["X", "Y"]
        bdd1 = BDD(expression_1, variables_1, build_new=False)
        root1 = BDDNode(var = "X")
        child1 = BDDNode(var ="Y")
        leaf_true1 = BDDNode(value=True)
        leaf_false1 = BDDNode(value=False)
        root1.positive_child = child1
        root1.negative_child = leaf_false1
        child1.positive_child = leaf_true1
        child1.negative_child = leaf_false1
        bdd1.root = root1
        
        #example X
        expression2 = "X"
        variables2 = ["X"]
        bdd2 = BDD(expression2, variables2, build_new=False)
        root2 = BDDNode(var = "X")
        leaf_true2 = BDDNode(value=True)
        leaf_false2 = BDDNode(value=False)
        root2.positive_child = leaf_true2
        root2.negative_child = leaf_false2
        bdd2.root = root2
        
        #example Y
        expression3 = "Y"
        variables3 = ["Y"]
        bdd3 = BDD(expression3, variables3, build_new=False)
        root3 = BDDNode(var = "Y")
        leaf_true3 = BDDNode(value=True)
        leaf_false3 = BDDNode(value=False)
        root3.positive_child = leaf_true3
        root3.negative_child = leaf_false3
        bdd3.root = root3
        
        self.assertEqual(bdd1, BDD.apply_binary_operand(bdd2, bdd3, "and", ["X", "Y"]))
        

    def test_apply_or(self):
        # example X or Y reduced
        expression1 = "X or Y"
        variables1 = ["X", "Y"]
        bdd1 = BDD(expression1, variables1, build_new=False)
        root1 = BDDNode(var="X")
        child1 = BDDNode(var="Y")
        leaf_true1 = BDDNode(value=True)
        leaf_false1 = BDDNode(value=False)
        root1.positive_child = leaf_true1
        root1.negative_child = child1
        child1.positive_child = leaf_true1
        child1.negative_child = leaf_false1
        bdd1.root = root1 
        
        #example X
        expression2 = "X"
        variables2 = ["X"]
        bdd2 = BDD(expression2, variables2, build_new=False)
        root2 = BDDNode(var = "X")
        leaf_true2 = BDDNode(value=True)
        leaf_false2 = BDDNode(value=False)
        root2.positive_child = leaf_true2
        root2.negative_child = leaf_false2
        bdd2.root = root2
        
        #example Y
        expression3 = "Y"
        variables3 = ["Y"]
        bdd3 = BDD(expression3, variables3, build_new=False)
        root3 = BDDNode(var = "Y")
        leaf_true3 = BDDNode(value=True)
        leaf_false3 = BDDNode(value=False)
        root3.positive_child = leaf_true3
        root3.negative_child = leaf_false3
        bdd3.root = root3
        
        self.assertEqual(bdd1, BDD.apply_binary_operand(bdd2, bdd3, "or", ["X", "Y"]))
        
    
    def test_copy(self):
        # example X or Y reduced
        expression1 = "X or Y"
        variables1 = ["X", "Y"]
        bdd1 = BDD(expression1, variables1, build_new=False)
        root1 = BDDNode(var="X")
        child1 = BDDNode(var="Y")
        leaf_true1 = BDDNode(value=True)
        leaf_false1 = BDDNode(value=False)
        root1.positive_child = leaf_true1
        root1.negative_child = child1
        child1.positive_child = leaf_true1
        child1.negative_child = leaf_false1
        bdd1.root = root1
        
        bdd2 = bdd1.copy_bdd()
        self.assertEqual(bdd1, bdd2)

    def test_renaming(self):
        # example X or Y reduced
        expression1 = "X or Y"
        variables1 = ["X", "Y"]
        bdd1 = BDD(expression1, variables1, build_new=False)
        root1 = BDDNode(var="X")
        child1 = BDDNode(var="Y")
        leaf_true1 = BDDNode(value=True)
        leaf_false1 = BDDNode(value=False)
        root1.positive_child = leaf_true1
        root1.negative_child = child1
        child1.positive_child = leaf_true1
        child1.negative_child = leaf_false1
        bdd1.root = root1
        
        # example renamed X or Y reduced
        expression2 = "X_ or Y_"
        variables2= ["X_", "Y_"]
        bdd2 = BDD(expression2, variables2, build_new=False)
        root2 = BDDNode(var="X", is_alt=True)
        child2 = BDDNode(var="Y", is_alt=True)
        leaf_true2 = BDDNode(value=True, is_alt=True)
        leaf_false2 = BDDNode(value=False, is_alt=True)
        root2.positive_child = leaf_true2
        root2.negative_child = child2
        child2.positive_child = leaf_true2
        child2.negative_child = leaf_false2
        bdd2.root = root2
        
        self.assertEqual(bdd1.rename_variables(), bdd2)
#
#    def test_breadth_first_bottom_up_search(self):
#        bdd1 = BDD("((not X1 or X2) and (not X2 or X1)) and ((not X4 or X3))", ["X2", "X3", "X4", "X1"])
#        bdd1.generateDot("BFBU_search")
#        BFBU_search = []
#        n = BDD.get_parents_of_pos_and_neg_leaf(bdd1)
#        while n: 
#            BFBU_search.append(n.variable)
#            n = BDD.get_parents_of_pos_and_neg_leaf(bdd1)
#        #see generated Dot for correct order
#        correct_order = ["X1", "X1", "X4", "X4", "X3", "X3", "X2"]
#        
#        self.assertEqual(BFBU_search, correct_order)
#            
            
    def test_probabilities(self):
        bdd = BDD("((not X1 or X2) and (not X2 or X1)) and ((not X4 or X3))", ["X2", "X3", "X4", "X1"])
        p = {
        "X1": [mpq(0.2), mpq(0.3), mpq(0.4), mpq(0.1)],
        "X2": [mpq(0.15), mpq(0.6), mpq(0.13), mpq(0.12)],
        "X3": [mpq(0.23), mpq(0.17), mpq(0.2), mpq(0.4)],
        "X4": [mpq(0.25), mpq(0.31), mpq(0.27), mpq(0.17)]
        }
        
        bdd.set_probabilities(p)
        sum = bdd._BDD__sum_all_probability_paths()
        self.assertAlmostEqual(float(sum), 1)

if __name__ == '__main__':
    delete_all_files_from_out()
    unittest.main()