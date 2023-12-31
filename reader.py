from typing import Tuple, List

import networkx as nx
import matplotlib.pyplot as plt


class Island:
    def __init__(self, x, y, number_of_bridges, name):
        self.x = x
        self.y = y
        self.number_of_bridges = number_of_bridges
        self.name = name

    def __repr__(self):
        return f"Island(x: {self.x, self.y, self.number_of_bridges}"

    def __str__(self):
        return self.name


# Convert puzzle text to array with Island
def _find_islands(puzzle_lines):
    islands = []
    counter = 0
    for r, col in enumerate(puzzle_lines):
        my_col = []
        for c, ele in enumerate(col.strip()):
            if ele == ".":
                my_col.append(None)
            else:
                counter += 1
                number_of_bridges = int(ele)
                my_col.append(Island(r, c, number_of_bridges, str(counter)))
        islands.append(my_col)
    return islands


# Find all possible bridges
def _find_bridge(target_island, islands, puzzle_size):
    bridges = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for direction in directions:
        searching_row, searching_col = (
            target_island.x + direction[0],
            target_island.y + direction[1],
        )
        while (
            0 <= searching_row < puzzle_size[0] and 0 <= searching_col < puzzle_size[1]
        ):
            if islands[searching_row][searching_col] is not None:
                bridges.append((target_island, islands[searching_row][searching_col]))
                break
            else:
                searching_row += direction[0]
                searching_col += direction[1]
    return bridges


def read_puzzle_from_string(
    puzzle_str: str,
) -> Tuple[List[List[Island]], List[Tuple[Island, Island]]]:
    lines = puzzle_str.splitlines()
    puzzle_size = tuple(map(int, lines.pop(0).split()))
    islands = _find_islands(lines)
    bridges = []
    for rows in islands:
        for island in rows:
            if island is not None:
                bridges.extend(_find_bridge(island, islands, puzzle_size))
    return islands, bridges


def to_graph(
    islands: List[List[Island]], bridges: List[Tuple[Island, Island]]
) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    for rows in islands:
        for island in rows:
            if island is not None:
                g.add_node(
                    island, pos=(island.y, -island.x), label=island.number_of_bridges
                )
    g.add_edges_from(bridges)
    return g


# Draw the puzzle as graph
def plot_puzzle(islands: List[List[Island]], bridges: List[Tuple[Island, Island]]):
    g = nx.MultiDiGraph()
    for rows in islands:
        for island in rows:
            if island is not None:
                g.add_node(
                    island, pos=(island.y, -island.x), label=island.number_of_bridges
                )
    g.add_edges_from(bridges)
    pos = nx.get_node_attributes(g, "pos")
    labels = nx.get_node_attributes(g, "label")
    nx.draw(g, pos=pos, with_labels=True, labels=labels)
    plt.show()
