import math

from TruthTableOut import TruthTableOut
import scipy


class Case:
    def __init__(self, variableCount, minSize, probBitFlipped, sociallyAcceptable):
        self.variableCount = variableCount
        self.minSize = minSize
        self.probBitFlipped = probBitFlipped
        self.sociallyAcceptable = sociallyAcceptable
        self.rowCount = pow(2, variableCount)
        self.tableIn = []
        self.tableOut = []

        for i in range(0, self.rowCount):
            row = []
            detected = 0
            for j in range(variableCount - 1, -1, -1):
                num = int((i / pow(2, j)) % 2)
                row.append(num == 1)
                detected += num
            self.tableIn.append(row)
            if detected == 0:
                self.tableOut.append(TruthTableOut.FALSE)
            elif detected < minSize:
                self.tableOut.append(TruthTableOut.DONTCARE)
            else:
                self.tableOut.append(TruthTableOut.TRUE)
        self.acceptableFalsePositive = self.getFalsePositive()
        self.acceptableTruePositive = self.getTruePositive()[0]
        self.maxTruePositive = self.getTruePositive()[1]

        dontCaresSet = self.maxTruePositive[1]
        maxTruePositive = self.maxTruePositive[0]
        falsePositive = self.acceptableFalsePositive[dontCaresSet]
        self.solution = {dontCaresSet, maxTruePositive, falsePositive}


    def getSolution(self):
        return self.solution
    def getFalsePositive(self):
        # i represent bits flipped
        sol = {}
        dcCount = sum(1 for x in self.tableOut if x == TruthTableOut.DONTCARE)
        # init solution Map
        for i in range(0, dcCount + 1):
            sol[i] = 0
        # calc factor for first summand and put x corresponding to Map key
        for i in range(1, self.variableCount + 1):
            factor = math.comb(self.variableCount, 0) * math.comb(self.variableCount, i) * math.comb(0, 0)
            p = pow(self.probBitFlipped, i)
            xPresent = i < self.minSize
            # j are dont cares set to true
            for j in range(0, dcCount + 1):
                if xPresent:
                    sol[j] += factor * p * j
                else:
                    sol[j] += factor * p
        print("These are the false positive probabilities for different evaluations of the Don't Cares")
        for i in sol:
            print(i, sol[i]*100, "%")
        print("These are the false positive probabilities that are acceptable")
        # map consisting of keys Dont Cares set and values correlated false positive
        acceptableFalsePositive = {key: value for key, value in sol.items() if
                                   value < self.sociallyAcceptable}
        for i in acceptableFalsePositive:
            print(i, acceptableFalsePositive[i] * 100, '%')
        return acceptableFalsePositive

    def getTruePositive(self):
        sol = {}
        dcCount = sum(1 for x in self.tableOut if x == TruthTableOut.DONTCARE)
        # init solution Map
        for i in range(0, dcCount + 1):
            sol[i] = 0
        # notes page 177
        for i in range(self.minSize, self.variableCount + 1):
            for j in range(0, self.variableCount - i + 1):
                for m in range(0, i + 1):
                    # if no 0's are flipped and all 1's are supposed to be flipped break, because perception would
                    # not be positive
                    if j == 0 and m == i:
                        break
                    factor = math.comb(self.variableCount, i) * math.comb(self.variableCount - i, j) * math.comb(i, m)
                    bitsFlipped = j + m
                    #TODO: How to incorporate 0 bits flipped??
                    #p = pow(self.probBitFlipped, bitsFlipped) if bitsFlipped > 0 else pow(1-self.probBitFlipped, 3)
                    p = pow(self.probBitFlipped, bitsFlipped) * pow(1-self.probBitFlipped, self.variableCount-self.probBitFlipped)

                    bitsSet = i + j - m
                    xPresent = bitsSet < self.minSize
                    # for every value x can take i.e. 0..Don'tCareCount
                    for l in range(0, dcCount+1):
                        if xPresent:
                            sol[l] += factor * p * l
                        else:
                            sol[l] += factor * p
        print("These are the true positive probabilities for different evaluations of the Don't Cares")
        for i in sol:
            print(i, sol[i] * 100, '%')
        print("These are the true positive probabilities for the acceptable fp")
        acceptableTruePositive = {key: value for key, value in sol.items() if key in self.acceptableFalsePositive}
        for i in acceptableTruePositive:
            print(i, acceptableTruePositive[i] * 100, '%')
        maxTP = max(zip(acceptableTruePositive.values(), acceptableTruePositive.keys()))
        print("Maximal tp rate is achieved at ", maxTP[0], " with ", maxTP[1], " Don't Cares set")
        return acceptableTruePositive, maxTP
