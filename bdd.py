from __future__ import annotations
from collections import deque
import operator
from typing import Optional
import re
import os
import glob
import shutil
import boolean_parser
from gmpy2 import mpq
import pyparsing as pp
from sqlalchemy.sql.operators import is_associative
from collections import defaultdict
import parser


ops_lookup = {"and": operator.and_, "or": operator.or_}

# deletes all files from the out folder 
def delete_all_files_from_out():
    files = glob.glob('out/*')
    for obj in files:
        if os.path.isfile(obj):
            os.remove(obj)
        elif os.path.isdir(obj):
            shutil.rmtree(obj)


class BDDNode:
    def __init__(self, var: str = None, value: bool = None, is_alt=False,
                parents: list[BDDNode] = None,
                negative_child: Optional[BDDNode] = None,
                negative_probability: dict[BDDNode, mpq] = None,
                positive_child: Optional[BDDNode] = None,
                positive_probability: dict[BDDNode, mpq] = None):

        self.variable = var  #None for leaf nodes
        self.is_alt = is_alt #used to differentiate variables and their renamed counterpart
        self.value = value  #None for nodes with children
        self.parents = [] if parents is None else parents
        self.negative_child = negative_child
        self.negative_probability = {} if negative_probability is None else negative_probability
        self.positive_child = positive_child
        self.positive_probability = {} if positive_probability is None else positive_probability
        self.drawn = False

    def isLeaf(self):
        return self.value is not None and self.variable is None

    def hasChildren(self):
        return self.negative_child or self.positive_child
    
    def isEmpty(self):
        return self.variable is None and self.value is None

    #creates new BDD with this node as root and reduces it
    def reduce(self, overarching_tree: BDD):
        temp_bdd = BDD(overarching_tree.expression, overarching_tree.variables, False)
        temp_bdd.root = self
        temp_bdd.reduce()

    def copy_node(self, renaming: bool) -> BDDNode:
        var = None
        value = None
        if self.isLeaf():
            value = self.value
        else:
            var = self.variable
        if self.is_alt:
            renaming = True
        return BDDNode(var=var, 
                        value=value, 
                        is_alt=renaming, 
                        negative_probability=self.negative_probability, 
                        positive_probability=self.positive_probability)
    
    def remove_parent_link_leafs(self):
        if self.negative_child.isLeaf():
            found_parent = next((parent for parent in self.negative_child.parents if id(parent) == id(self)), None)
            if found_parent:
                self.negative_child.parents.remove(found_parent)
        else: self.negative_child.remove_parent_link_leafs()
        
        if self.positive_child.isLeaf():
            found_parent = next((parent for parent in self.positive_child.parents if id(parent) == id(self)), None)
            if found_parent:
                self.positive_child.parents.remove(found_parent)
        else: self.positive_child.remove_parent_link_leafs()
        

    def __eq__(self, other):
        if other is None or not isinstance(other, BDDNode):
            return False
        if self.isLeaf() and other.isLeaf():
            return self.value == other.value 
        return (
                self.variable == other.variable and
                self.negative_child == other.negative_child and
                self.positive_child == other.positive_child
        )

    def __hash__(self):
        # Hash für Leaf-Nodes basierend auf ihrem Wert, ansonsten auf (var, left, right)
        if self.isLeaf():
            return hash(self.value)
        return hash((self.variable, self.negative_child, self.positive_child))
#______________________________________________________________________________________________________________________________


class BDD:
    def __init__(self, expression: str, variables: list[str], build_new=True):
        self.variables = variables  # List of variables (alt vars are stored with "_" after the name)
        self.expression = expression
        self.leafs = {False: BDDNode(value=False), True: BDDNode(value=True)}
        self.root = None
        self.probabilities_set = False
        self.renamed = False
        if build_new:
            self.satisfiable = self.build_new()
        
        
    def build_new(self):
        ops = parser.parse_line(self.expression)
        #expressions sometimes get parsed as a single list in a list
        #--> extract inner list
        #if a bdd is build from only one variable, the variable needs to be extracted from list
        while (isinstance(ops, list) and len(ops) == 1) and (isinstance(ops[0], list) or isinstance(ops[0], str)):
            ops = ops[0]
        root = self.build(ops)
        self.root = root
        satisfiable = not (self.root.isLeaf() and self.root.value == False)
        return satisfiable

    def build(self, ops) -> BDDNode:
        #case only variable
        if (isinstance(ops, str)):
            root = BDDNode(var = ops)
            root.negative_child = self.leafs[False]
            root.positive_child = self.leafs[True]
            self.leafs[False].parents.append(root)
            self.leafs[True].parents.append(root)
            #root.negative_child = BDDNode(value=False)
            #root.negative_child.parents.append(root)
            #root.positive_child = BDDNode(value=True)
            #root.positive_child.parents.append(root)
            return root
        #not case
        elif len(ops) == 2:
            if ops[0] != "not":
                raise Exception("Wrong expression given: "+", ".join(ops))
            root = self.build(ops[1])
            bdd = BDD("", self.variables, False)
            bdd.root = root
            bdd.leafs = self.leafs
            negated_bdd = bdd.negate()
            return negated_bdd.root
        #binary operator case
        elif len(ops) == 3:
            root1 = self.build(ops[0])
            bdd1 = BDD("", self.variables, False)
            bdd1.root = root1
            op = ops[1]
            root2 = self.build(ops[2])
            bdd2 = BDD("", self.variables, False)
            bdd2.root = root2
            
            bdd_sol = self.apply_binary_operand(bdd1, bdd2, op, self.variables)
            self.leafs = bdd_sol.leafs
            return bdd_sol.root
        else: raise Exception("Wrong expression given: "+", ".join(ops)+ " Parentheses not set correctly?")


    def reduce(self):
        if not self.root.hasChildren:
            print("BDD only has root.")
            return False
        self.__merge_leafs(self.root)
        self.__remove_duplicate_subgraph(self.root, mem=[])
        self.__remove_equivalent_child_nodes(self.root)
        
        #hotfix for multiple parents not connected to tree
        self.__clear_parents(self.root)
        self.generateDot("cleared parents")
        self.__set_parents(self.root, [])
        self.generateDot("set parents")

        #print("Reduction done.")

    def __remove_duplicate_subgraph(self, node: BDDNode, mem: list[BDDNode]):
        if node.isLeaf():
            return node
        elif node in mem:
            other_node = mem[mem.index(node)]
            #only replace if its not the same node 
            if id(node) != id(other_node):
                other_node.parents.extend(node.parents)
                node.remove_parent_link_leafs()
            return other_node
        else:
            mem.append(node)
            node.negative_child = self.__remove_duplicate_subgraph(node.negative_child, mem)
            node.positive_child = self.__remove_duplicate_subgraph(node.positive_child, mem)
            return node

    def __merge_leafs(self, node: BDDNode) -> Optional[BDDNode]:
        if node is None:
            raise Exception("unexpected Node is None")
        #if node is leaf return it 
        if node.isLeaf():
            return node

        negative_child = self.__merge_leafs(node.negative_child)
        # if not None, child is a leaf and needs to be replaced with prebuild leaf
        if negative_child is not None and id(negative_child) != id(self.leafs[negative_child.value]):
            if not node in negative_child.parents:
                raise Exception("unexpected")
            negative_child.parents.remove(node)
            leaf = self.leafs[negative_child.value]
            #leaf.parents.extend(node.negative_child.parents)
            node.negative_child = leaf

        positive_child = self.__merge_leafs(node.positive_child)
        if positive_child is not None and id(positive_child) != id(self.leafs[positive_child.value]):
            if not node in positive_child.parents:
                raise Exception("unexpected")
            positive_child.parents.remove(node)
            leaf = self.leafs[positive_child.value]
            #leaf.parents.extend(node.positive_child.parents)
            node.positive_child = leaf
            
        return None
    
    def __remove_equivalent_child_nodes(self, node: BDDNode) -> Optional[BDDNode]:
        if node.isLeaf():
            return
        
        #only go one path if both children are the same but reduce the children first
        if id(node.negative_child) == id(node.positive_child):
            self.__remove_equivalent_child_nodes(node.negative_child)
        else:
            self.__remove_equivalent_child_nodes(node.negative_child)
            self.__remove_equivalent_child_nodes(node.positive_child)

        if id(node.negative_child) == id(node.positive_child):
            #child represents both pos and neg child
            child = node.negative_child
            if node == self.root:
                self.root = child
                child.parents.clear()
            #for every parent node delete old child, add new
            for parent in node.parents:
                if parent.negative_child == node:
                    parent.negative_child = child    
                else:
                    parent.positive_child = child
                child.parents.append(parent)
            node.parents.clear()
            #remove twice because node is parent twice
            while next((parent for parent in child.parents if id(parent) == id(node)), None):
                child.parents.remove(node)
        return
            
    def __clear_parents(self, node: BDDNode):
        node.parents.clear()
        if node.isLeaf():
            return
        self.__clear_parents(node.negative_child)
        self.__clear_parents(node.positive_child)
    
    def __set_parents(self, node: BDDNode, mem: list[BDDNode]):
        if node.isLeaf():
            return
        found = next((n for n in mem if id(n) == id(node)), None)
        if not found:
        #if node not in mem:    
            node.negative_child.parents.append(node)
            node.positive_child.parents.append(node)
            mem.append(node)
            
        self.__set_parents(node.negative_child, mem)
        self.__set_parents(node.positive_child, mem)
        
    """ 
    def __remove_equivalent_child_nodes(self, node: BDDNode) -> Optional[BDDNode]:
        #if and while root is reducable reduce it and set new root
        if node == self.root:
            while self.root.negative_child == self.root.positive_child:
                #both leafs of root have the same value --> formular always false or true
                if self.root.negative_child.isLeaf() and self.root.positive_child.isLeaf():
                    return self.root
                
                self.root = self.root.negative_child
                node = self.root
        
        if node.negative_child is not None:
            child_of_neg_child = self.__remove_equivalent_child_nodes(node.negative_child)
            #if not None, the children of the neg child node are identical -> original negative child needs to get skipped over
            if child_of_neg_child is not None:
                node.negative_child = child_of_neg_child

        if node.positive_child is not None:
            child_of_pos_child = self.__remove_equivalent_child_nodes(node.positive_child)
            #equivalent to negative child
            if child_of_pos_child is not None:
                node.positive_child = child_of_pos_child

        #negative child is same as positive child and said child is returned
        if node.negative_child is not None and node.positive_child is not None and id(node.negative_child) == id(
                node.positive_child):
            return node.negative_child
        
        return None 
        """

    def find_paths(self, target: BDDNode,
                    current_node: BDDNode = None,
                    overall_assignments: list[dict[str, bool]] = None,
                    current_assignments: list[dict[str, bool]] = None,
                    searched_variables: list[str] = None) -> list[dict[str, bool]]:
        #init
        if overall_assignments is None:
            overall_assignments = []
        if current_assignments is None:
            current_assignments = [{}]
        if current_node is None:
            current_node = self.root
        if searched_variables is None:
            searched_variables = self.variables.copy()

        # node is leaf --> target was not found
        if current_node.isLeaf():
            return overall_assignments

        # tree skipped at least one variable -> assignments get copied one sets
        # skipped variable(s) to True the other to false, both are appended
        searched_variables = searched_variables.copy()
        next_var = searched_variables.pop(0)
        while next_var != current_node.variable:
            current_assignments_copies = []
            for assignment in current_assignments:
                assignment_copy = assignment.copy()
                assignment[next_var] = True
                assignment_copy[next_var] = False
                current_assignments_copies.append(assignment_copy)
            current_assignments.extend(current_assignments_copies)
            next_var = searched_variables.pop(0)

        #target found
        if current_node == target:
            overall_assignments.extend(current_assignments)
            return overall_assignments


        #children nodes need to be searched further for target
        current_assignments = [assignment.copy() for assignment in current_assignments]
        for assignment in current_assignments:
            assignment[current_node.variable] = False
        self.find_paths(target, current_node.negative_child, overall_assignments, current_assignments.copy(), searched_variables)
        
        current_assignments = [assignment.copy() for assignment in current_assignments]
        for assignment in current_assignments:
            assignment[current_node.variable] = True
        self.find_paths(target, current_node.positive_child, overall_assignments, current_assignments.copy(), searched_variables)

        return overall_assignments


    #creates a lookup table mapping nodes of bdd1 to corresponding nodes of bdd2 for all non-leaf nodes
    #bdds have to have same variables 
    def make_lookup_table_corr_nodes(self, bdd_from: BDD, bdd_to: BDD) -> dict[BDDNode, list[BDDNode]]:
        if bdd_from.variables != bdd_to.variables:
            raise Exception("Both BDDs have to have the same variable priorization!")
        #automatically creates empty list in every object
        result = defaultdict(list)
        self.__make_lookup_table_corr_nodes_recursive(bdd_from.variables, bdd_from.root, bdd_to.root, result)
        return result
        
        

    #needs roots of bdd_from and bdd_to as first node inputs
    def __make_lookup_table_corr_nodes_recursive(self, variables: list[str], node_from: BDDNode = None, node_to: BDDNode = None, result : dict[BDDNode, list[BDDNode]] = None) -> dict[BDDNode, list[BDDNode]]:
        #leafs are not relevant, don't need to be safed
        if node_from.isLeaf() or node_to.isLeaf():
            return     
        #adds the renaming to variable if it's present
        node_from_var = node_from.variable + "_" if node_from.is_alt else node_from.variable
        node_to_var = node_to.variable + "_" if node_to.is_alt else node_to.variable
        
        #both nodes have the same variable, can be mapped together
        if node_from_var == node_to_var:
            result[node_from].append(node_to)
            self.__make_lookup_table_corr_nodes_recursive(variables, node_from.negative_child, node_to.negative_child, result)
            self.__make_lookup_table_corr_nodes_recursive(variables, node_from.positive_child, node_to.positive_child, result)
        #variables don't match, one graph is skipping at least one node 
        #node from has higher priority, node to skipped a node 
        elif variables.index(node_from_var) < variables.index(node_to_var):
            self.__make_lookup_table_corr_nodes_recursive(variables, node_from.negative_child, node_to, result)
            self.__make_lookup_table_corr_nodes_recursive(variables, node_from.positive_child, node_to, result)
        #node from has lower priority, higher index in variables
        #cannot map node_from to any node, try mapping node_from to both child of node_to
        elif variables.index(node_from_var) > variables.index(node_to_var):
            self.__make_lookup_table_corr_nodes_recursive(variables, node_from, node_to.negative_child, result)
            self.__make_lookup_table_corr_nodes_recursive(variables, node_from, node_to.positive_child, result)

    #makes a copy of BDD and negates it
    def negate(self):
        negated_BDD = self.copy_bdd()
        #negate leaf values
        false_leaf = negated_BDD.leafs[False]
        false_leaf.value = True
        
        true_leaf = negated_BDD.leafs[True]
        true_leaf.value = False

        #switch leafs in dictionary
        negated_BDD.leafs[True] = false_leaf
        negated_BDD.leafs[False] = true_leaf

        negated_BDD.expression = "not (" + negated_BDD.expression + ")"
        return negated_BDD

    @staticmethod
    def apply_binary_operand(BDD1: BDD, BDD2: BDD, operand: str, variable_order: list) -> BDD:
        for var in BDD1.variables:
            if var not in variable_order:
                raise Exception("Variable " + var + " from BDD1 not found in variables.")

        for var in BDD2.variables:
            if var not in variable_order:
                raise Exception("Variable " + var + " from BDD2 not found in variables.")

        if operand not in ops_lookup:
            raise Exception("Operand " + operand + " not supported.")

        united_bdd = BDD(expression="(" + BDD1.expression + ")and(" + BDD2.expression + ")", variables=variable_order,
                        build_new=False)
        united_bdd.root = BDD.__apply_binary_operand_recursion(BDD1.root, BDD2.root, operand, variable_order, united_bdd)
        #united_bdd.generateDot("united_unreduced")
        united_bdd.reduce()
        #united_bdd.generateDot("united_reduced")
        if BDD1.renamed or BDD2.renamed:
            united_bdd.renamed = True
        united_bdd.satisfiable = not (united_bdd.root.isLeaf() and united_bdd.root.value == False)
        return united_bdd

    @staticmethod
    def __apply_binary_operand_recursion(node1: BDDNode, node2: BDDNode, operand: str, variable_order: list[str], united_bdd: BDD) -> BDDNode:
        node1_var = None
        node2_var = None
        if node1.variable:
            #add "_" if var is alt, so it can be looked up in variabole order
            node1_var = node1.variable + "_" if node1.is_alt else node1.variable
            if node1_var not in variable_order:
                raise Exception(f"{node1_var} not in variable order {variable_order}.")
        if node2.variable:
            node2_var = node2.variable + "_" if node2.is_alt else node2.variable
            if node2_var not in variable_order:
                raise Exception(f"{node2_var} not in variable order {variable_order}.")

        # if both nodes are leafs return new leaf with united value
        if node1.isLeaf() and node2.isLeaf():
            value =  ops_lookup[operand](node1.value, node2.value)
            solution = united_bdd.leafs[value]
            return solution

        # if both nodes are of the same variable unite the negative children and positive children of both bdd
        elif node1_var == node2_var:
            solution = BDDNode(var=node1_var, is_alt=node1.is_alt)
            solution.negative_child = BDD.__apply_binary_operand_recursion(node1.negative_child, node2.negative_child, operand, variable_order, united_bdd)
            solution.negative_child.parents.append(solution)
            solution.positive_child = BDD.__apply_binary_operand_recursion(node1.positive_child, node2.positive_child, operand, variable_order, united_bdd)
            solution.positive_child.parents.append(solution)
            if solution.negative_child is None or solution.positive_child is None:
                raise Exception("Children are None")
            #solution.reduce(united_bdd)
            return solution

        # if variables don't match determine higher priority variable and unite children of higher prio variable with
        # lower prio BDD
        else:
            gen = (var for var in variable_order if var == node1_var or var == node2_var)
            higher_variable = next(gen)

            if node1_var == higher_variable:
                higher_prio = node1
                lower_prio = node2
            else:
                higher_prio = node2
                lower_prio = node1

            solution = BDDNode(var=higher_prio.variable, is_alt=higher_prio.is_alt)
            solution.negative_child = BDD.__apply_binary_operand_recursion(higher_prio.negative_child, lower_prio, operand, variable_order, united_bdd)
            solution.negative_child.parents.append(solution)
            solution.positive_child = BDD.__apply_binary_operand_recursion(higher_prio.positive_child, lower_prio, operand, variable_order, united_bdd)
            solution.positive_child.parents.append(solution)
            return solution

    #creates a copy of BDD gives it is_alt attribute
    def rename_variables(self) -> BDD:
        if self.renamed:
            raise Exception("BDD already renamed!")
        renamed_BDD = self.__copy(True)
        renamed_BDD.renamed = True
        return renamed_BDD

    #gives a copy of bdd
    def copy_bdd(self) -> BDD:
        return self.__copy(False)

    def __copy(self, rename: bool) -> BDD:
        expression_copy = self.expression
        if rename:
            var_copy = [var + "_" for var in self.variables.copy()]
            for var in self.variables:
                #replace var in expression if a space follows it
                expression_copy = re.sub(var + " ", var + "_" + " ", expression_copy)
        else:
            var_copy = self.variables.copy()

        
        bdd_copy = BDD(expression_copy, var_copy, build_new=False)
        bdd_copy.root = self.__replace_children_nodes(self.root, {}, rename or self.renamed, bdd_copy.leafs)
        bdd_copy.__merge_leafs(bdd_copy.root)
        return bdd_copy

    def __replace_children_nodes(self, original_node: BDDNode, visited_nodes: dict[BDDNode, BDDNode], is_alt: bool, new_leafs: dict[bool: BDDNode]):      
        #if original node is already copied return copy
        if original_node in visited_nodes:
            node_copy = visited_nodes[original_node]
            return node_copy
        
        #if original node is a leaf use the leafs of new tree as node
        if original_node.isLeaf():
            node_copy = new_leafs[original_node.value]
            visited_nodes[original_node] = node_copy
            return node_copy

        #node has not been copied yet -> copy it, set children and set itself as parent of children
        node_copy = original_node.copy_node(is_alt)
        node_copy.negative_child = self.__replace_children_nodes(original_node.negative_child, visited_nodes, is_alt, new_leafs)
        node_copy.negative_child.parents.append(node_copy)
        node_copy.positive_child = self.__replace_children_nodes(original_node.positive_child, visited_nodes, is_alt,  new_leafs)
        node_copy.positive_child.parents.append(node_copy)
        #map copy of Node to the original node
        visited_nodes[original_node] = node_copy
        return node_copy

    #only use if original and alternative Variables are united
    # TODO: reduce
    def set_probabilities(self, probabilities: dict[str: list[mpq]]):
        root = self.root
        keys = probabilities.keys()
        new_vars = self.remove_alt_variables(self.variables.copy())
        for v in new_vars:
            if v not in keys:
                raise Exception("Variables given in probabilities do not match variables set in BDD")
        if root.isLeaf():
            raise Exception("Tree needs at least one Node that isn't a leaf!")
        #root handled separately because it does not have a parent node
        if not root.is_alt:
            #p of only x
            root.negative_probability[root] = probabilities[root.variable][0] + probabilities[root.variable][2]
            #p of only not x
            root.positive_probability[root] = probabilities[root.variable][1] + probabilities[root.variable][3]
        else:
            #p of only x_
            root.negative_probability[root] = probabilities[root.variable][0] + probabilities[root.variable][1]
            #p of only not x_
            root.positive_probability[root] = probabilities[root.variable][1] + probabilities[root.variable][0]
        self.__set_probabilities_recursion(root, probabilities)
        self.probabilities_set = True
        return

    #helper method for set_probabilities
    #sets probabilities of children for each parent node separately
    def __set_probabilities_recursion(self, current_node: BDDNode, probabilities: dict[str: list[mpq]]):
        # example of table/list:
        # x'\x     0        1
        # 0    [0] 0.2   [1] 0.3
        # 1    [2] 0.4   [3] 0.1

        negative_child = current_node.negative_child
        positive_child = current_node.positive_child

        if not negative_child.isLeaf():
            if not current_node.is_alt and current_node.variable == negative_child.variable:
                #child needs to be alt of current node -> current probability affects alt child probability
                p_list = probabilities[current_node.variable]

                # p = (p not x and not x_) / (p not x)
                negative_child.negative_probability[current_node] = p_list[0] / (p_list[0] + p_list[2])
                # p = (p not x and x_) / (p not x)
                negative_child.positive_probability[current_node] = p_list[2] / (p_list[0] + p_list[2])

            #child is not influenced by current node probability
            else:
                p_list = probabilities[negative_child.variable]
                if not negative_child.is_alt:
                    # p = not x
                    negative_child.negative_probability[current_node] = p_list[0] + p_list[2]
                    # p = x
                    negative_child.positive_probability[current_node] = p_list[1] + p_list[3]
                else:
                    #child is alt child but doesn't match variable --> add both alt probabilities
                    # p = not x_
                    negative_child.negative_probability[current_node] = p_list[0] + p_list[1]
                    #p = not x
                    negative_child.positive_probability[current_node] = p_list[2] + p_list[3]
            self.__set_probabilities_recursion(negative_child, probabilities)

        #same for positive child
        if not positive_child.isLeaf():
            if not current_node.is_alt and current_node.variable == positive_child.variable:
                #child needs to be alt of current node -> current probability affects alt child probability
                p_list = probabilities[current_node.variable]

                # p = (p x and not x_) / (p x)
                positive_child.negative_probability[current_node] = p_list[1] / (p_list[1] + p_list[3])
                # p = (p x and x_) / (p x)
                positive_child.positive_probability[current_node] = p_list[3] / (p_list[1] + p_list[3])

            #child is not influenced by current node probability
            else:
                p_list = probabilities[positive_child.variable]

                if not positive_child.is_alt:
                    # p = not x
                    positive_child.negative_probability[current_node] = p_list[0] + p_list[2]
                    # p = x
                    positive_child.positive_probability[current_node] = p_list[1] + p_list[3]
                else:
                    #child is alt child but doesn't match variable --> add both alt probabilities
                    # p = not x_
                    positive_child.negative_probability[current_node] = p_list[0] + p_list[1]
                    #p = not x
                    positive_child.positive_probability[current_node] = p_list[2] + p_list[3]
            self.__set_probabilities_recursion(positive_child, probabilities)

            #end case: both children are leafs
        return
    
    def remove_alt_variables(self, vars: list[str]) -> list[str]:
        for i in range(len(vars)): 
            if vars[i].endswith("_"):  
                vars[i] = vars[i][:-1]
        return vars

    #only use if probabilities are set
    def sum_probabilities_positive_cases(self):
        if not self.probabilities_set:
            raise Exception("Set the probabilities first.")
        return self.__sum_probabilities_helper(self.root, self.root, path_mul=mpq(1))

    def __sum_probabilities_helper(self, current_node: BDDNode, parent_node: BDDNode, path_mul: mpq) -> mpq:
        #sum of path is complete
        if current_node.isLeaf():
            #don't sum probabilities of paths that end in zero
            if current_node.value == 0:
                return mpq(0)
            else:
                return path_mul
        else:
            negative_child = current_node.negative_child
            positive_child = current_node.positive_child

            mul_negative_path = self.__sum_probabilities_helper(negative_child, current_node,
                                                                path_mul * current_node.negative_probability[
                                                                    parent_node])
            mul_positive_path = self.__sum_probabilities_helper(positive_child, current_node,
                                                                path_mul * current_node.positive_probability[
                                                                    parent_node])

            return mul_negative_path + mul_positive_path

    #only used for testing purposes
    def __sum_all_probability_paths(self):
        if not self.probabilities_set:
            raise Exception("Set the probabilities first.")
        return self.__sum_all_probability_paths_recursion(self.root, self.root, path_mul=mpq(1))

    def __sum_all_probability_paths_recursion(self, current_node: BDDNode, parent_node: BDDNode, path_mul: mpq):
        #sum of path is complete
        if current_node.isLeaf():
            return path_mul
        else:
            negative_child = current_node.negative_child
            positive_child = current_node.positive_child

            mul_negative_path = self.__sum_all_probability_paths_recursion(negative_child, current_node,
                                                                path_mul * current_node.negative_probability[
                                                                    parent_node])
            mul_positive_path = self.__sum_all_probability_paths_recursion(positive_child, current_node,
                                                                path_mul * current_node.positive_probability[
                                                                    parent_node])

            return mul_negative_path + mul_positive_path

    # returns first node of all nodes with a positive and negative leaf as child
    def get_parents_of_pos_and_neg_leaf(self) -> BDDNode:
        for node in self.leafs[True].parents:
            if node.negative_child.isLeaf() and node.positive_child.isLeaf():
                if node.negative_child.value + node.positive_child.value == 1:
                    return node
        return None

    # Visualization
    def generateDot(self, path="output"):
        #add "_" to node label if BDD is alternative version of another BDD
        node = self.root
        alt_str = "_" if node.is_alt else ""
        label = node.value if node.isLeaf() else node.variable + alt_str

        #make file
        path = f"out\{path}.dot"
        directory = os.path.dirname(path)

        os.makedirs(directory, exist_ok=True)
        out = open(path, "w")

        #write start of the dot file and the root node
        #out.write(f"digraph{{\nlabel=\"{self.expression}\\n\\n\"\n{id(node)}[label={label}]")
        out.write(f"digraph{{{id(node)}[label={label}]")
        self.__generate_dot_recursive(node, out)
        out.write("}")
        out.close()
        self.__reset_draw(self.root)

    def __generate_dot_recursive(self, node: BDDNode, out):
        if not node.drawn:
            # draw negative_child child node
            if node.negative_child is not None:
                alt_str = "_" if node.negative_child.is_alt else ""
                child_node = node.negative_child
                #get probabilities
                prob_str = ""
                if node.negative_probability is not None:
                    for prob in node.negative_probability:
                        if prob.variable is not None:
                            prob_str = " " + prob_str + (prob.variable if not prob.is_alt else prob.variable + "_") + " "
                        prob_str = prob_str + f"{float(node.negative_probability[prob]):.2f}"
                        prob_str = prob_str + "\\n"
                if child_node.variable is not None:
                    #draw child node
                    parents = " ".join(p.variable for p in child_node.parents)
                    out.write(f"{id(child_node)}[label=\"{child_node.variable + alt_str}\"]\n")
                    #draw edge node -> child_node
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed label=\"{prob_str}\" fontcolor = gray]\n")
                    self.__generate_dot_recursive(child_node, out)
                elif node.negative_child.value is not None:
                    #draw leaf node
                    parents = " ".join(p.variable for p in child_node.parents)
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\"]\n")
                    #draw edge node -> leaf node
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed label=\"{prob_str}\" fontcolor = gray]\n")
            #draw positive childnode
            if node.positive_child is not None:
                child_node = node.positive_child
                alt_str = "_" if node.positive_child.is_alt else ""
                #get probability
                prob_str = ""
                if node.positive_probability is not None:
                    for prob in node.positive_probability:
                        if prob.variable is not None:
                            prob_str = " " + prob_str + (prob.variable if not prob.is_alt else prob.variable + "_") + " "
                        prob_str = prob_str + f"{float(node.positive_probability[prob]):.2f}"
                        prob_str = prob_str + "\\n"
                if child_node.variable is not None:
                    #draw child node
                    parents = " ".join(p.variable for p in child_node.parents)
                    out.write(f"{id(child_node)}[label=\"{child_node.variable + alt_str} \"]\n")
                    #draw edge node -> child node
                    out.write(f"{id(node)} -> {id(child_node)} [label=\"{prob_str}\" fontcolor = gray]\n")
                    self.__generate_dot_recursive(child_node, out)
                elif child_node.value is not None:
                    #draw leaf node 
                    parents = " ".join(p.variable for p in child_node.parents)
                    out.write(f"{id(child_node)}[label=\"{child_node.value} \"]\n")
                    #draw edge node -> leaf node
                    out.write(f"{id(node)} -> {id(child_node)} [label=\"{prob_str}\" fontcolor = gray]\n")
            node.drawn = True

    def __reset_draw(self, node):
        if node.isLeaf():
            node.drawn = False
        if node.negative_child is not None:
            self.__reset_draw(node.negative_child)
        if node.positive_child is not None:
            self.__reset_draw(node.positive_child)
        node.drawn = False

    def __eq__(self, other):
        if other is None or not isinstance(other, BDD):
            return False
        return(
            #expression doesn't need to be checked (can be different for same BDDs)
            self.variables == other.variables and
            #checks all child nodes in tree
            self.root == other.root
        )

