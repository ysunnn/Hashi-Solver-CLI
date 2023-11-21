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
