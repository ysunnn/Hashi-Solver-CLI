import os
from typing import List
import argparse
from pathlib import Path

import networkx as nx
from matplotlib import pyplot as plt
from pysat.solvers import MinisatGH
from pysat.formula import CNF

from boolean import to_solver_string_iterative
from encoder import Encoder
from reader import read_puzzle_from_string, to_graph
import tseytin


def plot_graph(graph: nx.Graph):
    pos = nx.get_node_attributes(graph, "pos")
    labels = nx.get_node_attributes(graph, "label")
    nx.draw(graph, pos=pos, with_labels=True, labels=labels)
    plt.show()


def map_back(result: List[int], solver_mapping, islands_mapping, graph):
    for variable in result:
        if variable > 0:
            # If the variable is positive, we keep the bridge because it is part of the solution
            continue
        variable = abs(variable)
        bridge = solver_mapping.get(str(variable))
        if bridge[0].isalpha():
            # If the bridge is not a number, it is an auxiliary variable and we can ignore it
            continue
        # remove bridge from graph because it is not part of the solution
        x, y = islands_mapping.get(bridge)
        graph.remove_edge(x, y)


def solve(
    puzzle: str, plot: bool = False, cnf_to_file: bool = False, cnf_path: Path = None
):
    # transform to islands and bridges
    islands, bridges = read_puzzle_from_string(puzzle)
    # make a graph from the islands and bridges
    graph = to_graph(islands, bridges)
    # encode the graph to a boolean expression
    expression, islands_mapping = Encoder().encode(graph, bridges)
    # transform the expression to cnf
    expression = tseytin.transform(expression)
    # transform the cnf to a string that can be used by a SAT solver
    flat, mapping = to_solver_string_iterative(expression)

    if cnf_to_file:
        with open(cnf_path, "w") as file:
            file.write(flat)
    # solve the cnf with a SAT solver
    solver = MinisatGH()
    cnf = CNF(from_string=flat)
    solver.append_formula(cnf)
    if not solver.solve():
        print("No solution found")
        return
    # map the result back to the graph
    map_back(solver.get_model(), mapping, islands_mapping, graph)
    if plot:
        plot_graph(graph)


def test():
    for file in os.listdir("data"):
        if not file.endswith(".txt"):
            continue
        print(file)
        with open(os.path.join("data", file)) as f:
            puzzle_str = f.read()
            solve(
                puzzle_str,
                plot=True,
                cnf_to_file=True,
                cnf_path=Path(f"data/{file.replace('.txt', '.cnf')}"),
            )


def main():
    parser = argparse.ArgumentParser(description="Solve a puzzle.")
    parser.add_argument(
        "puzzle_file", type=str, nargs="?", help="Path to the puzzle file."
    )
    parser.add_argument("--plot", action="store_true", help="Plot the graph.")
    parser.add_argument(
        "--cnf_to_file", action="store_true", help="Write the CNF to a file."
    )
    parser.add_argument("--cnf_path", type=str, help="Path to the CNF file.")
    args = parser.parse_args()

    if args.puzzle_file is None:
        test()
    else:
        puzzle_file = Path(args.puzzle_file)
        with open(puzzle_file, "r") as f:
            puzzle_str = f.read()
        solve(
            puzzle_str,
            plot=args.plot,
            cnf_to_file=args.cnf_to_file,
            cnf_path=Path(args.cnf_path)
            if args.cnf_path
            else puzzle_file.with_suffix(".cnf"),
        )


if __name__ == "__main__":
    main()
