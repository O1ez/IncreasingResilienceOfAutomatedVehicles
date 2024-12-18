from BDD import BDD, BDDNode
from typing import Optional
from copy import copy, deepcopy


class Model:
    def __init__(self, acceptable_threshold: float, unobservable: str, f_guard: str, variables):
        self.acceptable_threshold = acceptable_threshold
        self.uo = BDD(unobservable, variables)
        self.uo.reduce()
        self.f = BDD(f_guard, variables)
        self.f.reduce()
        self.vars = vars

    #TODO: implement this
    def calc_tp_fp(self, step = ""):
        self.f.generateDot(step+"0_bdd_f_")
        bdd_f_replaced = self.f.replace_variables("_")
        bdd_f_replaced.generateDot(step+"1_bdd_f_replaced")
        
        bdd_not_f = self.f.replace_variables("")
        bdd_not_f.negate()
        bdd_not_f.generateDot(step+"2_bdd_not_f")
        
        bdd_not_uo = self.uo.replace_variables("")
        bdd_not_uo.negate()
        bdd_not_uo.generateDot(step+"3_bdd_not_uo")
        
        
        if bdd_not_f.variables != bdd_not_uo.variables:
            raise Exception("variables of f and uo don't match")
        
        f_replaced_vars = bdd_f_replaced.variables
        not_f_vars = bdd_not_f.variables
        f_united_vars = []
        for i in range(len(not_f_vars)):
            f_united_vars.append(not_f_vars[i])
            f_united_vars.append(f_replaced_vars[i])
        
        first_unite = BDD.unite(bdd_not_f, bdd_not_uo, not_f_vars)
        first_unite.generateDot(step+"4_bdd_not_f_and_not_uo")
        bdd_fp = BDD.unite(bdd_f_replaced, first_unite, f_united_vars)
        bdd_fp.generateDot(step+"5_bdd_fp")
        
        #mit Fehler in der Dok
        bdd_f_replaced.negate()
        
        f_replaced_vars = bdd_f_replaced.variables
        not_f_vars = bdd_not_f.variables
        f_united_vars = []
        for i in range(len(not_f_vars)):
            f_united_vars.append(not_f_vars[i])
            f_united_vars.append(f_replaced_vars[i])
        
        first_unite = BDD.unite(bdd_not_f, bdd_not_uo, not_f_vars)
        bdd_fp_wrong = BDD.unite(bdd_f_replaced, first_unite, f_united_vars)
        bdd_fp_wrong.generateDot(step+"5_wrong_bdd_fp")

        return 0.5, 0.5

    def check_acceptable(self, fp: float):
        return fp < self.acceptable_threshold

    def find_node_in_uo(self, bdd_uo: BDD) -> BDDNode:
        nodes = bdd_uo.breadth_first_bottom_up_search()
        while nodes:
            n = nodes.pop(0)
            if n.isLeaf() or n == bdd_uo.root:
                continue
            if n.negative_child.isLeaf() and n.positive_child.isLeaf():
                if n.negative_child.value + n.positive_child.value == 1:
                    return n

    def find_node_in_f(self, node_in_uo: BDDNode) -> list[BDDNode]:
        assignments = node_in_uo.assignment
        current_node = self.f.root
        found_nodes = set()
        for assignment in assignments:
            for var in assignment:
                if current_node.var != var:
                    continue
                if assignment[var]:
                    current_node = current_node.positive_child
                else:
                    current_node = current_node.negative_child
            found_nodes.add(current_node)
        return found_nodes

    #TODO: rename this
    def algorithm(self):
        bdd_uo_copy = self.uo.replace_variables("")
        #1
        tp_old, fp_old = self.calc_tp_fp("_start_")
        print("Initial values: \ntp: " + str(tp_old) + "\nfp: " + str(fp_old))
        #2
        child_uo = self.find_node_in_uo(bdd_uo_copy)
        i = 1
        while child_uo:
            #a
            children_f = self.find_node_in_f(child_uo)
            #b
            for child in children_f:
                child.positive_child = child.negative_child
            #c
            child_uo.positive_child = child_uo.negative_child
            #d
            self.f.reduce()
            self.f.generateDot("bdd_f_"+str(i))
            self.uo.reduce()
            self.uo.generateDot("bdd_uo_"+str(i))
            i+=1
            child_uo = self.find_node_in_uo(bdd_uo_copy)
        #3
        tp_new, fp_new = self.calc_tp_fp("end_")
        print("New values: \ntp: " + str(tp_new) + "\nfp: " + str(fp_new))
        #4
        is_acceptable = self.check_acceptable(fp_new)


if __name__ == "__main__":
    #Example:
    #vars = ["A1", "A2", "A3"]
    #observations = "(A2 or A3)"
    #f_guard = "(not A1 and A2) or (A1 and not A3) or (not A2 and A3)"
    #unobservable = "(A1 and not A2 and not A3) or (not A1 and A2 and not A3) or (not A1 and not A2 and A3)"
    #ground_truth = "(not A1 and A2 and A3) or (A1 and not A2 and A3) or (A1 and A2 and not A3)"
    #print(f"Ground Truth: {model.bdd_ground_truth.evaluation.values()}")
    #print(f"observations: {model.bbd_observations.evaluation.values()}")
    #tp, fp = model.calc_tp_fp()
    #print(f"tp: {tp}, fp: {fp}")

    print("Start test")
    v = ["x", "y", "z"]
    f = "(x and y) or (x and not y and not z) or (not x and y and not z) or (not x and not y and z)"
    uo = "(x and z) or (not x and y)"

    BDD.delete_all_files_from_out()
    model = Model(0.1, uo, f, v)
    model.algorithm()
