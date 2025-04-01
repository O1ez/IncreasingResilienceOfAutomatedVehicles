import matplotlib.pyplot as plt
import sys
import numpy as np
from gmpy2 import mpq
import statistics

class plot:
    
    def scatterplot_change(ratios, solution_paths):
        i=0
        for s in solution_paths:
            tp = []
            fp = []
            t = []
            points_under_0 = 0
            points = 0
            tp_positive_change = 0
            with open(s, "r") as file:
                for line in file:
                    vals = line.split(",")
                    
                    if float(vals[0]) != 0 and float(vals[1]) != 0:
                        tp.append(float(vals[0]))
                        fp.append(float(vals[1]))
                        points += 1
                    if float(vals[0]) < 0 and float(vals[1]) < 0:
                        points_under_0 += 1
                    if float(vals[0]) > 0:
                        tp_positive_change += 1
                    
            plt.scatter(tp, fp, label = ratios[i])
            i+=1
        return points_under_0, points, tp_positive_change
        
    def scatterplot_calc_change(ratios, solution_paths):
        i = 0
        points_under_0 = 0
        points = 0
        tp_positive_change = 0
        for s in solution_paths:
            tp = []
            fp = []
            
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
                    if tp_change != 0 and fp_change != 0:
                        tp.append(tp_change)
                        fp.append(fp_change)
                        points += 1
                        
                    if tp_change < 0 and fp_change < 0:
                        points_under_0 += 1
                        
                    if tp_change > 0:
                        tp_positive_change +=1
                    
            plt.scatter(tp, fp, label = ratios[i])
            i+=1
        return points_under_0, points, tp_positive_change
    
    def get_time(ratios, solution_paths):
        
        plt.style.use('_mpl-gallery')
        x = ratios
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
        plt.figure(figsize=(4, 3))
        plt.plot(x, mean_list, marker='o', linestyle='-', color='b')  
        plt.xlabel("r= c/v")
        plt.ylabel("Mean time in seconds")
        plt.tight_layout()
        plt.xlim(left = 0.9)  
        plt.ylim(bottom = 0)
        plt.show()
        
        plt.figure(figsize=(4, 3))
        plt.plot(x, median_list, marker='o', linestyle='-', color='g')  
        plt.xlabel("r = c/v")
        plt.ylabel("Median time in seconds")
        plt.tight_layout()
        plt.xlim(left = 0.9)  
        plt.ylim(bottom = 0)
        plt.show()
        
    def get_number_changes(ratios, solution_paths):
        plt.style.use('_mpl-gallery')
        nochanges = []
        
        for s in solution_paths:
            unchanged = 0
            with open(s, "r") as file:
                    for line in file:
                        vals = line.split(",")
                        if vals[0] == vals[1] and vals[2] == vals[3]:
                            unchanged += 1
            nochanges.append(unchanged)
            
        
        fig, ax = plt.subplots(figsize=(5, 3))
        ratios_str = [str(r) for r in ratios]
        ax.bar(ratios_str, nochanges, color='tab:red')
        
        ax.grid(True, which='minor', axis='both', linestyle=':', color='gray', linewidth=0.5)

        ax.set_ylabel('unchanged samples')
        ax.set_yticks(range(0, 51, 10))
        ax.set_yticks(range(0, 50, 2), minor=True) 
        ax.set_ylim(0,50)
        ax.set_xlabel('ratios c/v')
        ax.minorticks_on()
        
        plt.tight_layout()
        
        plt.show()
        
    def plot_time_exp_change(v_num, solution_paths):
        plt.style.use('_mpl-gallery')
        x = v_num
        time = []
        for s in solution_paths:
            print(s)
            t = 0
            
            with open(s, "r") as file:
                for line in file:
                    vals = line.split(",")
                    t += (float(vals[4]))
            time.append((t / 60)/ 60)
            
        fig, ax = plt.subplots(figsize=(4, 3))
        plt.plot(x, time, marker='o', linestyle='-', color='orange')  
        
        plt.xlim(left = 9, right = 21)  
        plt.ylim(bottom = 0)
        plt.xlabel("variable count")
        ax.set_xticks([10, 15, 20])
        ax.grid(True)
        ax.set_xticklabels([10, 15, 20])
        plt.ylabel("computation time in h")
        plt.tight_layout()
        #plt.show()
        plt.savefig("./test_plot.pdf")
        
        
    if __name__ == "__main__":
        #increase of tp rate in percent 
        #fig, ax = plt.subplots()
        #plt.xlabel("tp change")
        #plt.ylabel("fp change")
        #plt.grid()
        #
        #solution_paths = [
        #    "solutions/15/solutions_15_100_1.0.txt",
        #    "solutions/15/solutions_15_100_1.25.txt",
        #    "solutions/15/solutions_15_100_1.5.txt",
        #    "solutions/15/solutions_15_100_2.0.txt",
        #    "solutions/15/solutions_15_100_2.5.txt"
        #]
        #ratios = [1.0, 1.25, 1.5, 2.0, 2.5]
        #points_under_0, points, tp_pos = scatterplot_calc_change(ratios, solution_paths)
    #
        #ax.legend(title = "r = c/v")
        #
        #print(f"There are {points} with {points_under_0} under 0. \n {tp_pos} had positive changes in true pos")
        #plt.show()
        ##__________________________________________________________________________________
        #fig, ax = plt.subplots()
        #plt.xlabel("tp change")
        #plt.ylabel("fp change")
        #plt.grid()
        #
        #solution_paths = [
        #    "solutions/15/solutions_15_100_3.0.txt",
        #    "solutions/15/solutions_15_100_3.5.txt",
        #    "solutions/15/solutions_15_100_4.0.txt",
        #    "solutions/15/solutions_15_100_4.2.txt"
        #]
        #ratios = [3.0, 3.5, 4.0, 4.2]
        #points_under_0, points, tp = scatterplot_calc_change(ratios, solution_paths)
        #
        #ax.legend(title = "r = c/v")
        #print(f"There are {points} with {points_under_0} under 0")
        #plt.show()
        #
        #ratios = [
        #    1.0, 1.25, 1.5,
        #    2.0, 2.5, 3.0, 3.5, 4.0, 4.2]
        #get_time(ratios, [
        #    "solutions/15/solutions_15_100_1.0.txt",
        #    "solutions/15/solutions_15_100_1.25.txt",
        #    "solutions/15/solutions_15_100_1.5.txt",
        #    "solutions/15/solutions_15_100_2.0.txt",
        #    "solutions/15/solutions_15_100_2.5.txt",
        #    "solutions/15/solutions_15_100_3.0.txt",
        #    "solutions/15/solutions_15_100_3.5.txt",
        #    "solutions/15/solutions_15_100_4.0.txt",
        #    "solutions/15/solutions_15_100_4.2.txt"
        #])
        #
        #solution_paths= ["solutions/15/solutions_15_100_1.0.txt",
        #    "solutions/15/solutions_15_100_1.25.txt",
        #    "solutions/15/solutions_15_100_1.5.txt",
        #    "solutions/15/solutions_15_100_2.0.txt",
        #    "solutions/15/solutions_15_100_2.5.txt",
        #    "solutions/15/solutions_15_100_3.0.txt",
        #    "solutions/15/solutions_15_100_3.5.txt",
        #    "solutions/15/solutions_15_100_4.0.txt",
        #    "solutions/15/solutions_15_100_4.2.txt"]
        #ratios = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.2]
        #get_number_changes(ratios, solution_paths)
        #
        solution_paths= ["solutions/10/solutions_10_100_1.5.txt",
            "solutions/15/solutions_15_100_1.5.txt"
            ]
        v_num = [10, 15]
        plot_time_exp_change(v_num, solution_paths)