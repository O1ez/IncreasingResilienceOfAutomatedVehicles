from sklearn.metrics import confusion_matrix
from BDD.BDD import BDD
class Model:    
    def __init__(self, observations, unobservable, ground_truth, vars):
        self.observations = observations
        self.unobservable = unobservable
        self.ground_truth = ground_truth
        self.vars = vars
        self.bbd_observations = BDD(observations, vars)
        self.bdd_unobservable = BDD(unobservable, vars)
        self.bdd_ground_truth = BDD(ground_truth, vars)

    def calc_tp_fp(self):
        eval_ground_truth = self.change_log_val_to_num_val(self.bdd_ground_truth.evaluation.values())
        eval_observations = self.change_log_val_to_num_val(self.bbd_observations.evaluation.values())
        abs_tn, abs_fp, abs_fn, abs_tp = confusion_matrix(eval_ground_truth, eval_observations).ravel()
        #tp= tp Cases / (all positive cases) fp= fp cases / (all neg cases)
        return abs_tp/(abs_tp+abs_fn), abs_fp/(abs_tn+abs_fp) 
    
    def find_node_to_remove(self):
        nodes = self.unobservable.breadth_first_bottom_up()
        removed_node = None
        while nodes:
            n = nodes.pop_left()
            if n.left.value is not None and n.right.value is not None:
                if n.left.value + n.right.value == 1:
                    self.unobservable.remove(n)
                    return n
    
    def change_log_val_to_num_val(self, values):
        return [1 if v else 0 for v in values]
    
    def algorithm(self):
        tp, fp = self.calc_tp_fp()
        self.find_node_to_remove()
    

    
#Example:
vars = ["A1", "A2", "A3"]
observations = "(A2 or A3)"
f_guard = "(not A1 and A2) or (A1 and not A3) or (not A2 and A3)"
unobservable = "(A1 and not A2 and not A3) or (not A1 and A2 and not A3) or (not A1 and not A2 and A3)"
ground_truth = "(not A1 and A2 and A3) or (A1 and not A2 and A3) or (A1 and A2 and not A3)"
model = Model(observations, unobservable, ground_truth, vars)
print(f"Ground Truth: {model.bdd_ground_truth.evaluation.values()}")
print(f"observations: {model.bbd_observations.evaluation.values()}")
tp, fp = model.calc_tp_fp()
print(f"tp: {tp}, fp: {fp}")

    

