from boolean import AndNode, Literal, NotNode, OrNode


class CNF:
    counter: int
    clauses: AndNode | None

    def __init__(self):
        self.counter = 0
        self.clauses = None

    def new_aux(self):
        self.counter += 1
        return Literal(f"P_{self.counter}")

    def add_and_clause(self, clause):
        if self.clauses is None:
            # If there are no clauses yet, the new clause becomes the root
            self.clauses = clause
        else:
            # Otherwise, append the new clause to the tree
            new_node = AndNode(self.clauses, clause)
            self.clauses = new_node


def transform(
    node: Literal | AndNode | OrNode | NotNode, recursive: bool = False
) -> AndNode | None:
    """
    Transforms a boolean expression into CNF using Tseytin transformation
    """
    cnf = CNF()

    def _tseytin_transform_recursive(
        node_: Literal | AndNode | OrNode | NotNode, cnf_: CNF
    ) -> Literal:
        """
        Basic Tseytin transformation, credit to https://profs.info.uaic.ro/~stefan.ciobaca/logic-2018-2019/notes7.pdf
        """
        if isinstance(node_, Literal):
            return node_

        if isinstance(node_, NotNode):
            aux_lit = cnf_.new_aux()
            child_lit = _tseytin_transform_recursive(node_.operand, cnf_)
            cnf_.add_and_clause(
                AndNode(
                    OrNode(aux_lit, child_lit),
                    OrNode(NotNode(aux_lit), NotNode(child_lit)),
                )
            )
            return aux_lit

        if isinstance(node_, AndNode) or isinstance(node_, OrNode):
            aux_lit = cnf_.new_aux()
            left_lit = _tseytin_transform_recursive(node_.left, cnf_)
            right_lit = _tseytin_transform_recursive(node_.right, cnf_)
            if isinstance(node_, AndNode):
                cnf_.add_and_clause(
                    AndNode(
                        AndNode(
                            OrNode(NotNode(aux_lit), left_lit),
                            OrNode(NotNode(aux_lit), right_lit),
                        ),
                        OrNode(aux_lit, OrNode(NotNode(left_lit), NotNode(right_lit))),
                    )
                )
            elif isinstance(node_, OrNode):
                cnf_.add_and_clause(
                    AndNode(
                        AndNode(
                            OrNode(aux_lit, NotNode(left_lit)),
                            OrNode(aux_lit, NotNode(right_lit)),
                        ),
                        OrNode(NotNode(aux_lit), OrNode(left_lit, right_lit)),
                    )
                )
            return aux_lit

    def _tseytin_transform_iterative(
        root: Literal | AndNode | OrNode | NotNode, cnf: CNF
    ) -> Literal:
        stack = [(root, False)]
        result = []

        while stack:
            node, visited = stack.pop()

            if visited:
                if isinstance(node, Literal):
                    result.append(node)
                elif isinstance(node, NotNode):
                    aux_lit = cnf.new_aux()
                    child_lit = result.pop()
                    cnf.add_and_clause(
                        AndNode(
                            OrNode(aux_lit, child_lit),
                            OrNode(NotNode(aux_lit), NotNode(child_lit)),
                        )
                    )
                    result.append(aux_lit)
                elif isinstance(node, AndNode) or isinstance(node, OrNode):
                    aux_lit = cnf.new_aux()
                    right_lit = result.pop()
                    left_lit = result.pop()
                    if isinstance(node, AndNode):
                        cnf.add_and_clause(
                            AndNode(
                                AndNode(
                                    OrNode(NotNode(aux_lit), left_lit),
                                    OrNode(NotNode(aux_lit), right_lit),
                                ),
                                OrNode(
                                    aux_lit,
                                    OrNode(NotNode(left_lit), NotNode(right_lit)),
                                ),
                            )
                        )
                    elif isinstance(node, OrNode):
                        cnf.add_and_clause(
                            AndNode(
                                AndNode(
                                    OrNode(aux_lit, NotNode(left_lit)),
                                    OrNode(aux_lit, NotNode(right_lit)),
                                ),
                                OrNode(NotNode(aux_lit), OrNode(left_lit, right_lit)),
                            )
                        )
                    result.append(aux_lit)
            else:
                if isinstance(node, Literal):
                    stack.append((node, True))
                elif isinstance(node, NotNode):
                    stack.append((node, True))
                    stack.append((node.operand, False))
                elif isinstance(node, AndNode) or isinstance(node, OrNode):
                    stack.append((node, True))
                    stack.append((node.right, False))
                    stack.append((node.left, False))

        return result.pop()

    if recursive:
        root = _tseytin_transform_recursive(node, cnf)
    else:
        root = _tseytin_transform_iterative(node, cnf)
    cnf.add_and_clause(root)
    return cnf.clauses
