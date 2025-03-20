import matplotlib.pyplot as plt
import sys
import numpy as np
class exec:
    
    if __name__ == "__main__":
        plt.xlabel("tp change")
        plt.ylabel("fp change")
        
        solution_paths = ["solutions/10/solutions_10_50_1.0.txt",
                            "solutions/10/solutions_10_50_2.0.txt",
                            "solutions/10/solutions_10_50_2.5.txt",
                            "solutions/10/solutions_10_50_3.0.txt",
                            "solutions/10/solutions_10_50_4.1.txt"]
        
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