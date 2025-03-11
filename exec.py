from formula_generator import formula_generator
from model import Model
from bdd import BDD, BDDNode, delete_all_files_from_out
import time
import math

class exec:
    
    if __name__ == "__main__":
        with open('formulas.txt', 'r') as file:
            formulas = file.readlines()
        contingency_tables = formula_generator.generate_contingency_tables(20)
        print(contingency_tables)
        delete_all_files_from_out()
        
        
        for i in range(0, len(formulas), 2):
            test_num= math.ceil((i+1)/2)
            print(f"\033[96m\n\033[1mTest {test_num}:\033[0m\n")
            start = time.time()

            uo = formulas[i]
            f = formulas[i+1]
            p = contingency_tables
            model = Model(0.05, uo, f, p)
            model.algorithm(f"{test_num}")
            
            duration = time.time() - start
            print(f"\nTest {test_num} took {duration:.5f} milliseconds and {duration/1000} seconds and {(duration/1000)/60} minutes")
            print("---------------------------------\n")
            
        print("All tests done")

