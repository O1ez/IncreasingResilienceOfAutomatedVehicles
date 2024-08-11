import math

from tabulate import tabulate

from TruthTableOut import TruthTableOut
import scipy


class Case:
    def __init__(self, variableCount, minSize, probBitFlipped, tolerance):
        self.variableCount = variableCount
        self.minSize = minSize
        self.probBitFlipped = probBitFlipped
        self.tol = tolerance
        self.rowCount = pow(2, variableCount)
        self.tableIn = []
        self.tableOut = []

        self.calcTruthTable()

        self.acceptableFalsePositive = self.getFalsePositive()
        #if dict is not empty
        if bool(self.acceptableFalsePositive):
            tpOut = self.getTruePositive()
            #printing solutions
            self.acceptableTruePositive = tpOut[0]
            table = zip(self.acceptableFalsePositive.keys(), self.acceptableFalsePositive.values(),
                        self.acceptableTruePositive.values())
            print(tabulate(table, headers=["x", "fp", "tp"], floatfmt=".4f"))

            x_value = tpOut[1]
            maxTruePositive = (self.acceptableTruePositive[x_value])
            falsePositive = (self.acceptableFalsePositive[x_value])
            self.solution = [x_value, maxTruePositive, falsePositive]
            print("The Solution is:\n x=" + str(round(self.solution[0], 3)) + "  tp=" + str(
                round(self.solution[1], 3)) + "  fp=" + str(
                round(self.solution[2], 3)))
        else:
            print("Case not socially acceptable")
            self.solution = []

    # calc truth table with output
    def calcTruthTable(self):
        for i in range(0, self.rowCount):
            # list of bools containing one row
            row = []
            # num of positive Vals in row
            positiveVars = 0
            for j in range(self.variableCount - 1, -1, -1):
                thisVar = int((i / pow(2, j)) % 2)
                row.append(thisVar == 1)
                positiveVars += thisVar
            self.tableIn.append(row)
            # calculate output (all negative out=f, all positive out=t, else out=*)
            if positiveVars == 0:
                self.tableOut.append(TruthTableOut.FALSE)
            elif positiveVars < self.minSize:
                self.tableOut.append(TruthTableOut.DONTCARE)
            else:
                self.tableOut.append(TruthTableOut.TRUE)

    def getSolution(self):
        return self.solution

    def getFalsePositive(self):
        sol = {}
        dcCount = sum(1 for x in self.tableOut if x == TruthTableOut.DONTCARE)
        # init sol dict
        # j represents value of x in (0 .. Number of Don't Cares)
        for j in range(0, dcCount + 1):
            sol[j] = 0
        # calc factor for every summand in every x evaluation
        for i in range(1, self.variableCount + 1):
            #calc binomial coefficients
            #1st: of varCount there are no bits set in ground truth
            #2nd: of varCount 0s there can be (0..varCount) Bits flipped
            #3rd: of zero 1s there can be no bits flipped
            factor = (math.comb(self.variableCount, 0) * math.comb(self.variableCount, i) * math.comb(0, 0))
            p = pow(self.probBitFlipped, i) * pow(1 - self.probBitFlipped, self.variableCount - self.probBitFlipped)
            xPresent = i < self.minSize
            # j represents value of x in (0 .. Number of Don't Cares)
            for j in range(0, dcCount + 1):
                if xPresent:
                    sol[j] += factor * p * j
                else:
                    sol[j] += factor * p
        # map consisting of keys=Dont Cares set and values=correlated false positive
        #filter false positives that are higher than tolerance
        acceptableFalsePositive = {key: value for key, value in sol.items() if
                                   value < self.tol}
        return acceptableFalsePositive

    def getTruePositive(self):
        sol = {}
        dcCount = sum(1 for x in self.tableOut if x == TruthTableOut.DONTCARE)
        # init solution dict
        for i in range(0, dcCount + 1):
            sol[i] = 0
        #notes page 177
        #calc binomial coefficients
        for i in range(self.minSize, self.variableCount + 1):
            for j in range(0, self.variableCount - i + 1):
                for m in range(0, i + 1):
                    # if no 0's are flipped and all 1's are supposed to be flipped continue, because perception would
                    # not be positive -> no true positive case
                    if j == 0 and m == i:
                        continue
                    factor = math.comb(self.variableCount, i) * math.comb(self.variableCount - i, j) * math.comb(i, m)
                    bitsFlipped = j + m
                    p = pow(self.probBitFlipped, bitsFlipped) * pow(1 - self.probBitFlipped,
                                                                    self.variableCount - self.probBitFlipped)
                    bitsSet = i + j - m
                    xPresent = bitsSet < self.minSize
                    # l represents value of x in (0 .. Number of Don't Cares)
                    for l in range(0, dcCount + 1):
                        if xPresent:
                            sol[l] += factor * p * l
                        else:
                            sol[l] += factor * p
        #filter out values for which false positive is above tolerance
        acceptableTruePositive = {key: value for key, value in sol.items() if key in self.acceptableFalsePositive}
        #maximal x value with max True positive
        x_maxTp = max(acceptableTruePositive, key=acceptableTruePositive.get)
        return acceptableTruePositive, x_maxTp
