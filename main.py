import networkx as nx
import matplotlib.pyplot as plt


class Island:
    def __init__(self, x, y, number_of_bridges):
        self.x = x
        self.y = y
        self.number_of_bridges = number_of_bridges

    def __repr__(self):
        return f"Island(x: {self.x, self.y, self.number_of_bridges}"


puzzle_str = """7
1.3..2.
.......
4.5...2
.......
..6..2.
2......
..2.1.2
"""

islands = []
bridges = []


# Convert puzzle text to array with Island
def find_islands(puzzle_lines):
    for r, col in enumerate(puzzle_lines):
        my_col = []
        for c, ele in enumerate(col):
            if ele == '.':
                my_col.append(None)
            else:
                number_of_bridges = int(ele)
                my_col.append(Island(r, c, number_of_bridges))
        islands.append(my_col)


# Find all possible bridges
def find_bridge(target_island):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for direction in directions:
        searching_row, searching_col = target_island.x + direction[0], target_island.y + direction[1]
        while 0 <= searching_row < puzzle_size and 0 <= searching_col < puzzle_size:
            if islands[searching_row][searching_col] is not None:
                bridges.append((target_island, islands[searching_row][searching_col]))
                break
            else:
                searching_row += direction[0]
                searching_col += direction[1]


lines = puzzle_str.splitlines()
puzzle_size = int(lines.pop(0))
find_islands(lines)
for rows in islands:
    for island in rows:
        if island is not None:
            find_bridge(island)

# Draw the graph
G = nx.MultiDiGraph()
for rows in islands:
    for island in rows:
        if island is not None:
            G.add_node(island, pos=(island.y, -island.x), label=island.number_of_bridges)
G.add_edges_from(bridges)
pos = nx.get_node_attributes(G, 'pos')
labels = nx.get_node_attributes(G, 'label')
nx.draw(G, pos=pos, with_labels=True, labels=labels)
plt.show()
