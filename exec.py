from formula_generator import formula_generator
from model import Model
from bdd import BDD, BDDNode, delete_all_files_from_out

class exec:
    
    if __name__ == "__main__":
        formulas, contingency_tables = formula_generator.generate_formulas(20, 4.1, 10)
        print("Formulas generated.")
        delete_all_files_from_out()
        
        test = BDD(formulas[0], list(contingency_tables.keys()))
        print("first formula BDD generated")
        test.generateDot()
        
        for i in range(0, len(formulas), 2):
            uo = formulas[i]
            f = formulas[i+1]
            p = contingency_tables
            model = Model(0.05, uo, f, p)
            model.algorithm(f"{int((i+1)/2)}")
            
        print("All tests done")

