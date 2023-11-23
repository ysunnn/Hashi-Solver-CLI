from itertools import combinations
from typing import Dict, List, Tuple

import networkx as nx

from boolean import Literal, NotNode, OrNode, AndNode
from reader import Island


class Encoder:
    def _build_and(self, literals: List[Literal]) -> AndNode | Literal:
        """
        Helper function to build an and node from a list of literals
        """
        result = literals[0]
        for literal in literals[1:]:
            result = AndNode(result, literal)
        return result

    def _build_or(self, literals: List[Literal]) -> OrNode | Literal:
        """
        Helper function to build an or node from a list of literals
        """
        result = literals[0]
        for literal in literals[1:]:
            result = OrNode(result, literal)
        return result

    @staticmethod
    def _node_edges_to_literals(
        node: Island, graph: nx.MultiDiGraph, mapping: Dict[str, Tuple[Island, Island]]
    ) -> List[Literal]:
        """
        Converts in and out going edges of a node to a list of literals.
        And create a mapping, so we can translate the literals back to the edges.
        """
        bridges = []
        for edge in list(graph.in_edges(node)) + list(graph.out_edges(node)):
            bridge = "".join([str(e) for e in edge])
            bridges.append(Literal(bridge))
            if mapping.get(bridge) is None:
                mapping[bridge] = edge
        return bridges

    def _build_node(
        self,
        graph: nx.MultiDiGraph,
        node: Island,
        mapping: Dict[str, Tuple[Island, Island]],
    ) -> Literal | AndNode | OrNode | NotNode:
        """
        build ast for the bridges of the given node, with the constraint of the number of bridges
        """
        num = node.number_of_bridges
        bridges = Encoder._node_edges_to_literals(node, graph, mapping)

        # If the number of available bridges is equal to the number of bridges
        # than we add them all with and because they are all required.
        if len(bridges) == num:
            return self._build_and(bridges)
        ands = []
        # If the number of available bridges is not equal to the number of bridges, we calculate the difference,
        # so that we now how many of the bridges have to be negated.
        # Then we calculate all the combinations of the bridges that have to be negated and negate them.
        # (We calculate the combination not directly for the bridges but rather for the index, so we can easily negate them)
        # Each bridge in a combination is combined with an and.
        # And then all the combinations are combined with an or.
        # For example, B is an Island where 4 bridges are required, but there are 6 bridges available.
        #             A - B - C
        #                 |
        #                 D
        # dif = 4-6 = -2 -> 2 bridges have to be negated at the same time
        # bridges = [AB, BA, BC, CB, BD, DB]
        # combinations
        # ['-AB', '-BA', 'BC', 'CB', 'BD', 'DB']
        # ['-AB', 'BA', '-BC', 'CB', 'BD', 'DB']
        # ['-AB', 'BA', 'BC', '-CB', 'BD', 'DB']
        # ['-AB', 'BA', 'BC', 'CB', '-BD', 'DB']
        # ['-AB', 'BA', 'BC', 'CB', 'BD', '-DB']
        # ['AB', '-BA', '-BC', 'CB', 'BD', 'DB']
        # ['AB', '-BA', 'BC', '-CB', 'BD', 'DB']
        # ['AB', '-BA', 'BC', 'CB', '-BD', 'DB']
        # ['AB', '-BA', 'BC', 'CB', 'BD', '-DB']
        # ['AB', 'BA', '-BC', '-CB', 'BD', 'DB']
        # ['AB', 'BA', '-BC', 'CB', '-BD', 'DB']
        # ['AB', 'BA', '-BC', 'CB', 'BD', '-DB']
        # ['AB', 'BA', 'BC', '-CB', '-BD', 'DB']
        # ['AB', 'BA', 'BC', '-CB', 'BD', '-DB']
        # ['AB', 'BA', 'BC', 'CB', '-BD', '-DB']
        # Each value in a list is combined with an and for the first list it would look like this:
        # -AB and -BA and BC and CB and BD and DB
        # Then all the lists are combined with an or:
        # (-AB and -BA and BC and CB and BD and DB) or ... or ...
        for combination in combinations(range(len(bridges)), abs(num - len(bridges))):
            transformed = bridges.copy()
            for i in combination:
                transformed[i] = NotNode(bridges[i])
            ands.append(self._build_and(transformed))
        return self._build_or(ands)

    def encode(
        self, graph: nx.MultiDiGraph, bridges: List[Tuple[Island, Island]]
    ) -> Tuple[AndNode | Literal, Dict[str, Tuple[Island, Island]]]:
        """
        Transform the given graph into a boolean ast
        """
        mapping = {}
        nodes = [self._build_node(graph, node, mapping) for node in graph.nodes]
        expression = self._build_and(nodes)
        crossing_bridges = self._find_crossing_bridges(bridges)
        if crossing_bridges is not None:
            expression = AndNode(expression, crossing_bridges)
        reachability = self.encode_reachable(graph, mapping)
        if reachability is not None:
            expression = AndNode(expression, reachability)
        return expression, mapping

    def encode_reachable(
        self, graph: nx.MultiDiGraph, bridge_vars: Dict[str, Tuple[Island, Island]]
    ):
        """
        encode the reachability of islands
        """
        bridge_vars = {value: key for key, value in bridge_vars.items()}
        # print(bridge_vars)
        reachability_vars = {
            (a, b): f"r_{a.name}{b.name}" for a, b in combinations(graph.nodes, 2)
        }
        reachability_vars.update(
            {(b, a): value for (a, b), value in reachability_vars.items()}
        )

        # print(reachability_vars)
        # exit()

        sat_clauses = None

        # Direct reachability clauses
        for (a, b), var in bridge_vars.items():
            # print(var)
            # print(a, b)
            if sat_clauses is None:
                sat_clauses = OrNode(
                    NotNode(Literal(var)), Literal(reachability_vars[a, b])
                )
            else:
                sat_clauses = AndNode(
                    sat_clauses,
                    OrNode(NotNode(Literal(var)), Literal(reachability_vars[a, b])),
                )

        for a, b, c in combinations(graph.nodes, 3):
            if (
                (a, b) in reachability_vars
                and (b, c) in reachability_vars
                and (a, c) in reachability_vars
            ):
                c = OrNode(
                    NotNode(Literal(reachability_vars[a, c])),
                    OrNode(
                        NotNode(Literal(reachability_vars[c, b])),
                        Literal(reachability_vars[a, b]),
                    ),
                )
                if sat_clauses is None:
                    sat_clauses = c
                else:
                    sat_clauses = AndNode(sat_clauses, c)

        # Transitive reachability clauses
        # Only consider pairs connected by a potential bridge for transitive reachability
        # for a, b in reachability_vars:
        #    for c in graph.nodes:
        #        if c != a and c != b and ((a, c) in bridge_vars or (c, a) in bridge_vars) and (
        #                (b, c) in bridge_vars or (c, b) in bridge_vars):
        #            #sat_clauses.append(f'(~{reachability_vars[a, c]} or ~{reachability_vars[c, b]} or {reachability_vars[a, b]})')
        #            c = OrNode(NotNode(Literal(reachability_vars[a, c])),OrNode(NotNode(Literal(reachability_vars[c, b])), Literal(reachability_vars[a, b])))
        #            if sat_clauses is None:
        #                sat_clauses = c
        #            else:
        #                sat_clauses = AndNode(sat_clauses, c)

        # Global connectivity constraint
        for a, b in combinations(graph.nodes, 2):
            # sat_clauses.append(f'{reachability_vars[a, b]}')
            c = Literal(reachability_vars[a, b])
            if sat_clauses is None:
                sat_clauses = c
            else:
                sat_clauses = AndNode(sat_clauses, c)

        return sat_clauses

    @staticmethod
    def _do_intersect(p1: Island, q1: Island, p2: Island, q2: Island) -> bool:
        """
        find a pair of parallel islands, and find another pair of parallel islands that pass between them.
        """
        if p1.y == q1.y and p2.x == q2.x:
            if p1.x < p2.x < q1.x and p2.y < p1.y < q2.y:
                return True
            if q1.x < p2.x < p1.x and q2.y < p1.y < p2.y:
                return True
        return False

    def encode_crossing_bridges(self, crossing_bridges: List[str]) -> AndNode | None:
        """
        build ast for each crossing bridges. CNF of "A -> ~B" is "¬A ∨ ¬B"
        """
        if len(crossing_bridges) == 0:
            return None
        nodes = [
            AndNode(
                OrNode(
                    NotNode(Literal(crossing_bridges[0])),
                    NotNode(Literal(crossing_bridges[1])),
                ),
                OrNode(
                    NotNode(Literal(crossing_bridges[0])),
                    NotNode(Literal(crossing_bridges[2])),
                ),
            )
        ]
        if len(nodes) > 0:
            return self._build_and(nodes)

    def _find_crossing_bridges(
        self, bridges: List[Tuple[Island, Island]]
    ) -> AndNode | None:
        """
        find possible intersecting bridges through the intersecting islands and add ast
        """
        final_ast = None
        for i in range(len(bridges)):
            for j in range(len(bridges)):
                if Encoder._do_intersect(
                    bridges[i][0], bridges[i][1], bridges[j][0], bridges[j][1]
                ):
                    b1 = [island.name for island in bridges[i]]
                    b2 = [island.name for island in bridges[j]]
                    b3 = [island.name for island in bridges[j][::-1]]
                    ast = self.encode_crossing_bridges(
                        ["".join(b1), "".join(b2), "".join(b3)]
                    )
                    if ast is None:
                        continue
                    if final_ast is None:
                        final_ast = ast
                    else:
                        final_ast = AndNode(final_ast, ast)
        return final_ast
