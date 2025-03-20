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
        return solution, duration
    except Exception as e:
        print(f"Error bei formula {formulae[0]} and {formulae[1]}: {e}")
        return [0, 0, 0, 0], 0

class exec:
    
    if __name__ == "__main__":
        
        max_workers = int(sys.argv[1])
        num_variables = int(sys.argv[2])
        path = sys.argv[3]
        dest_path = sys.argv[4]
        
        with open(path, 'r') as file:
            lines = file.readlines()
        formulae = list(zip(lines[::2], lines[1::2]))
        delete_all_files_from_out()

        print("Tests start now")
        i = 0
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            calculate = partial(calculate_example, variables = num_variables)
            futures = []
            for f in formulae:
                future = executor.submit(calculate, f)
                futures.append(future)
        
            for future in concurrent.futures.as_completed(futures):
                try:
                    s = future.result() 
                    
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
                    
                    if(tp_old > 0): tp_change = float((tp_new -tp_old) / tp_old)
                    if(fp_old > 0): fp_change = float((fp_new - fp_old) / fp_old)
                    
                    calc_time = s[1]
                    
                    with open(dest_path, "a", newline="") as out:
                        writer = csv.writer(out)
                        if(tp_old > 0 and fp_old > 0):
                            writer.writerow([tp_change, fp_change, calc_time])
                        else:
                            print("Error in the generation of probabilities. Case cannot be used")
                        out.flush()
                        
                except Exception as e:
                    print(f"Error in process: {e}")
        
        out.close()
        
        print("All tests done")

