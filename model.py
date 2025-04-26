from bdd import BDD, BDDNode, delete_all_files_from_out
from gmpy2 import mpq
import time

'Class that implements the algorithm to rewrite guard conditions and calculate false-positive as well as true-positive rates'
class Model:
    def __init__(self, acceptable_threshold: float,
                unobservable: str,
                f_guard: str,
                probabilities: dict[str, list[mpq]],
                generate_BDDs = False):
        self.acceptable_threshold = acceptable_threshold
        self.uo = BDD(unobservable, list(probabilities.keys()))
        #self.uo.reduce()
        self.f = BDD(f_guard, list(probabilities.keys()))
        #self.f.reduce()
        self.vars = list(probabilities.keys())
        self.probabilities = probabilities
        self.generate_bdds = generate_BDDs

    def calc_tp_fp(self, test_num: str, step=""):
        if self.generate_bdds:
            self.f.generateDot(f"test{test_num}\\{step}0_f_")
            self.uo.generateDot(f"test{test_num}\\{step}3_uo")
        bdd_f_replaced = self.f.rename_variables()
        bdd_not_f_replaced = bdd_f_replaced.negate()
        bdd_not_f = self.f.negate()
        bdd_not_uo = self.uo.negate()
        bdd_not_uo.generateDot(f"test{test_num}\\{step}2_not_uo")
        bdd_not_f_replaced.generateDot(f"test{test_num}\\{step}2-1_not_f_replaced")
        bdd_f_replaced.generateDot(f"test{test_num}\\{step}2-2_f_replaced")

        if bdd_not_f.variables != bdd_not_uo.variables:
            raise Exception("variables of f and uo don't match")

        f_replaced_vars = bdd_f_replaced.variables
        not_f_vars = bdd_not_f.variables
        f_united_vars = []
        for i in range(len(not_f_vars)):
            f_united_vars.append(not_f_vars[i])
            f_united_vars.append(f_replaced_vars[i])

        #build fp = not f_ and f and not uo
        first_unite = BDD.apply_binary_operand(self.f, bdd_not_uo, "and", not_f_vars)
        bdd_fp = BDD.apply_binary_operand(bdd_not_f_replaced, first_unite,"and", f_united_vars)
        fp = 0
        if(bdd_fp.satisfiable):
            bdd_fp.set_probabilities(self.probabilities)
            if self.generate_bdds: bdd_fp.generateDot(f"test{test_num}\\{step}5_fp")
            fp = bdd_fp.sum_probabilities_positive_cases()

        #build tp = f_ and f and not uo
        bdd_tp = BDD.apply_binary_operand(bdd_f_replaced, BDD.apply_binary_operand(bdd_not_uo, self.f,"and", self.vars),"and", f_united_vars)
        tp = 0
        if(bdd_fp.satisfiable):
            bdd_tp.set_probabilities(self.probabilities)
            if self.generate_bdds: bdd_tp.generateDot(f"test{test_num}\\{step}6_tp")
            tp = bdd_tp.sum_probabilities_positive_cases()
        #bdd_tp.sum_all_probability_paths()
        
        if not bdd_fp.satisfiable or not bdd_tp.satisfiable:
            print("WARNING: BDDf and BDDuo not satisfiable!")

        return tp, fp

    def check_acceptable(self, fp: float):
        return fp < self.acceptable_threshold
    
    #finds corresponding node in F and stores wether the positive-valued leaf was the positive or negative child
    def find_node_in_f_with_table(self, node_uo: BDDNode, lookup_table :dict[BDDNode, list[BDDNode]]):
        nodes_f = lookup_table[node_uo]
        return_dict: dict[BDDNode, bool] = {}  
        uo_child = False
        if node_uo.negative_child.isLeaf() and node_uo.negative_child.value == 1:
                uo_child = False
        else:
                uo_child = True
        for node in nodes_f:
            return_dict[node] = uo_child
        return return_dict

    #return a dict of nodes matching the node in uo, with a bool value representing which child they are 
    def find_node_in_f(self, node_in_uo: BDDNode) -> dict[BDDNode, bool]:
        #assignments = node_in_uo.assignments
        #wenn das true leaf das positive Kind der uo Node war, dann ist value true 
        # wenn es das negative Kind war dann value false
        # weil das Kind das 1 war ist nicht observable 
        assignments = self.uo.find_paths(node_in_uo)
        found_nodes: list[BDDNode] = []
        for assignment in assignments:
            current_node = self.f.root
            for var in assignment:
                if current_node.variable != var:
                    continue
                if assignment[var]:
                    current_node = current_node.positive_child
                else:
                    current_node = current_node.negative_child
            if node_in_uo.variable == current_node.variable:
                found_nodes.append(current_node)
            
        return_dict: dict[BDDNode, bool] = {}    
        for node in found_nodes:
            if node.negative_child.isLeaf() and node.negative_child.value == 1:
                return_dict[node] = 0
            elif node.positive_child.isLeaf() and node.positive_child.value == 1:
                return_dict[node] = 1
        return return_dict

    #TODO: rename this
    def algorithm(self, test_num: int):
        #needs to remain to calc BDDtp and BDDfp
        bdd_uo_copy = self.uo.copy_bdd()
        lookup_table = bdd_uo_copy.make_lookup_table_corr_nodes(bdd_uo_copy, self.f)
        #1
        tp_old, fp_old = self.calc_tp_fp(test_num, "_start_")
        print(
            f"Initial values: \ntp: " + f"{float(tp_old):.8f}" + "\nfp: " +
            f"{float(fp_old):.8f}")
        #2
        node_uo = bdd_uo_copy.get_parents_of_pos_and_neg_leaf()
        i = 1
        while node_uo:
            #a
            lookup_table = bdd_uo_copy.make_lookup_table_corr_nodes(bdd_uo_copy, self.f)
            nodes_f = self.find_node_in_f_with_table(node_uo, lookup_table)
            #b
            changed = False
            for node in nodes_f:
                #only change if parents are not empty -> node is still in BDD
                changed = True
                #one child gets redirected to other depending on which child it was in the uo BDD
                if nodes_f[node] == True:
                    node.positive_child.parents.remove(node)
                    node.negative_child.parents.append(node)
                    node.positive_child = node.negative_child
                else:
                    node.negative_child.parents.remove(node)
                    node.positive_child.parents.append(node)
                    node.negative_child = node.positive_child
            #c
            #always redirect the child ending in positive leaf in uo, because it is the one that is unobservable
            if node_uo.positive_child.isLeaf() and node_uo.positive_child.value == 1:
                node_uo.positive_child = node_uo.negative_child
            else: node_uo.negative_child = node_uo.positive_child
            
            #d
            if changed:
                if self.generate_bdds: self.f.generateDot(f"test{test_num}\\_step_{str(i)}_f_unreduced")
                self.f.reduce()
            
            if self.generate_bdds: self.f.generateDot(f"test{test_num}\\_step_{str(i)}_f_")
            if self.generate_bdds: bdd_uo_copy.generateDot(f"test{test_num}\\_step_{str(i)}_uo_unreduced")
            bdd_uo_copy.reduce()
            if self.generate_bdds: bdd_uo_copy.generateDot(f"test{test_num}\\_step_{str(i)}_uo_")
            i += 1
            node_uo = bdd_uo_copy.get_parents_of_pos_and_neg_leaf()
        #3
        tp_new, fp_new = self.calc_tp_fp(test_num, "end_")
        print("\nNew values: \ntp: " + f"{float(tp_new):.8f}" + "\nfp: " + f"{float(fp_new):.8f}")
        #4
        is_acceptable = self.check_acceptable(fp_new)
        print(
            f"\nThe fp Value ({float(fp_new):.8f}) is {'not ' if not is_acceptable else ''}acceptable. "
            f"-> {float(fp_new):.4f} "f"{'>' if not is_acceptable else '<='} {self.acceptable_threshold}")
        return tp_old, fp_old, tp_new, fp_new
        


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
    # 0    0.54   0.04 0.58
    # 1    0.06   0.36 0.42
    #      0.6    0.4
    #
    # y'\y  0     1
    # 0    0.18  0.06 0.24
    # 1    0.1   0.66 0.76
    #      0.28  0.72

    # z'\z  0     1
    # 0    0.35  0.02 0.37
    # 1    0.04  0.59 0.63
    #      0.39  0.61  
    
    #Beispiel notes Paul
    p = {
        "x": [mpq(0.54), mpq(0.04), mpq(0.06), mpq(0.36)],
        "y": [mpq(0.18), mpq(0.06), mpq(0.1), mpq(0.66)],
        "z": [mpq(0.35), mpq(0.02), mpq(0.04), mpq(0.59)]
    }
    f = "((x and y) or ((x and not y) and not z)) or (((not x and y) and not z) or ((not x and not y) and z))"
    #f = "x and not z and y"
    uo = "(x and z) or (not x and y)"
    
    #Beispiel Paper Martin
    p1 = {
        "A1": [mpq(0.54), mpq(0.04), mpq(0.06), mpq(0.36)],
        "A2": [mpq(0.18), mpq(0.06), mpq(0.1), mpq(0.66)],
        "A3": [mpq(0.35), mpq(0.02), mpq(0.04), mpq(0.59)]
    }
    f1 = "(not A1 and A2 and A3) or (A1 and not A2 and A3) or (A1 and A2 and not A3)"
    uo1 = "(not A1 and not A2 and A3) or (not A1 and A2 and not A3) or (A1 and not A2 and not A3)"
    

    p2 = {
        "a": [mpq(0.05), mpq(0.65), mpq(0.05), mpq(0.25)],
        "b": [mpq(0.2), mpq(0.4), mpq(0.1), mpq(0.3)],
        "c": [mpq(0.13), mpq(0.62), mpq(0.1), mpq(0.15)]
    }
    f2 = "a and ((b or c) and (a or not c))"
    uo2 = "not a and (b or (not b and c))"

    p3 ={
        "m": [mpq(0.7), mpq(0.03), mpq(0.17), mpq(0.1)],
        "n": [mpq(0.08), mpq(0.53), mpq(0.03), mpq(0.36)],
        "l": [mpq(0.25), mpq(0.31), mpq(0.27), mpq(0.17)]
    }
    f3 = "((m or l) and (not m and n)) or (m and n)"
    uo3 = "(not m and not n) or (n and l)"


    f4 = "(not X5 or X2 or X1) and (not X1 or not X4 or not X3) and (not X4 or X5 or not X1) and (X5 or not X3 or not X4) and (X5 or X3 or X4) and (not X4 or X3 or not X1) and (X4 or X5 or X2) and (not X4 or not X2 or X3) and (not X5 or X2 or X1) and (X3 or not X5 or not X2) and (not X4 or not X3 or X5) and (X1 or X3 or not X2) and (not X5 or X2 or X3) and (X2 or X4 or X3) and (not X1 or X2 or X3) and (not X2 or not X1 or X3) and (X1 or X2 or X4) and (not X2 or not X3 or X1) and (X3 or X1 or X2) and (X2 or X4 or X1)"
    uo4 = "(not X4 or not X2 or X3) and (not X5 or not X2 or X4) and (not X4 or not X2 or X1) and (X1 or not X3 or not X2) and (X1 or X5 or X3) and (X3 or not X1 or X5) and (not X2 or not X1 or X4) and (not X3 or not X1 or X4) and (X5 or X4 or not X3) and (not X1 or not X4 or X2) and (X1 or X5 or not X3) and (not X1 or X4 or not X5) and (not X2 or not X3 or not X1) and (X4 or X2 or not X3) and (X2 or X3 or X5) and (X1 or not X3 or not X5) and (X2 or X3 or not X1) and (not X1 or X5 or X4) and (not X2 or not X5 or not X1) and (X2 or X5 or X3)"
    p4 = {
        "X1": [mpq(0.2), mpq(0.3), mpq(0.4), mpq(0.1)],
        "X2": [mpq(0.15), mpq(0.6), mpq(0.13), mpq(0.12)],
        "X3": [mpq(0.23), mpq(0.17), mpq(0.2), mpq(0.4)],
        "X4": [mpq(0.25), mpq(0.31), mpq(0.27), mpq(0.17)],
        "X8": [mpq(0.05), mpq(0.65), mpq(0.05), mpq(0.25)],
        "X5": [mpq(0.2), mpq(0.4), mpq(0.1), mpq(0.3)],
        "X7": [mpq(0.13), mpq(0.62), mpq(0.1), mpq(0.15)],
        "X6": [mpq(0.08), mpq(0.53), mpq(0.03), mpq(0.36)]
        }
    
    
    
    delete_all_files_from_out()
    
    start_time_1 = time.time()
    model = Model(0.05, uo, f, p, True)
    tp_old, fp_old, tp_new, fp_new = model.algorithm("0")
    if(tp_old > 0): tp_change = float((tp_new -tp_old) / tp_old)
    if(fp_old > 0): fp_change = float((fp_new - fp_old) / fp_old)
    print (tp_change*100)
    print(fp_change*100)
    
    start_time_1 = time.time()
    model = Model(0.05, uo1, f1, p1, True)
    tp_old, fp_old, tp_new, fp_new = model.algorithm("1")
    if(tp_old > 0): tp_change = float((tp_new -tp_old) / tp_old)
    if(fp_old > 0): fp_change = float((fp_new - fp_old) / fp_old)
    print (tp_change*100)
    print(fp_change*100)
    #print(f"Test 1 took {float(time.time()-start_time_1):.5f} milliseconds.")
    
    #start_time_2 = time.time()
    #model2 = Model(0.05, uo2, f2, p2)
    #model2.algorithm("2")
    #print(f"Test 2 took {float(time.time()-start_time_2):.5f} milliseconds.")
    
    #start_time_3 = time.time()
    #model3 = Model(0.05, uo3, f3, p3)
    #model3.algorithm("3")
    #print(f"Test 3 took {float(time.time()-start_time_3):.5f} milliseconds.")
    
    #start_time_4 = time.time()
    #model4 = Model(0.05, uo4, f4,p4,  True)
    #model4.algorithm("4")
    #print(f"Test 4 took {float(time.time()-start_time_4):.5f} milliseconds.")
    
    BDD("X and Y",["X","Y"]).generateDot("X and Y")