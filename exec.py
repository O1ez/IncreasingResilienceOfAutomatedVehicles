from formula_generator import formula_generator
from model import Model
import concurrent.futures
from bdd import BDD, BDDNode, delete_all_files_from_out
import time
import math
import sys
import matplotlib.pyplot as plt
import csv
from functools import partial

def calculate_example(formulae, variables ,i = ""):
        #print(f"\033[96m\n\033[1mTest:\033[0m\n")
        start = time.time()

        uo = formulae[0]
        f = formulae[1]
        contingency_tables = formula_generator.generate_contingency_tables(10)
        
        model = Model(0.05, uo, f, contingency_tables, True)
        solution = model.algorithm(i)
        
        duration = time.time() - start
        #print(f"\nTest took {duration:.5f} milliseconds and {duration/1000} seconds and {(duration/1000)/60} minutes")
        #print("---------------------------------\n")
        return solution, duration

class exec:
    
    if __name__ == "__main__":
        
        num_variables = int(sys.argv[1])
        path = sys.argv[2]
        dest_path = sys.argv[3]
        
        with open(path, 'r') as file:
            lines = file.readlines()
        formulae = list(zip(lines[::2], lines[1::2]))
        delete_all_files_from_out()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
            calculate = partial(calculate_example, variables = num_variables)
            solutions = list(executor.map(calculate, formulae))

        
        out = open(dest_path, "w", newline="")
        for s in solutions:
            tp_old = s[0][0]
            fp_old = s[0][1]
            
            tp_new = s[0][2]
            fp_new = s[0][3]
            
            #tp or fp unsatisfiable
            if(tp_old == 0 or tp_new == 0 or fp_old==0 or fp_new == 0):
                continue
            
            print(f"{s}\n\n-----------------------------------")
            
            writer = csv.writer(out)
            
            if(tp_old > 0): tp_change = float(tp_new / tp_old)
            if(fp_old > 0): fp_change = float(fp_new / fp_old)
            
            calc_time = s[1]
            
            
            if(tp_old > 0 and fp_old > 0):
                writer.writerow([tp_change, fp_change, calc_time])
            else:
                print("Error in the generation of probabilities. Case cannot be used")
                
        out.close()
        
        print("All tests done")

