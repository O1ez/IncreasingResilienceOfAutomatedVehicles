import random
from scipy.stats import random_table
from gmpy2 import mpq
class formula_generator:
    @staticmethod
    def generate_formulas(num_variables: int, ratio_variable_clauses: float, num_formulas: int, num_literals: int = 3) -> tuple[list[str], dict[str, list[mpq]]]:
        formulas = []
        #generate formula
        for i in range(1, num_formulas+1):
            #print(f"{i}: \n")
            formula = ""
            #generate clause
            num_clauses = int(ratio_variable_clauses * num_variables)
            for j in range(1, num_clauses + 1):
                formula = formula + "("
                used_vars = []
                #generate variable
                for k in range(1, num_literals+1):
                    variable = random.randint(1, num_variables)
                    while variable in used_vars:
                        variable = random.randint(1, num_variables)
                    used_vars.append(variable)
                    
                    if bool(random.getrandbits(1)):
                        formula = formula + "not "
                    formula = formula + f"X{variable} and "
                    
                #delete last and
                formula = formula [:-5]
                formula = formula + ") or "
                
            #delete last or
            formula = formula[:-3]
            ##print(formula + "\n\n")
            formulas.append(formula)
        contingency_tables = formula_generator.generate_contingency_tables(num_variables)
        return formulas, contingency_tables
    
    @staticmethod
    def generate_contingency_tables(num_variables: int):
        contingency_tables = {}
        for i in range(1, num_variables + 1):
            first_row_sum = random.randint(1, 100)
            second_row_sum = 100 - first_row_sum
            
            first_col_sum = random.randint(1, 100)
            second_col_sum = 100 - first_col_sum
            
            row = [first_row_sum, second_row_sum]
            col = [first_col_sum, second_col_sum]
            table = random_table.rvs(row, col)
            
            #print(table)
            first = int(table[0][0])
            second = int(table[0][1])
            third = int(table[1][0])
            fourth = int(table[1][1])
            
            contingency_tables[f"X{i}"] = [mpq(first,100), mpq(second,100), mpq(third,100), mpq(fourth,100)]
        return contingency_tables
        
if __name__ == "__main__":
    formulas = formula_generator.generate_formulas(50, 4.1, 50)