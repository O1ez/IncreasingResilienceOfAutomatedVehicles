from formula_generator import formula_generator
from model import Model
import concurrent.futures
from multiprocessing import Value, Lock
from bdd import BDD, BDDNode, delete_all_files_from_out
import time
import math
import sys
import matplotlib.pyplot as plt
import csv
from functools import partial
import itertools

def calculate_example(index, formulae, variables ,i = ""):
    global j
    try:
        #print(f"\033[96m\n\033[1mTest:\033[0m\n")
        start = time.time()

        uo = formulae[0]
        f = formulae[1]
        contingency_tables = formula_generator.generate_contingency_tables(variables)
        
        model = Model(0.05, uo, f, contingency_tables)
        solution = model.algorithm(i)
        
        duration = time.time() - start
        #print(f"\nTest took {duration:.5f} milliseconds and {duration/1000} seconds and {(duration/1000)/60} minutes")
        #print("---------------------------------\n")

        print(f"Test {index} done!")

            
        return solution, duration
    except Exception as e:
        print(f"Error at calculation: {e}")
        return [0, 0, 0, 0], 0

class exec:
    
    if __name__ == "__main__":
        
        max_workers = int(sys.argv[1])
        num_variables = int(sys.argv[2])
        source_path = sys.argv[3]
        dest_path = sys.argv[4]
        
        with open(source_path, 'r') as file:
            lines = file.readlines()
        formulae = list(zip(lines[::2], lines[1::2]))
        delete_all_files_from_out()

        print("Tests start now")
        i = 0
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            calculate = partial(calculate_example, variables = num_variables)
            solutions = list(executor.map(calculate, itertools.count(), formulae))
    
        out = open(dest_path, "a", newline="")
        for s in solutions:
            
            tp_old = s[0][0]
            fp_old = s[0][1]
            
            tp_new = s[0][2]
            fp_new = s[0][3]
            
            #tp or fp unsatisfiable
            if(tp_old == 0 or tp_new == 0 or fp_old==0 or fp_new == 0):
                continue
            
            i += 1
            print(f"Test {i} done:")
            print(f"{s}\n\n-----------------------------------")
            
            #if(tp_old > 0): tp_change = float((tp_new -tp_old) / tp_old)
            #if(fp_old > 0): fp_change = float((fp_new - fp_old) / fp_old)
            
            calc_time = s[1]
            
            writer = csv.writer(out)
            if(tp_old > 0 and fp_old > 0):
                writer.writerow([tp_old, tp_new, fp_old, fp_new, calc_time])
            else:
                print("Error in the generation of probabilities. Case cannot be used")
                    
        out.close()
        
        print("All tests done")

