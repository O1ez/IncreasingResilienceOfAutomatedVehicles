import matplotlib.pyplot as plt
import sys
import numpy as np
from gmpy2 import mpq
class plot:
    
    def scatterplot_change(self, solution_paths):
        for s in solution_paths:
            tp = []
            fp = []
            t = []
            
            with open(s, "r") as file:
                for line in file:
                    vals = line.split(",")
                    tp.append(float(vals[0]))
                    fp.append(float(vals[1]))
                    t.append(float(vals[2]))
                    
            plt.scatter(tp, fp)
        
        major_ticks = np.arange(0, 5, 1)
        plt.xlim(-2, 5)  
        plt.ylim(-2, 5)
        plt.grid()
        plt.show()
        
    def scatterplot_calc_change( solution_paths):
        for s in solution_paths:
            tp = []
            fp = []
            t = []
            
            with open(s, "r") as file:
                for line in file:
                    vals = line.split(",")
                    tp_old = mpq(vals[0])
                    tp_new = mpq(vals[1])
                    fp_old = mpq(vals[2])
                    fp_new = mpq(vals[3])
                    time = vals[4]
                    
                    if(tp_old > 0): tp_change = float((tp_new -tp_old) / tp_old)
                    if(fp_old > 0): fp_change = float((fp_new - fp_old) / fp_old)
                    tp.append(tp_change)
                    fp.append(fp_change)
                    t.append(time)
                    
            plt.scatter(tp, fp)
        
        major_ticks = np.arange(0, 5, 1)
        plt.xlim(-2, 5)  
        plt.ylim(-2, 5)
        plt.grid()
        plt.show()
    
    if __name__ == "__main__":
        plt.xlabel("tp change")
        plt.ylabel("fp change")
        
        #solution_paths = ["solutions/10/solutions_10_50_1.0.txt",
        #                    "solutions/10/solutions_10_50_2.0.txt",
        #                    "solutions/10/solutions_10_50_2.5.txt",
        #                    "solutions/10/solutions_10_50_3.0.txt",
        #                    "solutions/10/solutions_10_50_4.1.txt"]
        
        solution_paths = ["solutions/10/test.txt"]
        
        scatterplot_calc_change(solution_paths)
        
        