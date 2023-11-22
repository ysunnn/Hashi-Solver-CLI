from itertools import combinations
from typing import Dict, List

import networkx as nx

from boolean import Literal, NotNode, OrNode, AndNode, Node
from reader import Island


def build_and(bridges: List[Node], mapping: Dict) -> Node | AndNode:
    if type(bridges[0]) == Literal and mapping.get(bridges[0]) is None:
        mapping[bridges[0]] = mapping.get("counter") + 1
        mapping["counter"] += 1
    if len(bridges) == 1:
        return bridges[0]
    return AndNode(bridges[0], build_and(bridges[1:], mapping))


def build_or(bridges: List[Literal], mapping: Dict) -> OrNode | Literal:
    if type(bridges[0]) == Literal and mapping.get(bridges[0]) is None:
        mapping[bridges[0]] = mapping.get("counter") + 1
        mapping["counter"] += 1
    if len(bridges) == 1:
        return bridges[0]
    return OrNode(bridges[0], build_or(bridges[1:], mapping))


def build_node(
        graph: nx.MultiDiGraph, node: Island, mapping: Dict
) -> Literal | AndNode | OrNode | NotNode:
    num = node.number_of_bridges
    bridges = [
        Literal("".join([str(e) for e in edge]))
        for edge in list(graph.in_edges(node)) + list(graph.out_edges(node))
    ]
    if len(bridges) == num:
        return build_and(bridges, mapping)
    ands = []
    for combination in combinations(range(len(bridges)), abs(num - len(bridges))):
        transformed = bridges.copy()
        for i in combination:
            transformed[i] = NotNode(bridges[i])
        ands.append(build_and(transformed, mapping))
    return build_or(ands, mapping)


def encode(graph: nx.MultiDiGraph, bridges):
    mapping = {"counter": 0}
    nodes = [build_node(graph, node, mapping) for node in graph.nodes]
    expression = build_and(nodes, mapping)
    expression = AndNode(expression, encode_crossing_bridges(bridges))
    return expression, mapping


# rule - Bridges are not allowed to cross other bridges.

# Check if two island pairs intersect
def do_intersect(p1, q1, p2, q2):
    if p1.y == q1.y and p2.x == q2.x:
        if p1.x < p2.x < q1.x and p2.y < p1.y < q2.y:
            return True
        if q1.x < p2.x < p1.x and q2.y < p1.y < p2.y:
            return True
    return False


def find_crossing_bridges(bridges):
    crossing_bridges = []
    for i in range(len(bridges)):
        for j in range(len(bridges)):
            if do_intersect(bridges[i][0], bridges[i][1], bridges[j][0], bridges[j][1]):
                b1 = [island.name for island in bridges[i]]
                b2 = [island.name for island in bridges[j]]
                crossing_bridges.append("".join(b1))
                crossing_bridges.append("".join(b2))
    return crossing_bridges


def encode_crossing_bridges(bridges):
    crossing_bridges = find_crossing_bridges(bridges)
    nodes = []
    seen = {}
    for i in range(len(crossing_bridges)):
        for j in range(i+1, len(crossing_bridges)):
            if len(set(crossing_bridges[i]) & set(crossing_bridges[j])) == 0:
                pair = frozenset([crossing_bridges[i], crossing_bridges[j]])
                if pair not in seen:
                    nodes.append(AndNode(OrNode(Literal(crossing_bridges[i]), Literal(crossing_bridges[j])),
                                         OrNode(NotNode(Literal(crossing_bridges[i])),
                                                NotNode(Literal(crossing_bridges[j])))))
                    seen[pair] = True
    return build_and(nodes, {})
