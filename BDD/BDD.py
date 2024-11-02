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

    def generate_latex(self, node=None, level = 0):
        node = self.root
        out = open("BDD\out\output.tex", "w")
        out.write ("\\documentclass{article} \n\
\\usepackage{tikz-qtree} \n\
    \\begin{document} \n\
        \\begin{center} \n\
            \\tikzset{every tree node/.style={minimum width=2em,draw,circle},\
            blank/.style={draw=none}, %nodes are round\n\
            leaf/.style={draw, rectangle}, %leafs are square \n\
            edge from parent/.style= \n\
            {draw, edge from parent path={(\\tikzparentnode) -- (\\tikzchildnode)}}, \n\
            level distance=1.5cm} \n\
                \\begin{tikzpicture} \n\
                    \\Tree\n\
                   ")
        self.rec(node, level, out, False)
        out.write("          \\end{tikzpicture} \n\
                        \\end{center} \n\
                    \\end{document}\n")
        print("File generated")


    def rec(self, node, level, out, side):
        indent = "  " * level + "                    "
        if node.isLeaf(): 
            if side:
                out.write (f"\\edge[]; \\node[leaf]{{{node.value}}};\n")
            else:             
                out.write (f"\\edge[dashed]; \\node[leaf]{{{node.value}}};\n")
        else:
            out.write("[."+node.var+"\n"+indent+"\edge[dashed];\n")
            if node.left:
                out.write(indent)
                self.rec(node.left, level + 1, out, 0)
            else:
                 out.write (indent + "\\edge[blank]; \\node[blank]{};\n \\\left")
            if node.right:
                out.write(indent)
                self.rec(node.right, level + 1, out, 1)
            else:
                 out.write (indent + "\\edge[blank]; \\node[blank]{};\n \\\right")
            out.write(indent+"]\n")

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
bdd.generate_latex(bdd.root)
bdd.display(bdd.root)
