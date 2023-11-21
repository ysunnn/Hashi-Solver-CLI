from itertools import combinations
from typing import Dict, List

import networkx as nx

from boolean import Literal, NotNode, OrNode, AndNode
from reader import Island


def build_and(bridges: List[Literal], mapping: Dict) -> AndNode | Literal:
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


def encode(graph: nx.MultiDiGraph):
    mapping = {"counter": 0}
    nodes = [build_node(graph, node, mapping) for node in graph.nodes]
    return build_and(nodes, mapping), mapping
