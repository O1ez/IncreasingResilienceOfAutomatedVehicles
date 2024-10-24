from itertools import product


class BDDNode:
    def __init__(self, var=None, left=None, right=None, value=None):
        self.var = var  # The variable for decision (None for terminal nodes)
        self.left = left
        self.right = right
        self.value = value  # Terminal value (True or False for leaf nodes)

    def isLeaf(self):
        # Check if the node is a terminal node (leaf with True/False)
        return self.value is not None


def evaluate_expression(expr, assignment):
    return eval(expr, {}, assignment)


class BDD:
    def __init__(self, expression, variables):
        self.variables = variables  # List of variables
        self.expression = expression
        self.current_assignment = {}
        self.root = self.build(0)  # Build the BDD starting from the first variable index

    def build(self, var_index):

        # end of recursion if node is a leaf
        if var_index == len(self.variables):
            assignment = {var: val for var, val in self.current_assignment.items()}  # copies current_assignment
            value = evaluate_expression(self.expression, assignment)
            return BDDNode(value=value)

        # Create node for false subtree and true subtree
        var = self.variables[var_index]
        self.current_assignment[var] = False
        leftNode = self.build(var_index + 1)
        self.current_assignment[var] = True
        rightNode = self.build(var_index + 1)

        return BDDNode(var=var, left=leftNode, right=rightNode)

    # traverses down the diagram to evaluate it
    def evaluate(self, node, variables):
        if node.isLeaf():
            return node.value
        if variables[node.var] is False:
            return self.evaluate(node.left, variables)
        else:
            return self.evaluate(node.right, variables)

    #displays BDD graphically
    def display(self, node=None, level=0, output=None):
        # Start from the root
        if node is None:
            node = self.root

        indent = "      " * level  # indentation based level
        if node.isLeaf():
            print(node.value)
        else:
            print(node.var)
            if node.left:
                print(f"{indent}├----", end=" ")
                self.display(node.left, level + 1)
            if node.right:
                print(f"{indent}└────", end=" ")
                self.display(node.right, level + 1)

    #def reduce(self):
        #self.removeNodesWithSameChildren()
        #self.removeDuplicateTerminalNodes()

    #def removeNodesWithSameChildren(self):

    #def removeDuplicateTerminalNodes(self):
        #positiveNode = BDDNode(value=1)
        #negativeNode = BDDNode(value=0)


# Example:
e = "(A and B) or C"
v = ['A', 'B', 'C']
bdd = BDD(e, v)

print("Binary Decision Diagram (BDD):")
bdd.display(bdd.root)

