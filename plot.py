import matplotlib.pyplot as plt
import sys
import numpy as np
from gmpy2 import mpq
import statistics

class plot:
    
    def scatterplot_change(solution_paths):
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
        
    def scatterplot_calc_change(solution_paths):
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
    
    def get_time(solution_paths):
        
        plt.style.use('_mpl-gallery')
        x = [1.0, 2.0, 3.0, 3.5, 4.0, 4.2]
        mean_list = []
        median_list = []
        for s in solution_paths:
            print(s)
            times = []
            times_all = []
            unchanged = 0
            changed = 0
            
            with open(s, "r") as file:
                for line in file:
                    vals = line.split(",")
                    if vals[0] == vals[1] and vals[2] == vals[3]:
                        unchanged += 1
                        times_all.append(float(vals[4]))
                    else:
                        changed += 1
                        times.append(float(vals[4]))
                        times_all.append(float(vals[4]))
            
            mean_all = statistics.mean(times_all)
            mean_list.append(mean_all)
            median_all = statistics.median(times_all)
            median_list.append(median_all)
            print (f"The mean time is {mean_all} s and {mean_all / 60 } m and {(mean_all/60)/60} h and {((mean_all/60)/60)/24} d")
            print(f"{unchanged} examples have led to no change. {changed} examples have changed.")
            print(f"Calculations have lasted {sum(times_all)} seconds {((sum(times_all) /60)/60)/24} days")
            print("____________________________________________________________________________________________________________________________________")
        plt.figure(figsize=(8, 6))
        plt.plot(x, mean_list, marker='o', linestyle='-', color='b')  
        plt.xlabel("l/c ratio")
        plt.ylabel("Mean time in seconds")
        plt.tight_layout()
        plt.xlim(0.75, 5)  
        plt.ylim(-0.25, 25000)
        plt.show()
        
        plt.figure(figsize=(8, 6))
        plt.plot(x, median_list, marker='o', linestyle='-', color='g')  
        plt.xlabel("l/c ratio")
        plt.ylabel("Median time in seconds")
        plt.tight_layout()
        plt.xlim(0.75, 5)  
        plt.ylim(-0.25, 11000)
        plt.show()
        
    if __name__ == "__main__":
        plt.xlabel("tp change")
        plt.ylabel("fp change")
        
        #solution_paths = ["solutions/10/solutions_10_50_1.0.txt",
        #                    "solutions/10/solutions_10_50_2.0.txt",
        #                    "solutions/10/solutions_10_50_2.5.txt",
        #                    "solutions/10/solutions_10_50_3.0.txt",
        #                    "solutions/10/solutions_10_50_4.1.txt"]
        
        np.arange(0, 5, 1)
        plt.xlim(-2, 5)  
        plt.ylim(-2, 5)
        plt.grid()
        
        solution_paths = ["solutions/15/solutions_15_100_2.0.txt"]
        scatterplot_calc_change(solution_paths)
        
        solution_paths = ["solutions/15/solutions_15_100_1.5.txt"]
        scatterplot_change(solution_paths)
        plt.show()
        
        get_time([
            "solutions/15/solutions_15_100_1.0.txt",
            "solutions/15/solutions_15_100_2.0.txt",
            "solutions/15/solutions_15_100_3.0.txt",
            "solutions/15/solutions_15_100_3.5.txt",
            "solutions/15/solutions_15_100_4.0.txt",
            "solutions/15/solutions_15_100_4.2.txt"
        ])