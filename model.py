from BDD.BDD import BDD, BDDNode
from typing import Optional


class Model:
    def __init__(self, acceptable_threshold: float, unobservable: str, f_guard: str, variables):
        self.acceptable_threshold = acceptable_threshold
        self.uo = BDD(unobservable, variables)
        self.uo.reduce()
        self.uo.generateDot("unobservable")
        self.f = BDD(f_guard, variables)
        self.f.reduce()
        self.f.generateDot("fguard")
        self.vars = vars

    #TODO: implement this
    def calc_tp_fp(self):
        return 0.5, 0.5

    def check_acceptable(self, fp: float):
        return fp < self.acceptable_threshold

    def find_node_in_uo(self) -> BDDNode:
        nodes = self.uo.breadth_first_bottom_up_search()
        while nodes:
            n = nodes.pop(0)
            if n.negative_child.isLeaf() and n.positive_child.isLeaf():
                if n.negative_child.value + n.positive_child.value == 1:
                    self.uo.remove(n)
                    return n

    def find_node_in_f(self, node_in_uo: BDDNode) -> list[BDDNode]:
        assignments = node_in_uo.assignment
        current_node = self.f.root
        found_nodes = [BDDNode]
        for assignment in assignments:
            for var in assignment:
                if current_node.var != var:
                    continue
                if assignment[var]:
                    current_node = current_node.positive_child
                else:
                    current_node = current_node.negative_child
            found_nodes.append(current_node)
        return found_nodes

    #TODO: rename this
    def algorithm(self):
        #1
        tp_old, fp_old = self.calc_tp_fp()
        print("Initial values: \ntp: " + str(tp_old) + "\nfp: " + str(fp_old))
        #2
        child_uo = self.find_node_in_uo()
        while not self.uo.isOnlyRoot():
            #a
            children_f = self.find_node_in_f(child_uo)
            #b
            for child in children_f:
                child.positive_child = child.negative_child
            #c
            child_uo.positive_child = child_uo.negative_child
            #d
            self.f.reduce()
            self.uo.reduce()
        #3
        tp_new, fp_new = self.calc_tp_fp()
        print("New values: \ntp: " + str(tp_new) + "\nfp: " + str(fp_new))
        #4
        is_acceptable = self.check_acceptable(fp_new)


if __name__ == "__main":
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

    v = ["x", "y", "z"]
    f = "(x and y) or (x and not y and not z) or (not x and y and not z) or (not x and not y and z)"
    uo = "(x and z) or (not x and y)"

    model = Model(0.1, uo, f, v)
