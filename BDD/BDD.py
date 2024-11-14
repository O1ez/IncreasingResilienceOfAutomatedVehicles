from itertools import product


class BDDNode:
    def __init__(self, var=None, left=None, right=None, value=None):
        self.var = var  # The variable for decision (None for terminal nodes)
        self.left = left
        self.right = right
        self.value = value  # Terminal value (True or False for leaf nodes)
        self.drawn = False

    def isLeaf(self):
        # Check if the node is a terminal node (leaf with True/False)
        return self.value is not None
    
    def __eq__(self, other):
        if other is None or not isinstance(other, BDDNode):
            return False
        if self.isLeaf() and other.isLeaf():
            return self.value == other.value
        return (
            self.var == other.var and
            self.left == other.left and
            self.right == other.right
        )
    
    def __hash__(self):
        # Hash für Leaf-Nodes basierend auf ihrem Wert, ansonsten auf (var, left, right)
        if self.isLeaf():
            return hash(self.value)
        return hash((self.var, self.left, self.right))

def evaluate_expression(expr, assignment):
    return eval(expr, {}, assignment)


class BDD:
    def __init__(self, expression, variables):
        self.variables = variables  # List of variables
        self.expression = expression
        self.current_assignment = {}
        self.leafs= {False: BDDNode(value=False), True:BDDNode(value=True)}
        self.root = self.build(0)  # Build the BDD starting from the first variable index

    def build(self, var_index):

        # end of recursion if node is a leaf
        if var_index == len(self.variables):
            assignment = {var: val for var, val in self.current_assignment.items()}  # copies current_assignment
            value = evaluate_expression(self.expression, assignment)
            #leaf_vals = list(leaf.value for leaf in self.leafs)
            #if value not in leaf_vals:
            #    self.leafs.add(BDDNode(value))
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
        
    def reduce(self):
        self.remove_duplicate_subtree(self.root, mem = {})
        self.merge_leafs(self.root)
        self.remove_equivalent_child_nodes(self.root)
        print("Reduction done.")

    def remove_duplicate_subtree(self, node, mem):
        if node.isLeaf():
            return node
        if node in mem:
            return mem[node]
        node.left = self.remove_duplicate_subtree(node.left, mem)
        node.right = self.remove_duplicate_subtree(node.right, mem)
        if node in mem:
            return mem[node]
        mem[node] = node
        return node

    def merge_leafs(self, node):
        if node.isLeaf():
            return node.value
        left = self.merge_leafs(node.left)
        if left is not None:
            node.left = self.leafs.get(left)
        right = self.merge_leafs(node.right)
        if right is not None:
            node.right = self.leafs.get(right)
        return None 

    def remove_equivalent_child_nodes(self, node):
        if node.left is not None:
            eq_child_left = self.remove_equivalent_child_nodes(node.left)
            if eq_child_left is not None:
                node.left = eq_child_left
        if node.right is not None:
            eq_child_right = self.remove_equivalent_child_nodes(node.right)
            if eq_child_right is not None:
                node.right = eq_child_right
        if node.left is not None and node.right is not None and id(node.left) == id(node.right):
            return node.right
        return None
        

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

    def generate_latex(self, filename="output", node=None, level = 0):
        node = self.root          
        out = open(f"BDD\\out\\{filename}.tex", "w")
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
        self.generate_latex_recursive(node, level, out, False)
        out.write("          \\end{tikzpicture} \n\
                        \\end{center} \n\
                    \\end{document}\n")
        print("File generated")


    def generate_latex_recursive(self, node, level, out, side):
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
                self.generate_latex_recursive(node.left, level + 1, out, 0)
            else:
                 out.write (indent + "\\edge[blank]; \\node[blank]{};\n \\\left")
            if node.right:
                out.write(indent)
                self.generate_latex_recursive(node.right, level + 1, out, 1)
            else:
                 out.write (indent + "\\edge[blank]; \\node[blank]{};\n \\\right")
            out.write(indent+"]\n")

    def generateDot(self, filename="output", node=None):       
        node = self.root            
        out = open(f"BDD\\out\\{filename}.dot", "w")
        out.write (f"digraph{{\nlabel=\"{self.expression}\\n\\n\"\n{id(node)}[label={node.var}]")
        self.generate_dot_recursive(node, out)
        out.write("}")
        print("Dot File generated")

    def generate_dot_recursive(self, node, out):
        if not node.drawn:
            if node.left is not None:
                child_node = node.left
                if node.left.var is not None:
                    out.write(f"{id(child_node)}[label={child_node.var}]\n")
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed]\n")
                    self.generate_dot_recursive(child_node, out)
                elif node.left.value is not None:
                    out.write(f"{id(child_node)}[label={child_node.value}]\n")
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed]\n")
            if node.right is not None:
                child_node = node.right
                if node.right.var is not None:
                    out.write(f"{id(child_node)}[label={child_node.var}]\n")
                    out.write(f"{id(node)} -> {id(child_node)}\n")
                    self.generate_dot_recursive(node.right, out)
                elif node.right.value is not None:
                    out.write(f"{id(child_node)}[label={child_node.value}]\n")
                    out.write(f"{id(node)} -> {id(child_node)}\n")
            node.drawn = True

    def reset_draw(self, node):
        if node.isLeaf():
            node.drawn = False
        if node.left is not None:
            self.reset_draw(node.left)
        if node.right is not None:
            self.reset_draw(node.right)
        node.drawn = False
       

    #def reduce(self):
        #self.removeNodesWithSameChildren()
        #self.removeDuplicateTerminalNodes()

    #def removeNodesWithSameChildren(self):

    #def removeDuplicateTerminalNodes(self):
        #positiveNode = BDDNode(value=1)
        #negativeNode = BDDNode(value=0)


# Example:
e = "(A and B) or C"
e = "((not A or B) and (not B or A)) and ((not C or D) and (not D or C))"
v = ['A', 'B', 'C', 'D']
bdd = BDD(e, v)

print("Binary Decision Diagram (BDD):")
bdd.generate_latex(node = bdd.root, filename="out")
bdd.display(bdd.root)
bdd.generateDot(node=bdd.root, filename="out")
bdd.reduce()
bdd.display(bdd.root)
bdd.generate_latex(node=bdd.root, filename="reduced_out")
bdd.reset_draw(bdd.root)
bdd.generateDot(node=bdd.root, filename="reduced_out")
