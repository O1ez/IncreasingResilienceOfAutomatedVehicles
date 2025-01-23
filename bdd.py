from __future__ import annotations
from collections import deque
from typing import Optional
import re
import os
import glob
import shutil
from gmpy2 import mpq


class BDDNode:
    def __init__(self, var: str = None, value: bool = None, assignment: Optional[list[dict]] = None, is_alt=False,
                 negative_child: Optional[BDDNode] = None,
                 negative_probability: dict[BDDNode, mpq] = None,
                 positive_child: Optional[BDDNode] = None,
                 positive_probability: dict[BDDNode, mpq] = None):

        self.var = var  # The variable for decision (None for terminal nodes)
        self.negative_child = negative_child
        self.negative_probability = {} if negative_probability is None else negative_probability
        self.positive_child = positive_child
        self.positive_probability = {} if positive_probability is None else positive_probability
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

    def isEmpty(self):
        return self.var is None and self.value is None

    def copy_node(self, is_alt: bool) -> BDDNode:
        var = None
        value = None
        if self.isLeaf():
            value = self.value
        else:
            var = self.var
        node_assignment_copy = self.assignment.copy()
        for i in range(len(node_assignment_copy)):
            node_assignment_copy[i] = {k: v for k, v in node_assignment_copy[i].items()}
        return BDDNode(var=var, value=value, assignment=node_assignment_copy, is_alt=is_alt)

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


def delete_all_files_from_out():
    files = glob.glob('out/*')
    for obj in files:
        if os.path.isfile(obj):
            os.remove(obj)
        elif os.path.isdir(obj):
            shutil.rmtree(obj)


class BDD:
    def __init__(self, expression, variables: list[str], build_new=True):
        self.variables = variables  # List of variables
        self.expression = expression
        #dict of all evaluations
        self.evaluation = {}
        self.leafs = {False: BDDNode(value=False), True: BDDNode(value=True)}
        self.root = None
        self.probabilities_set = False
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
        current_node = BDDNode(var=var)
        current_node.assignment = [({var: val for var, val in current_assignment.items()})]

        # Create node for false subtree and true subtree
        current_assignment_negative = current_assignment.copy()
        current_assignment_negative[var] = False
        leftNode = self.build(var_index + 1, current_assignment_negative)
        current_node.negative_child = leftNode

        current_assignment_positive = current_assignment.copy()
        current_assignment_positive[var] = True
        positive_child = self.build(var_index + 1, current_assignment_positive)
        current_node.positive_child = positive_child
        return current_node

    def isOnlyRoot(self):
        return not self.root.hasChildren

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

        #print("Reduction done.")
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

    #TODO: assignment not set properly
    @staticmethod
    def unite(BDD1: BDD, BDD2: BDD, variable_order: list) -> BDD:
        for var in BDD1.variables:
            if var not in variable_order:
                raise Exception("Variable " + var + " from BDD1 not found in variables.")

        for var in BDD2.variables:
            if var not in variable_order:
                raise Exception("Variable " + var + " from BDD2 not found in variables.")

        united_bdd = BDD(expression="(" + BDD1.expression + ")and(" + BDD2.expression + ")", variables=variable_order,
                         build_new=False)
        united_bdd.root = BDD.__unite_helper(BDD1.root, BDD2.root, variable_order, united_bdd)
        united_bdd.reduce()
        return united_bdd

    @staticmethod
    def __unite_helper(node1: BDDNode, node2: BDDNode, variable_order: list[str], united_bdd: BDD) -> BDDNode:
        node1_var = None
        node2_var = None
        if node1.var:
            node1_var = node1.var + "_" if node1.is_alt else node1.var
            if node1_var not in variable_order:
                raise Exception(f"{node1_var} not in variable order {variable_order}.")
        if node2.var:
            node2_var = node2.var + "_" if node2.is_alt else node2.var
            if node2_var not in variable_order:
                raise Exception(f"{node2_var} not in variable order {variable_order}.")

        # if both nodes are leafs return new leaf with united value
        if node1.isLeaf() and node2.isLeaf():
            solution = BDDNode(value=node1.value and node2.value)
            #BDD.add_assignments(solution, Node1.assignment)
            #BDD.add_assignments(solution, Node2.assignment)
            return solution

        # if both nodes are of the same variable unite the negative children and positive children of both bdd
        elif node1_var == node2_var:
            solution = BDDNode(var=node1_var, is_alt=node1.is_alt)
            solution.negative_child = BDD.__unite_helper(node1.negative_child, node2.negative_child, variable_order,
                                                         united_bdd)
            solution.positive_child = BDD.__unite_helper(node1.positive_child, node2.positive_child, variable_order,
                                                         united_bdd)
            #BDD.add_assignments(solution, Node1.assignment)
            #BDD.add_assignments(solution, Node2.assignment)
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

            solution = BDDNode(var=higher_prio.var, is_alt=higher_prio.is_alt)
            solution.negative_child = BDD.__unite_helper(higher_prio.negative_child, lower_prio, variable_order,
                                                         united_bdd)
            solution.positive_child = BDD.__unite_helper(higher_prio.positive_child, lower_prio, variable_order,
                                                         united_bdd)
            if (solution.negative_child is None) or (solution.positive_child is None):
                raise Exception("Children are None")
            #TODO: doesn't work with reduced bdd's 
            #in example child node C without neg or pos child??
            return solution

    #creates a copy of BDD gives it is_alt attribute
    def rename_variables(self) -> BDD:
        return self.__copy(True)

    #gives a copy of bdd
    def copy_bdd(self) -> BDD:
        return self.__copy(False)

    def __copy(self, is_alt: bool) -> BDD:
        expression_copy = self.expression
        if is_alt:
            var_copy = [var + "_" for var in self.variables.copy()]
            for var in self.variables:
                #replace var in expression if a space follows it
                expression_copy = re.sub(var + " ", var + "_" + " ", expression_copy)
        else:
            var_copy = self.variables.copy()

        bdd_copy = BDD(expression_copy, var_copy, build_new=False)
        bdd_copy.root = self.__replace_children_nodes(self.root, {}, is_alt)
        bdd_copy.__merge_leafs(bdd_copy.root)
        return bdd_copy

    def __replace_children_nodes(self, original_node: BDDNode, visited_nodes: dict[BDDNode, BDDNode], is_alt: bool):
        #if original node is already copied use the copy
        if original_node in visited_nodes:
            node_copy = visited_nodes[original_node]
            return node_copy

        if original_node.isLeaf():
            node_copy = original_node.copy_node(is_alt)
            return node_copy

        node_copy = original_node.copy_node(is_alt)
        node_copy.negative_child = self.__replace_children_nodes(original_node.negative_child, visited_nodes, is_alt)
        node_copy.positive_child = self.__replace_children_nodes(original_node.positive_child, visited_nodes, is_alt)
        #map copy of Node to the original node
        visited_nodes[original_node] = node_copy
        return node_copy

    #only use if original and alternative Variables are united
    def set_probabilities(self, probabilities: dict[str: list[mpq]]):
        root = self.root
        if root.isLeaf():
            raise Exception("Tree needs at least one Node that isn't a leaf!")
        #root handled separately because it does not have a parent node
        if not root.is_alt:
            #p of only x
            root.negative_probability[root] = probabilities[root.var][0] + probabilities[root.var][2]
            #p of only not x
            root.positive_probability[root] = probabilities[root.var][1] + probabilities[root.var][3]
        else:
            #p of only x_
            root.negative_probability[root] = probabilities[root.var][0] + probabilities[root.var][1]
            #p of only not x_
            root.positive_probability[root] = probabilities[root.var][1] + probabilities[root.var][0]
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
            if not current_node.is_alt and current_node.var == negative_child.var:
                #child needs to be alt of current node -> current probability affects alt child probability
                p_list = probabilities[current_node.var]

                # p = (p not x and not x_) / (p not x)
                negative_child.negative_probability[current_node] = p_list[0] / (p_list[0] + p_list[2])
                # p = (p not x and x_) / (p not x)
                negative_child.positive_probability[current_node] = p_list[2] / (p_list[0] + p_list[2])

            #child is not influenced by current node probability
            else:
                p_list = probabilities[negative_child.var]
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
            if not current_node.is_alt and current_node.var == positive_child.var:
                #child needs to be alt of current node -> current probability affects alt child probability
                p_list = probabilities[current_node.var]

                # p = (p x and not x_) / (p x)
                positive_child.negative_probability[current_node] = p_list[1] / (p_list[1] + p_list[3])
                # p = (p x and x_) / (p x)
                positive_child.positive_probability[current_node] = p_list[3] / (p_list[1] + p_list[3])

            #child is not influenced by current node probability
            else:
                p_list = probabilities[positive_child.var]

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

    def sum_all_probability_paths(self):
        self.__sum_all_probability_paths_recursion(current_node=self.root, visited_nodes={self.root: mpq(1)})
        return

    def __sum_all_probability_paths_recursion(self, current_node: BDDNode, visited_nodes: dict[BDDNode, mpq],
                                              all_path_sum: mpq = 0,
                                              path_mul: mpq = 1) -> mpq:
        #visited_nodes.append(current_node.var if not current_node.is_alt else current_node+"_")
        if current_node.isLeaf():
            all_path_sum += path_mul
            out = "Path: "
            for n in visited_nodes:
                if n.isEmpty():
                    continue
                out = out + (n.var if not n.is_alt else n.var + "_") + f": {float(visited_nodes[n]):.2f} "
            print(out + "pathprobability = " + f"{float(path_mul):.2f}" + " new sum = " + f"{float(all_path_sum):.2f}")
            return all_path_sum
        else:

            negative_child = current_node.negative_child
            positive_child = current_node.positive_child
            parent_node = list(visited_nodes.keys())[-1]

            temp1 = dict(visited_nodes)
            temp1[current_node] = current_node.negative_probability[parent_node]
            all_path_sum = self.__sum_all_probability_paths_recursion(negative_child, temp1, all_path_sum,
                                                                      path_mul * current_node.negative_probability[
                                                                          parent_node])

            temp2 = dict(visited_nodes)
            temp2[current_node] = current_node.negative_probability[parent_node]
            all_path_sum = self.__sum_all_probability_paths_recursion(positive_child, temp2, all_path_sum,
                                                                      path_mul * current_node.positive_probability[
                                                                          parent_node])

        return all_path_sum

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

    # Visualization
    def generateDot(self, path="output"):
        #add "_" to node label if BDD is alternative version of another BDD
        node = self.root
        alt_str = "_" if node.is_alt else ""
        label = node.value if node.isLeaf() else node.var + alt_str

        #make file
        path = f"out\\{path}.dot"
        directory = os.path.dirname(path)

        os.makedirs(directory, exist_ok=True)
        out = open(path, "w")

        #write start of the dot file and the root node
        out.write(f"digraph{{\nlabel=\"{self.expression}\\n\\n\"\n{id(node)}[label={label}]")
        self.__generate_dot_recursive(node, out)
        out.write("}")
        #print(f"Dot File generated: {filename}.dot")
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
                        if prob.var is not None:
                            prob_str = " " + prob_str + (prob.var if not prob.is_alt else prob.var + "_") + " "
                        prob_str = prob_str + f"{float(node.negative_probability[prob]):.2f}"
                        prob_str = prob_str + "\\n"
                if child_node.var is not None:
                    #draw child node
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.var + alt_str}\n{assignments}\"]\n")
                    #draw edge node -> child_node
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed label=\"{prob_str}\" fontcolor = gray]\n")
                    self.__generate_dot_recursive(child_node, out)
                elif node.negative_child.value is not None:
                    #draw leaf node
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\n{assignments}\"]\n")
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
                        if prob.var is not None:
                            prob_str = " " + prob_str + (prob.var if not prob.is_alt else prob.var + "_") + " "
                        prob_str = prob_str + f"{float(node.positive_probability[prob]):.2f}"
                        prob_str = prob_str + "\\n"
                if child_node.var is not None:
                    #draw child node
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.var + alt_str}\n{assignments}\"]\n")
                    #draw edge node -> child node
                    out.write(f"{id(node)} -> {id(child_node)} [label=\"{prob_str}\" fontcolor = gray]\n")
                    self.__generate_dot_recursive(child_node, out)
                elif child_node.value is not None:
                    #draw leaf node 
                    assignments = "\n".join(str(d) for d in child_node.assignment)
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\n{assignments}\"]\n")
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


def evaluate_expression(expr, assignment):
    return eval(expr, {}, assignment)


def main():
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

    delete_all_files_from_out()
    expression1 = "A or B"
    expression2 = "(B or C) and (A and C)"
    variables = ['A', 'B', 'C']

    p = {
        "A": [mpq(0.2), mpq(0.3), mpq(0.4), mpq(0.1)],
        "B": [mpq(0.15), mpq(0.6), mpq(0.13), mpq(0.12)],
        "C": [mpq(0.23), mpq(0.17), mpq(0.2), mpq(0.4)]
    }

    bdd1 = BDD(expression1, variables)
    bdd1.reduce()
    bdd1.generateDot("1_bdd1")

    bdd2 = BDD(expression2, variables)
    bdd2.reduce()
    bdd2.generateDot("2_bdd2")

    bdd2_replaced = bdd2.rename_variables()
    bdd2_replaced.generateDot("3_bdd2_replaced")
    bdd2_replaced.negate()
    bdd2_replaced.generateDot("4_bdd_2_negate")

    united = BDD.unite(bdd1, bdd2_replaced, ["A", "A_", "B", "B_", "C", "C_"])
    united.generateDot(path="5_united")
    united.set_probabilities(p)
    united.generateDot(path="6_united_w_prob")
    print(f"Sum of all positive paths is: {float(united.sum_probabilities_positive_cases()):.2f}\n")
    united.sum_all_probability_paths()


if __name__ == "__main__":
    main()
