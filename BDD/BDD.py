from collections import deque


class BDDNode:
    def __init__(self, var=None, left=None, right=None, parent=None, value=None, assignment=[]):
        self.var = var  # The variable for decision (None for terminal nodes)
        self.left = left
        self.right = right
        self.parent = parent
        self.value = value  # Terminal value (True or False for leaf nodes)
        self.assignment = assignment
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
        self.evaluation = {}  #dict of all evaluations
        self.leafs = {False: BDDNode(value=False), True: BDDNode(value=True)}
        self.root = self.build(0)  # Build the BDD starting from the first variable index

    def build(self, var_index, current_assignment={}):
        # end of recursion if node is a leaf
        if var_index == len(self.variables):
            assignment = {var: val for var, val in current_assignment.items()}  # copies current_assignment
            value = evaluate_expression(self.expression, assignment)
            self.evaluation[tuple(assignment.items())] = value
            leaf = BDDNode(value=value)
            leaf.assignment.append(assignment)
            return leaf

        #initiate node
        var = self.variables[var_index]
        currentNode = BDDNode(var=var)
        currentNode.assignment.append({var: val for var, val in current_assignment.items()})
        # Create node for false subtree and true subtree
        current_assignment_left = current_assignment.copy()
        current_assignment_left[var] = False
        leftNode = self.build(var_index + 1, current_assignment_left)
        currentNode.left = leftNode

        current_assignment_right = current_assignment.copy()
        current_assignment_right[var] = True
        rightNode = self.build(var_index + 1, current_assignment_right)
        currentNode.right = rightNode
        return currentNode

    # # traverses down the diagram to evaluate it
    # def evaluate(self, node, variables):
    #     if node.isLeaf():
    #         return node.value
    #     if variables[node.var] is False:
    #         return self.evaluate(node.left, variables)
    #     else:
    #         return self.evaluate(node.right, variables)

    def reduce(self):
        self.remove_duplicate_subtree(self.root, mem={})
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
            return node.left
        return None

    def generateDot(self, filename="output", node=None):
        node = self.root
        #out = open(f"C:\\Users\\annan\\PycharmProjects\\SaferThanPerception\\BDD\\out\\{filename}.dot", "w")
        out = open(f"BDD\\out\\{filename}.dot", "w")
        out.write(f"digraph{{\nlabel=\"{self.expression}\\n\\n\"\n{id(node)}[label={node.var}]")
        self.generate_dot_recursive(node, out)
        out.write("}")
        print("Dot File generated")
        self.reset_draw(self.root)

    def generate_dot_recursive(self, node, out):
        if not node.drawn:
            # draw left childnode
            if node.left is not None:
                child_node = node.left
                if node.left.var is not None:
                    out.write(f"{id(child_node)}[label=\"{child_node.var} {str(child_node.assignment)}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed]\n")
                    self.generate_dot_recursive(child_node, out)
                elif node.left.value is not None:
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\n{str(child_node.assignment)}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}[style=dashed]\n")
            #draw right childnode
            if node.right is not None:
                child_node = node.right
                if node.right.var is not None:
                    out.write(f"{id(child_node)}[label=\"{child_node.var} {str(child_node.assignment)}\"]\n")
                    out.write(f"{id(node)} -> {id(child_node)}\n")
                    self.generate_dot_recursive(node.right, out)
                elif node.right.value is not None:
                    out.write(f"{id(child_node)}[label=\"{child_node.value}\n{str(child_node.assignment)}\"]\n")
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


def breadth_first_bottom_up(self):
    out = []
    queue = deque([self.root])
    visited = set()

    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        out.append(node)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return out.reverse()


#Example:
e = "(A and B) or C"
e = "((not A or B) and (not B or A)) and ((not C or D) and (not D or C))"
v = ['A', 'B', 'C', 'D']
bdd = BDD(e, v)

print("Binary Decision Diagram (BDD):")
bdd.generateDot(node=bdd.root, filename="out")
bdd.reduce()
bdd.generateDot(node=bdd.root, filename="reduced_out")
for k, v in bdd.evaluation.items():
    print(f"{k}: {v}")
