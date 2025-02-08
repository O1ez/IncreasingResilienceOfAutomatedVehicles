from bdd import BDD, BDDNode, delete_all_files_from_out
from gmpy2 import mpq


class Model:
    def __init__(self, acceptable_threshold: float,
                 unobservable: str,
                 f_guard: str,
                 probabilities: dict[str, list[mpq]]):
        self.acceptable_threshold = acceptable_threshold
        self.uo = BDD(unobservable, list(probabilities.keys()))
        self.uo.reduce()
        self.f = BDD(f_guard, list(probabilities.keys()))
        self.f.reduce()
        self.vars = list(probabilities.keys())
        self.probabilities = probabilities

    def calc_tp_fp(self, path: str, step=""):
        self.f.generateDot(f"{path}\\{step}0_bdd_f_")
        bdd_f_replaced = self.f.rename_variables()
        bdd_f_replaced.generateDot(f"{path}\\{step}1_bdd_f_replaced")

        bdd_not_f = self.f.negate()
        bdd_not_f.generateDot(f"{path}\\{step}2_bdd_not_f")

        bdd_not_uo = self.uo.negate()
        bdd_not_uo.generateDot(f"{path}\\{step}3_bdd_not_uo")

        if bdd_not_f.variables != bdd_not_uo.variables:
            raise Exception("variables of f and uo don't match")

        f_replaced_vars = bdd_f_replaced.variables
        not_f_vars = bdd_not_f.variables
        f_united_vars = []
        for i in range(len(not_f_vars)):
            f_united_vars.append(not_f_vars[i])
            f_united_vars.append(f_replaced_vars[i])

        #build fp = f_ and not f and not uo
        first_unite = BDD.apply_operand(bdd_not_f, bdd_not_uo, "and", not_f_vars)
        bdd_fp = BDD.apply_operand(bdd_f_replaced, first_unite,"and", f_united_vars)
        bdd_fp.set_probabilities(self.probabilities)
        bdd_fp.generateDot(f"{path}\\{step}5_bdd_fp")
        fp = bdd_fp.sum_probabilities_positive_cases()

        #build tp = f_ and f and not uo
        bdd_tp = BDD.apply_operand(bdd_f_replaced, BDD.apply_operand(bdd_not_uo, self.f,"and", self.vars),"and", f_united_vars)
        bdd_tp.set_probabilities(self.probabilities)
        bdd_tp.generateDot(f"{path}\\{step}6_bdd_tp")
        tp = bdd_tp.sum_probabilities_positive_cases()
        #bdd_tp.sum_all_probability_paths()

        return tp, fp

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

    def find_node_in_f(self, node_in_uo: BDDNode) -> set[BDDNode]:
        #assignments = node_in_uo.assignments
        assignments = self.uo.find_paths(node_in_uo)
        current_node = self.f.root
        found_nodes = set()
        for assignment in assignments:
            for var in assignment:
                if current_node.variable != var:
                    continue
                if assignment[var]:
                    current_node = current_node.positive_child
                else:
                    current_node = current_node.negative_child
            found_nodes.add(current_node)
        return found_nodes

    #TODO: rename this
    def algorithm(self, path: str):
        bdd_uo_copy = self.uo.copy_bdd()
        #1
        tp_old, fp_old = self.calc_tp_fp(path, "_start_")
        print(
            f"\033[96m\n\033[1m{path}:\033[0m\nInitial values: \ntp: " + f"{float(tp_old):.2f}" + "\nfp: " +
            f"{float(fp_old):.2f}")
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
            self.f.generateDot(f"{path}\\bdd_f_" + str(i))
            bdd_uo_copy.reduce()
            bdd_uo_copy.generateDot(f"{path}\\bdd_uo_" + str(i))
            i += 1
            child_uo = self.find_node_in_uo(bdd_uo_copy)
        #3
        tp_new, fp_new = self.calc_tp_fp(path, "end_")
        print("New values: \ntp: " + f"{float(tp_new):.2f}" + "\nfp: " + f"{float(fp_new):.2f}")
        #4
        is_acceptable = self.check_acceptable(fp_new)
        print(
            f"The fp Value ({float(fp_new):.2f}) is {'not ' if not is_acceptable else ''}acceptable. "
            f"-> {float(fp_new):.2f} "f"{'>' if not is_acceptable else '<='} {self.acceptable_threshold}"
            "\n---------------------------------\n")


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

    #v = ["x", "y", "z"]

    # x'\x  0     1
    # 0    0.2   0.3
    # 1    0.4   0.1
    #
    # y'\y  0     1
    # 0    0.15  0.6  0.75
    # 1    0.13  0.12 0.25
    #      0.28  0.72

    # z'\z  0     1
    # 0    0.23  0.17
    # 1    0.2   0.4
    #
    p = {
        "x": [mpq(0.2), mpq(0.3), mpq(0.4), mpq(0.1)],
        "y": [mpq(0.15), mpq(0.6), mpq(0.13), mpq(0.12)],
        "z": [mpq(0.23), mpq(0.17), mpq(0.2), mpq(0.4)]
    }
    f = "((x and y) or ((x and not y) and not z)) or (((not x and y) and not z) or ((not x and not y) and z))"
    uo = "(x and z) or (not x and y)"

    p2 = {
        "a": [mpq(0.05), mpq(0.65), mpq(0.05), mpq(0.25)],
        "b": [mpq(0.2), mpq(0.4), mpq(0.1), mpq(0.3)],
        "c": [mpq(0.13), mpq(0.62), mpq(0.1), mpq(0.15)]
    }
    f2 = "a and ((b or c) and (a or not c))"
    uo2 = "not a and (b or (not b and c))"

    p3 ={
        "m": [mpq(0.7), mpq(0.0,), mpq(0.17), mpq(0.1)],
        "n": [mpq(0.08), mpq(0.53), mpq(0.03), mpq(0.36)],
        "l": [mpq(0.25), mpq(0.31), mpq(0.27), mpq(0.17)]
    }
    f3 = "((m or l) and (not m and n)) or (m and n)"
    uo3 = "(not m and not n) or (n and l)"

    delete_all_files_from_out()
    model = Model(0.05, uo, f, p)
    model.algorithm("test1")
    model2 = Model(0.05, uo2, f2, p2)
    model2.algorithm("test2")
    model3 = Model(0.05, uo3, f3, p3)
    model3.algorithm("test3")
