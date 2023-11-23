# Gruppe L

# Hashi Solver CLI

This is a command-line interface (CLI) for solving Hashi.
The CLI takes a Hashi-puzzle file as input and solves the puzzle using a SAT solver.
The solution can be visualized as a graph, and the Conjunctive Normal Form (CNF) of the puzzle can be written to a file.

## Installation



This project requires Python and pip. You can install the required packages using the following command:

```bash
pip install -r requirements.txt
```

### Warning
We use [pysat](https://pysathq.github.io/installation/) to solve the CNF. Which is only easy to install on Linux.

## Usage

You can run the CLI using the following command:

```bash
python main.py [puzzle_file] [--plot] [--cnf_to_file] [--cnf_path CNF_PATH]
```

### Arguments

- `puzzle_file`: Path to the puzzle file. This is an optional argument. If not provided, the `test` function will be run.
- `--plot`: If this flag is set, the graph of the solution will be plotted.
- `--cnf_to_file`: If this flag is set, the CNF of the puzzle will be written to a file.
- `--cnf_path CNF_PATH`: Path to the CNF file. This argument is required if `--cnf_to_file` is set.

### Examples

To solve a puzzle and plot the graph of the solution:

```bash
python main.py puzzle.txt --plot
```

To solve a puzzle and write the CNF to a file:

```bash
python main.py puzzle.txt --cnf_to_file --cnf_path cnf.txt
```

To run the `test` function:

Now each puzzle in the `data` directory will be solved, and the graph of each solution will be plotted.
Every time a plot is shown, you have to close it to continue to the next puzzle.
Also, a DIMACS CNF file will be written for each puzzle in the `data` directory,
it hase the same name as the puzzle file but with a `.cnf` extension instead of `.txt`.

```bash
python main.py
```

## Notes 

- if the cnf_to_file flag is true, the cnf is written to a file no matter if it is satisfiable or not.
- if someone wants to test multiple puzzles at once, the test function can be used. drop the puzzles in the data folder and run the test function.
  - optional manual deactivation of the plot flag in the test function to avoid the manual closing of the plots.