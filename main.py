# This is a sample Python script.
from tabulate import tabulate

from Case import Case

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #print("Test:")
    #testCase = Case(3, 2, 0.003, 0.05)

    print('Welcome. \nUse test cases?(y/n)')
    if input() == "y":
        size = 6
        inputCount = 6
        p = 0.003
        tol = 0.05

    else:
        print("How big is the object?")
        size = int(input())

        print("How many inputs does the system have?")
        inputCount = int(input())

        print("How big is the probability that one bit is flipped?")
        p = int(input())

        print("How high is the socially accepted tolerance for false positives?")
        tol = int(input())

    caseSols = []
    for i in range(1, size + 1):
        print("\n\nCase: " + str(i))
        case = Case(inputCount, i, p, tol)
        sol = case.solution
        if sol:
            caseSols.append([i, sol[0], round(sol[1], 2), round(sol[2], 5)])

    print("\n\n"+tabulate(caseSols, headers=['minSize', 'x', 'tp', 'fp']))
