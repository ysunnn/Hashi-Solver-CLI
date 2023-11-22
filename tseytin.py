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


def transform(node: Literal | AndNode | OrNode | NotNode) -> AndNode | None:
    """
    Transforms a boolean expression into CNF using Tseytin transformation
    """
    cnf = CNF()

    def _tseytin_transform(
        node_: Literal | AndNode | OrNode | NotNode, cnf_: CNF
    ) -> Literal:
        """
        Basic Tseytin transformation, credit to https://profs.info.uaic.ro/~stefan.ciobaca/logic-2018-2019/notes7.pdf
        """
        if isinstance(node_, Literal):
            return node_

        if isinstance(node_, NotNode):
            aux_lit = cnf_.new_aux()
            child_lit = _tseytin_transform(node_.operand, cnf_)
            cnf_.add_and_clause(
                AndNode(
                    OrNode(aux_lit, child_lit),
                    OrNode(NotNode(aux_lit), NotNode(child_lit)),
                )
            )
            return aux_lit

        if isinstance(node_, AndNode) or isinstance(node_, OrNode):
            aux_lit = cnf_.new_aux()
            left_lit = _tseytin_transform(node_.left, cnf_)
            right_lit = _tseytin_transform(node_.right, cnf_)
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

    root = _tseytin_transform(node, cnf)

    cnf.add_and_clause(root)
    return cnf.clauses
