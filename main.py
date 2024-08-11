# This is a sample Python script.
from tabulate import tabulate

from Case import Case

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #print("Test:")
    #testCase = Case(3, 2, 0.003, 0.05)

    print('Use test cases?(y/n)')
    if input() == "y":
        #Test case inputs
        #size of object
        size = 4
        #number of inputs
        inputCount = 6
        #probability that one bit is flipped
        p = 0.005
        #maximal value false positive is allowed to be
        tol = 0.3

    else:
        print("How big is the object?")
        size = int(input())

        print("How many inputs does the system have?")
        inputCount = int(input())

        print("How big is the probability that one bit is flipped?")
        p = int(input())

        print("How high is the socially accepted tolerance for false positives?")
        tol = int(input())

    #minsize describes minimum count of Variables that have to be true to detect the object
    #make Cases for minsize = (1..realObjectSize)
    caseSols = []
    for i in range(1, size + 1):
        print("\n\nCase: k=" + str(i))
        case = Case(inputCount, i, p, tol)
        sol = case.solution
        if sol:
            caseSols.append([i, sol[0], round(sol[2], 5), round(sol[1], 5)])

    print("\n\n"+tabulate(caseSols, headers=['minSize', 'x', 'fp', 'tp']))
