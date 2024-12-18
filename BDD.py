from __future__ import annotations

from collections import deque
from typing import Optional, Any, Type
import re
from copy import copy, deepcopy
import os
import glob



class BDDNode:
    def __init__(self, var=None, negative_child: Optional[BDDNode] = None, positive_child: Optional[BDDNode] = None, value=None, assignment: Optional[list[dict]] = None):
        self.var = var  # The variable for decision (None for terminal nodes)
        self.negative_child = negative_child
        self.positive_child = positive_child
        self.value = value  # Terminal value (True or False for leaf nodes)
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
                deepcopy(self.value, memo),)
            memo[id_self] = _copy
        return _copy


class BDD:
    def __init__(self, expression, variables: list[str], build_new=True):
        self.variables = variables  # List of variables
        self.expression = expression
        self.evaluation = {}  #dict of all evaluations
        self.leafs = {False: BDDNode(value=False), True: BDDNode(value=True)}
        self.root = None
        if build_new:
            self.build_new()

    def build_new(self):
        empty_dict = {}
        self.root = self.build(0, empty_dict)

    def build(self, var_index, current_assignment: dict):
        # end of recursion if node is a leaf
        if var_index == len(self.variables):
            current_assignment = {var: val for var, val in current_assignment.items()}  # copies current_assignment
            value = evaluate_expression(self.expression, current_assignment)
            self.evaluation[tuple(current_assignment.items())] = value
            leaf = BDDNode(value=value)
            leaf.assignment = [current_assignment]
            return leaf

        #initiate node
        var = self.variables[var_index]
        currentNode = BDDNode(var=var)
        currentNode.assignment = [({var: val for var, val in current_assignment.items()})]

        # Create node for false subtree and true subtree
        current_assignment_negative = current_assignment.copy()
        current_assignment_negative[var] = False
        leftNode = self.build(var_index + 1, current_assignment_negative)
        currentNode.negative_child = leftNode

        current_assignment_positive = current_assignment.copy()
        current_assignment_positive[var] = True
        positive_child = self.build(var_index + 1, current_assignment_positive)
        currentNode.positive_child = positive_child
        return currentNode

    def isOnlyRoot(self):
        return not self.root.hasChildren

    #TODO: needed?
    # # traverses down the diagram to evaluate it
    # def evaluate(self, node, variables):
    #     if node.isLeaf():
    #         return node.value
    #     if variables[node.var] is False:
    #         return self.evaluate(node.left, variables)
    #     else:
    #         return self.evaluate(node.positive_child, variables)

    def reduce(self):
        if not self.root.hasChildren:
            print("BDD only has root.")
            return False
        self.__merge_leafs(self.root)
        self.__remove_duplicate_subtree(self.root, mem={})
        self.__remove_equivalent_child_nodes(self.root)
        
        #TODO: fix hotfix
        if self.root.negative_child == self.root.positive_child:
            self.root = self.root.negative_child
        
        print("Reduction done.")
        return True

    def __remove_duplicate_subtree(self, node: BDDNode, mem: dict[BDDNode, BDDNode]):
        if node.isLeaf():
            return node

        if node in mem:
            self.add_assignments(mem[node], node.assignment)
            return mem[node]

        node.negative_child = self.__remove_duplicate_subtree(node.negative_child, mem)
        node.positive_child = self.__remove_duplicate_subtree(node.positive_child, mem)
        mem[node] = node
        return node

    def __merge_leafs(self, node: BDDNode) -> Optional[BDDNode]:
        if node is None:
            raise Exception("unexpected Node is None")
        
        if node.isLeaf():
            return node

        child_node_negative_child = self.__merge_leafs(node.negative_child)
        if child_node_negative_child is not None:
            leaf = self.leafs[child_node_negative_child.value]
            self.add_assignments(leaf, child_node_negative_child.assignment)
            node.negative_child = leaf

        child_node_positive_child = self.__merge_leafs(node.positive_child)
        if child_node_positive_child is not None and child_node_positive_child not in self.leafs:
            leaf = self.leafs[child_node_positive_child.value]
            self.add_assignments(leaf, child_node_positive_child.assignment)
            node.positive_child = leaf

        return None

    def __remove_equivalent_child_nodes(self, node: BDDNode) -> Optional[BDDNode]:
        if node.negative_child is not None:
            eq_child_negative_child = self.__remove_equivalent_child_nodes(node.negative_child)
            if eq_child_negative_child is not None:
                node.negative_child = eq_child_negative_child

        if node.positive_child is not None:
            eq_child_positive_child = self.__remove_equivalent_child_nodes(node.positive_child)
            if eq_child_positive_child is not None:
                node.positive_child = eq_child_positive_child

        if node.negative_child is not None and node.positive_child is not None and id(node.negative_child) == id(
                node.positive_child):
            return node.negative_child
        return None
    
    
    #adds assignments that are not already in the node
    @staticmethod
    def add_assignments(node: BDDNode, assignments: list[dict]):
        for a in assignments:
            if a not in node.assignment:
                node.assignment.append(a)

    #TODO: Kopie von der Negation zurückgeben, damit es einheitlich mit der unite Funktion ist?
    def negate(self):
        #negate leaf values
        false_leaf = self.leafs[False]
        false_leaf.value = True
        true_leaf = self.leafs[True]
        true_leaf.value = False
        
        #switch leafs in dictionary
        self.leafs[True] = false_leaf
        self.leafs[False] = true_leaf
        
        self.expression = "not (" + self.expression + ")"
        return

    #TODO: assignment not set properly
    @staticmethod
    def unite(BDD1: BDD, BDD2: BDD, variable_order: list) -> BDD:
        for var in BDD1.variables:
            if var not in variable_order:
                raise Exception("Variable " + var + " from BDD1 not found in variables.")

        for var in BDD2.variables:
            if var not in variable_order:
                raise Exception("Variable " + var + " from BDD2 not found in variables.")

        united = BDD(expression="(" + BDD1.expression + ")and(" + BDD2.expression + ")", variables=variable_order,build_new=False)
        united.root = BDD.__apply(BDD1.root, BDD2.root, variable_order, united)
        united.reduce()
        return united

    @staticmethod
    def __apply(Node1: BDDNode, Node2: BDDNode, variable_order: list[str], united_bdd: BDD) -> BDDNode:
        if (Node1.var and (Node1.var not in variable_order)) or (Node2.var and (Node2.var not in variable_order)):
            print(Node1.var + Node2.var + str(variable_order))
            raise Exception("BDD variables not in variable_order")
        
        # if both nodes are leafs return new leaf with united value
        if Node1.isLeaf() and Node2.isLeaf():
            solution = BDDNode(value=Node1.value and Node2.value)
            #BDD.add_assignments(solution, Node1.assignment)
            #BDD.add_assignments(solution, Node2.assignment)
            return solution
        
        # if both nodes are of the same variable unite the negative children and positive children of both bdd
        elif Node1.var == Node2.var:
            solution = BDDNode(var=Node1.var)
            solution.negative_child = BDD.__apply(Node1.negative_child, Node2.negative_child, variable_order,united_bdd)
            solution.positive_child = BDD.__apply(Node1.positive_child, Node2.positive_child, variable_order,united_bdd)
            #BDD.add_assignments(solution, Node1.assignment)
            #BDD.add_assignments(solution, Node2.assignment)
            if solution.negative_child is None or solution.positive_child is None:
                raise Exception("Children are None")
            #solution.reduce(united_bdd)
            return solution
        
        #if variables don't match deterine higher priority variable and unite children of higher prio variable with lower prio BDD
        else:
            gen = (var for var in variable_order if var == Node1.var or var == Node2.var)
            higher_variable = next(gen)

            if Node1.var == higher_variable:
                higher_prio = Node1
                lower_prio= Node2
            else:
                higher_prio = Node2
                lower_prio = Node1

            solution = BDDNode(var=higher_prio.var)
            #BDD.add_assignments(solution, higher_prio.assignment)
            print("...")
            solution.negative_child = BDD.__apply(higher_prio.negative_child, lower_prio, variable_order, united_bdd)
            solution.positive_child = BDD.__apply(higher_prio.positive_child, lower_prio, variable_order, united_bdd)
            if (solution.negative_child is None) or (solution.positive_child is None):
                raise Exception("Children are None")
            #TODO: doesn't work with reduced bdd's 
            #in example child node C without neg or pos child??
            #solution.reduce(united_bdd)
            return solution

    def replace_variables(self, replacer : str) -> BDD:
        #TODO: replacer richtig abfragen
        if replacer in ["'", "/"]:
            raise Exception("Replacer has not permitted characters")
        var_copy = [var+replacer for var in self.variables.copy()]
        expression_copy = self.expression
        for var in self.variables:
            expression_copy = re.sub(var, var+replacer, expression_copy)
        bdd_copy = BDD(expression_copy, var_copy, build_new=False)
        
        bdd_copy.root = self.__replace_children_nodes(self.root, {}, replacer)
        bdd_copy.__merge_leafs(bdd_copy.root)
        
        return bdd_copy
        
    def __replace_children_nodes(self, original_node: BDDNode, visited_nodes: dict[BDDNode], replacer: str):
        if original_node in visited_nodes:
            node_copy = visited_nodes[original_node]
            return node_copy
            
        if original_node.isLeaf():
            node_copy = self.__copy_node(original_node, replacer)
            return node_copy
        
        node_copy = self.__copy_node(original_node, replacer)
        node_copy.negative_child = self.__replace_children_nodes(original_node.negative_child, visited_nodes, replacer)
        node_copy.positive_child = self.__replace_children_nodes(original_node.positive_child, visited_nodes, replacer)
        visited_nodes[original_node] = node_copy
        return node_copy
            
    def __copy_node(self, node: BDDNode, replacer: str) -> BDDNode:
        var = None
        value = None
        if node.isLeaf():
            value = node.value
        else:
            var = node.var + replacer
        node_assignment_copy = node.assignment.copy()
        for i in range(len(node_assignment_copy)):
            node_assignment_copy[i] = {k+replacer: v for k, v in node_assignment_copy[i].items()}
        return BDDNode(var = var, value=value, assignment=node_assignment_copy)


    # returns list of all nodes in breadth first bottom up order
    def breadth_first_bottom_up_search(self) -> list[BDDNode]:
        out = []
        queue = deque([self.root])
        visited = set()

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            out.append(node)

            if node.negative_child:
                queue.append(node.negative_child)
            if node.positive_child:
                queue.append(node.positive_child)

        out.reverse()
        return out


    # Visualation
    def generateDot(self, filename="output"):
        node = self.root
        label = node.value if node.isLeaf() else node.var 
        #out = open(f"C:\\Users\\annan\\PycharmProjects\\SaferThanPerception\\BDD\\out\\{filename}.dot", "w")
        out = open(f"out\\{filename}.dot", "w")
        out.write(f"digraph{{\nlabel=\"{self.expression}\\n\\n\"\n{id(node)}[label={label}]")
        self.__generate_dot_recursive(node, out)
        out.write("}")
        print("Dot File generated")
        self.__reset_draw(self.root)

    def __generate_dot_recursive(self, node, out):
        if not node.drawn:
            # draw negative_child childnode
            if node.negative_child is not None:
                child_node = node.negative_child
                if node.negative_child.var is not None:
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.var} {assignments}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed]\n")
                    self.__generate_dot_recursive(child_node, out)
                elif node.negative_child.value is not None:
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\n{assignments}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed]\n")
            #draw right childnode
            if node.positive_child is not None:
                child_node = node.positive_child
                if node.positive_child.var is not None:
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.var} {assignments}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}\n")
                    self.__generate_dot_recursive(node.positive_child, out)
                elif node.positive_child.value is not None:
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\n{assignments}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}\n")
            node.drawn = True

    def __reset_draw(self, node):
        if node.isLeaf():
            node.drawn = False
        if node.negative_child is not None:
            self.__reset_draw(node.negative_child)
        if node.positive_child is not None:
            self.__reset_draw(node.positive_child)
        node.drawn = False
        
    def __copy__(self):
        return type(self)(self.variables, self.expression, self.evaluation, self.leafs, self.root)
    
    def __deepcopy__(self, memo): 
        id_self = id(self)       
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.expression, memo),
                deepcopy(self.variables, memo),
                )
            memo[id_self] = _copy 
            _copy.reduce()
        return _copy
    
    def delete_all_files_from_out():
        files = glob.glob('out/*')
        for file in files:
            os.remove(file)
        

def evaluate_expression(expr, assignment):
        return eval(expr, {}, assignment)
    


if __name__ == "__main__":
    #Example:
    # e = "(A and B) or C"
    # e = "((not A or B) and (not B or A)) and ((not C or D) and (not D or C))"
    # v = ['A', 'B', 'C', 'D']
    # bdd = BDD(e, v)
    #
    # print("Binary Decision Diagram (BDD):")
    # bdd.generateDot(filename="out")
    # bdd.reduce()
    # bdd.generateDot(filename="reduced_out")
    # bdd.negate()
    # bdd.generateDot(filename="negated_out")
    # for k, v in bdd.evaluation.items():
    #     print(f"{k}: {v}")
    #
    
    BDD.delete_all_files_from_out()
    e1 = "A or B"
    e2 = "(B or C) and (A and D)"
    v = ['A', 'B', 'C', 'D']
    #bdd1 = BDD(e1, v)
    #bdd1.reduce()
    #bdd1.generateDot("bdd1")
    bdd2 = BDD(e2, v)
    bdd2.reduce()
    bdd2.generateDot("bdd2")
    bdd2_replaced = bdd2.replace_variables("")
    bdd2.generateDot("bdd2_2")
    bdd2_replaced.negate()
    bdd2_replaced.generateDot("bdd_2_negate")
    #
    #bdd1_and_bdd2 = BDD.unite(bdd1, bdd2, ["A", "B", "C"])
    #bdd1_and_bdd2.generateDot(filename="united_out")
    #
    #bdd1_copy = bdd1.replace_variables(replacer="_")
    #bdd1_copy.generateDot("bdd1_copy")

