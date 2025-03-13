from formula_generator import formula_generator
from model import Model
import concurrent.futures
from bdd import BDD, BDDNode, delete_all_files_from_out
import time
import math
import sys

def calculate_example(formulae):
        #print(f"\033[96m\n\033[1mTest:\033[0m\n")
        start = time.time()

        uo = formulae[0]
        f = formulae[1]
        contingency_tables = formula_generator.generate_contingency_tables(20)
        model = Model(0.05, uo, f, contingency_tables)
        solution = model.algorithm("")
        
        duration = time.time() - start
        #print(f"\nTest took {duration:.5f} milliseconds and {duration/1000} seconds and {(duration/1000)/60} minutes")
        #print("---------------------------------\n")
        return solution, duration

class exec:
    if __name__ == "__main__":
        
        path = sys.argv[1]
        with open(path, 'r') as file:
            lines = file.readlines()
        formulae = list(zip(lines[::2], lines[1::2]))
        delete_all_files_from_out()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
            solutions = list(executor.map(calculate_example, formulae))
            
        for s in solutions:
            print(f"{s}\n\n-----------------------------------")
        
        
        print("All tests done")

