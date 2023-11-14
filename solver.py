# This is a sudoku solver that makes use of the dancing links algorithm.
# Eli Bell
# 2023-10-23


class Node:
    def __init__(self):
        self.up = self
        self.down = self
        self.right = self
        self.left = self


class Origin(Node):
    def __init__(self):
        super().__init__()
    


class Header(Node):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set = set({(k, v) for k, v in data.items() if v is not None})
    
    def __str__(self):
        return "{{{}}}".format(", ".join([f"{k}: {v}" for k, v in self.data.items()]))

class Constraint(Header):
    index = 0
    def __init__(self, group, data):
        super().__init__(data)
        self.group = group
        self.index = Constraint.index
        Constraint.index += 1

    def __str__(self):
        data = super().__str__()
        return "{} ({}) = {}".format("Constraint", self.group, data) 

class Option(Header):
    index = 0
    def __init__(self, data):
        super().__init__(data)
        self.index = Option.index
        Option.index += 1

    def __str__(self):
        return "r{}c{}={}".format(*[self.data.get(v) for v in ["row", "col", "num"]])


class Table:
    def __init__(self):
        self.origin = Origin()
        self.origin.up = self.origin
        self.origin.right = self.origin
        self.origin.down = self.origin
        self.origin.left = self.origin
        self.options = {}
        self.givens = []

    def __str__(self):
        elements = ["row", "col", "box", "num"]
        lhs_width = 7
        intro = ("This is an exact cover matrix for the game Sudoku. The rows\n"
                "represent every possible candidate placement, while the columns \n"
                "represent the constraints derived from the rules of Sudoku.\n"
                "There are 9x9x9=729 possible candidates and 9x9x4=324 constraints.\n"
                "The occupied cells indicate where the candidates and constraints\n"
                "intersect, the numbers displayed are simply the corresponding\n"
                "candidate numbers for ease of reading.\n")
        header = ["{:{}}".format(f"{lhs:5s}:", lhs_width) for lhs in ["GROUP"] + elements]
        sep_index = [lhs_width]
        constraint = self.origin.right
        while constraint is not self.origin:
            if constraint.left == self.origin or constraint.left.group != constraint.group:
                header = [v + "|" for v in header]
                header[0] += constraint.group.upper()
            for i, v in enumerate(elements, start=1):
                val = constraint.data.get(v)
                header[i] += " " if val is None else str(val)
            if constraint.right == self.origin or constraint.right.group != constraint.group:
                sep_index.append(len(header[1]))
                header[0] += " " * (len(header[1]) - len(header[0]))
            constraint = constraint.right

        sep_line = "".join(["+" if i in sep_index else "-" for i in range(sep_index[-1])])
        table = []
        option = self.origin.down
        while option is not self.origin:
            num = option.data.get("num")
            if num == 1:
                table.append(f"{sep_line}")
            lhs = f"{str(option):{lhs_width}s}"
            table.append(lhs)
            constraint = self.origin.right
            while constraint is not self.origin:
                if len(table[-1]) in sep_index:
                    table[-1] += "|"
                table[-1] += str(num) if constraint.set.issubset(option.set) else " "
                constraint = constraint.right
            option = option.down
        return "\n".join([v for v in [intro] + header + table])

    def add_constraint(self, group, data):
        constraint = Constraint(group, data)
        self.origin.left.right = constraint
        constraint.left = self.origin.left
        constraint.right = self.origin
        self.origin.left = constraint

    def add_option(self, data):
        # This function depends on all constraints being added first!
        option = Option(data)
        self.origin.up.down = option
        option.up = self.origin.up
        option.down = self.origin
        self.origin.up = option
        constraint = self.origin.right
        while constraint is not self.origin:
            if constraint.set.issubset(option.set):
                self.add_cell(constraint, option)
            constraint = constraint.right
        # box unnecessary for look-up
        self.options[tuple([data.get(v) for v in ["row", "col", "num"]])] = option

    def remove_constraint(self, constraint):
        current = constraint
        while current.right is not constraint:
            current.up.down = current.down
            current.down.up = current.up
            current = current.right

    def remove_option(self, option):
        current = option
        while current.down is not option:
            current.right.left = current.left
            current.left.right = current.right
            current = current.down

    def restore_constraint(self, constraint):
        current = constraint
        while current.right is not constraint:
            current.up.down = current
            current.down.up = current
            current = current.right

    def restore_option(self, option):
        current = option
        while current.down is not option:
            current.right.left = current
            current.left.right = current
            current = current.down

    def add_cell(self, constraint, option):
        cell = Node()
        constraint.up.down = cell
        cell.up = constraint.up
        cell.down = constraint
        constraint.up = constraint
        option.left.right = cell
        cell.left = option.left
        cell.right = option
        option.left = cell

    def add_given(self, *ref):
        self.givens.append(self.options[tuple(ref)])


class Sudoku:
    def __init__(self):
        self.table = Table()

        # bit-vectors indicating the elements that belong to each constraint group,
        # in order: row, column, box, number.
        groups = {"cell": "1100", "row": "1001", "col": "0101", "box": "0011"}
        elements = ["row", "col", "box", "num"]
        for group, vector in groups.items():
            size = len(vector)
            items = [i for i in range(size) if int(vector[i])]
            for i in range(9**2):
                n = [v + 1 for v in divmod(i, 9)]
                data = [None] * size
                data[items[0]] = n[0]
                data[items[1]] = n[1]
                self.table.add_constraint(group, {k: v for k, v in zip(elements, data)})

        for i in range(9**2):
            d = {}
            d["row"], d["col"] = divmod(i, 9)
            for d["num"] in range(9):
                d["box"] = 3 * (d.get("col") // 3) + (d.get("row") // 3)
                data = {k: v + 1 for k, v in d.items()} 
                self.table.add_option(data)

    def solve(self, puzzle):
        for row, arr in enumerate(puzzle, start=1):
            for col, num in enumerate(arr, start=1):
                if num:
                    self.table.add_given(row, col, num)

        with open("DLX.txt", "w") as DLX:
            DLX.write(f"{self.table}")


sudoku = Sudoku()

puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def solve(puzzle):
    sudoku.solve(puzzle)


solve(puzzle)
