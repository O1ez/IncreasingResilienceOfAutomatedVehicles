from sklearn.metrics import confusion_matrix
from BDD.BDD import BDD, BDDNode
from typing import Optional
class Model:    
    def __init__(self, acceptable_threshhold : float, observations= None, uo: Optional[BDD]=None, f : Optional[BDD] = None, ground_truth=None, vars=None):
        self.observations = observations
        self.ground_truth = ground_truth
        self.acceptable_threshold = acceptable_threshhold
        self.uo = uo
        self.f = f
        self.vars = vars
        self.bbd_observations = BDD(observations, vars)
        self.bdd_ground_truth = BDD(ground_truth, vars)

    def calc_tp_fp(self):
        eval_ground_truth = self.change_log_val_to_num_val(self.bdd_ground_truth.evaluation.values())
        eval_observations = self.change_log_val_to_num_val(self.bbd_observations.evaluation.values())
        abs_tn, abs_fp, abs_fn, abs_tp = confusion_matrix(eval_ground_truth, eval_observations).ravel()
        #tp= tp Cases / (all positive cases) fp= fp cases / (all neg cases)
        return abs_tp/(abs_tp+abs_fn), abs_fp/(abs_tn+abs_fp) 
    
    def change_log_val_to_num_val(self, values):
        return [1 if v else 0 for v in values]
    
    def check_acceptable(self, fp: float):
        return fp < self.acceptable_threshold
    
    def find_node_in_uo(self) -> BDDNode:
        nodes = self.uo.breadth_first_bottom_up()
        while nodes:
            n = nodes.pop_left()
            if n.negative_child.value is not None and n.positive_child.value is not None:
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
                if assignment[var] == True:
                    current_node=current_node.positive_child
                else: 
                    current_node=current_node.negative_child
            found_nodes.append(current_node)
        return found_nodes
    
    
    def algorithm(self):
        #1
        tp, fp = self.calc_tp_fp()
        #2
        child_uo = self.find_node_in_uo()
        while ()
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
        #4
        is_acceptable = self.check_acceptable()



    

    
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

vars = ["x", "y", "z"]
f_guard = "(x and y) or (not x and y and not z) or (not x and not y and z)"
unobservable = "(x and z) or (not x and y)"
bdd_f = BDD(variables= vars, expression= f_guard)
bdd_f.reduce()
bdd_f.generateDot("f_out")

bdd_uo = BDD(unobservable, vars)
bdd_uo.reduce()
bdd_uo.generateDot("uo_out")
model = Model(uo=unobservable, vars=vars)

