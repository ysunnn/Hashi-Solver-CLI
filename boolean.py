from typing import Dict, Tuple


class Node:
    pass


class AndNode(Node):
    left: Node
    right: Node

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left!r} & {self.right!r})"


class OrNode(Node):
    left: Node
    right: Node

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left!r} | {self.right!r})"


class NotNode(Node):
    operand: Node

    def __init__(self, operand: Node):
        self.operand = operand

    def __repr__(self):
        return f"~{self.operand!r}"


class Literal(Node):
    name: str

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Literal) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


def to_solver_string_recursive(root):
    # Maps literals to integers
    literal_map = {}
    next_literal_id = 1

    def dfs(node):
        nonlocal next_literal_id
        if isinstance(node, AndNode):
            return dfs(node.left) + " 0\n" + dfs(node.right)
        elif isinstance(node, OrNode):
            return dfs(node.left) + " " + dfs(node.right)
        elif isinstance(node, NotNode):
            return "-" + dfs(node.operand)
        elif isinstance(node, Literal):
            if node.name not in literal_map:
                literal_map[node.name] = str(next_literal_id)
                next_literal_id += 1
            return literal_map[node.name]
        else:
            raise ValueError("Unknown node type")

    return dfs(root) + " 0", {v: k for k, v in literal_map.items()}


def to_solver_string_iterative(
    root: Literal | AndNode | OrNode | NotNode,
) -> Tuple[str, Dict[str, str]]:
    """
    Transforms a boolean expression in cnf to a string that can be used by a SAT solver.
    We need to use an iterative approach because the recursive approach would exceed the recursion limit.
    """
    # Mapping to revers the process after the SAT solver has found a solution
    literal_map = {}
    next_literal_id = 1

    # One stack for the Ast and one for the results
    stack = [(root, False)]
    result = []
    and_counter = 0
    while stack:
        node, visited = stack.pop()

        if visited:
            # popping the node stack and build up the result stack
            if isinstance(node, Literal):
                if node.name not in literal_map:
                    literal_map[node.name] = str(next_literal_id)
                    next_literal_id += 1
                result.append(literal_map[node.name])
            elif isinstance(node, NotNode):
                result.append(f"-{result.pop()}")
            elif isinstance(node, AndNode):
                and_counter += 1
                right = result.pop()
                left = result.pop()
                result.append(f"{left} 0\n{right}")
            elif isinstance(node, OrNode):
                right = result.pop()
                left = result.pop()
                result.append(f"{left} {right}")
            else:
                # if for some reason we encounter an unknown node type, we raise an error
                # but this should never happen
                raise ValueError(f"Unknown node type, {node}")
        else:
            # Build up the stack of all nodes
            if isinstance(node, Literal):
                stack.append((node, True))
            elif isinstance(node, NotNode):
                stack.append((node, True))
                stack.append((node.operand, False))
            elif isinstance(node, AndNode) or isinstance(node, OrNode):
                stack.append((node, True))
                stack.append((node.right, False))
                stack.append((node.left, False))
            else:
                # if for some reason we encounter an unknown node type, we raise an error
                # but this should never happen
                raise ValueError(f"Unknown node type, {node}")

    return f"p cnf {next_literal_id - 1} {and_counter}\n" + result[0] + " 0", {
        v: k for k, v in literal_map.items()
    }
