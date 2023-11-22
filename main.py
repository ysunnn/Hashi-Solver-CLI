from encoder import encode
from reader import read_puzzle_from_string, plot_puzzle, to_graph

puzzle_str = """7
1.3..2.
.......
4.5...2
.......
..6..2.
2......
..2.1.2"""
islands, bridges = read_puzzle_from_string(puzzle_str)
plot_puzzle(islands, bridges)
graph = to_graph(islands, bridges)

expression, mapping = encode(graph=graph, bridges=bridges)
