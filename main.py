# This is a sample Python script.
from Case import Case

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print("Test:")
    testCase = Case(3, 2, 0.003, 0.01)


    print('Welcome to the program. \nHow big is the object?')
    size = input()

    print("How many inputs does the system have?")
    inputCount = input()

    cases = []

    for i in range(1, (int) size+1):
        cases.append(Case(inputCount, i, 0.003, 0.001))




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
