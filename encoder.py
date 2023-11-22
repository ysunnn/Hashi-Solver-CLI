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
        crossing_bridges = self.encode_crossing_bridges(bridges)
        if crossing_bridges is not None:
            expression = AndNode(expression, crossing_bridges)
        return expression, mapping

    @staticmethod
    def _do_intersect(p1: Island, q1: Island, p2: Island, q2: Island) -> bool:
        if p1.y == q1.y and p2.x == q2.x:
            if p1.x < p2.x < q1.x and p2.y < p1.y < q2.y:
                return True
            if q1.x < p2.x < p1.x and q2.y < p1.y < p2.y:
                return True
        return False

    @staticmethod
    def _find_crossing_bridges(bridges: List[Tuple[Island, Island]]) -> List[str]:
        crossing_bridges = []
        for i in range(len(bridges)):
            for j in range(len(bridges)):
                if Encoder._do_intersect(
                    bridges[i][0], bridges[i][1], bridges[j][0], bridges[j][1]
                ):
                    b1 = [island.name for island in bridges[i]]
                    b2 = [island.name for island in bridges[j]]
                    crossing_bridges.append("".join(b1))
                    crossing_bridges.append("".join(b2))
        return crossing_bridges

    def encode_crossing_bridges(
        self, bridges: List[Tuple[Island, Island]]
    ) -> AndNode | None:
        crossing_bridges = Encoder._find_crossing_bridges(bridges)
        if len(crossing_bridges) == 0:
            return None
        nodes = []
        seen = {}
        for i in range(len(crossing_bridges)):
            for j in range(i + 1, len(crossing_bridges)):
                if len(set(crossing_bridges[i]) & set(crossing_bridges[j])) == 0:
                    pair = frozenset([crossing_bridges[i], crossing_bridges[j]])
                    if pair not in seen:
                        nodes.append(
                            AndNode(
                                OrNode(
                                    Literal(crossing_bridges[i]),
                                    Literal(crossing_bridges[j]),
                                ),
                                OrNode(
                                    NotNode(Literal(crossing_bridges[i])),
                                    NotNode(Literal(crossing_bridges[j])),
                                ),
                            )
                        )
                        seen[pair] = True
        return self._build_and(nodes)
