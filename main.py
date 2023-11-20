from reader import read_puzzle_from_string, plot_puzzle

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
