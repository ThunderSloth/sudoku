# This is a sudoku solver that makes use of the dancing links algorithm.
# Eli Bell
# 2023-10-23


class Node:
    def __init__(self):
        self._up = self
        self._down = self
        self._right = self
        self._left = self

    @property
    def up(self):
        return self._up
    @property
    def down(self):
        return self._down
    @property
    def right(self):
        return self._right
    @property
    def left(self):
        return self._left

    @up.setter
    def up(self, node):
        self._up = node

    @down.setter
    def down(self, node):
        self._down = node
    
    @right.setter
    def right(self, node):
        self._right = node

    @left.setter
    def left(self, node):
        self._left = node

class Cell(Node):
    def __init__(self, constraint, option):
        super().__init__()
        self._constraint = constraint
        self._constraint.candidates += 1
        self._option = option

        constraint.up.down = self
        self.up = constraint.up
        self.down = constraint
        constraint.up = constraint
        option.left.right = self
        self.left = option.left
        self.right = option
        option.left = self

    def remove_from_row(self):
        self._constraint.candidates -= 1
        self.up.down = self.down
        self.down.up = self.up

    def remove_from_col(self):
        self.right.left = self.left
        self.left.right = self.right

    def restore_2_row(self):
        self._constraint.candidates += 1
        self.up.down = self
        self.down.up = self

    def restore_2_col(self):
        self.right.left = self
        self.left.right = self

    @property
    def constraint(self):
        return self._constraint

    @property
    def option(self):
        return self._option

    def __str__(self):
        return "{}: {}".format(self._option, self._constraint)


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


def increment(func):
    def wrap(self, *args, **kwargs):
        self.__class__.count += 1
        return func(self, *args, **kwargs)
    return wrap

def decrement(func):
    def wrap(self, *args, **kwargs):
        self.__class__.count -= 1
        return func(self, *args, **kwargs)
    return wrap


class Constraint(Header):
    count = 0

    @increment
    def __init__(self, origin, group, data):
        super().__init__(data)
        self._group = group
        self._candidates = 0

        origin.left.right = self
        self.left = origin.left
        self.right = origin
        origin.left = self

    def __str__(self):
        data = super().__str__()
        return "{} ({}) = {}".format("Constraint", self.group, data)

    @property
    def group(self):
        return self._group

    @property
    def candidates(self):
        return self._candidates
   
    @candidates.setter
    def candidates(self, n):
        self._candidates = n

    @decrement
    def remove(self):
        current = self
        keep_going = True
        while keep_going:
            current.remove_from_col()
            current = current.down
            keep_going = current is not self

    @increment
    def restore(self):
        current = self
        keep_going = True
        while keep_going:
            current.restore_2_col()
            current = current.down
            keep_going = current is not self


class Option(Header):
    count = 0

    @increment
    def __init__(self, origin, data):
        super().__init__(data)

        origin.up.down = self
        self.up = origin.up
        self.down = origin
        origin.up = self

    def __str__(self):
        return "r{}c{}={}".format(*[self.data.get(v) for v in ["row", "col", "num"]])

    @decrement
    def remove(self):
        current = self
        keep_going = True
        while keep_going:
            current.remove_from_row()
            current = current.right
            keep_going = current is not self

    @increment
    def restore(self):
        current = self
        keep_going = True
        while keep_going:
            current.restore_2_row()
            current = current.right
            keep_going = current is not self


class Table:
    def __init__(self):
        self._origin = Origin()

        self._given = []  # list containing options
        self._solution = []  # list containing options
        self._removed = []  # list containing options and constraints
        self._options = {}  # dictionary for option look-up by (row, col, num)

    def __str__(self):
        intro = (
            "This is an exact cover matrix for the game Sudoku. The rows\n"
            "represent every possible candidate placement, while the columns \n"
            "represent the constraints derived from the rules of Sudoku.\n"
            "There are 9x9x9=729 possible candidates and 9x9x4=324 constraints.\n"
            "The occupied cells indicate where the candidates and constraints\n"
            "intersect, the numbers displayed are simply the corresponding\n"
            "candidate numbers for ease of reading.\n"
        )
        elements = ["row", "col", "box", "num"]
        lhs_width = 7
        header = [
            "{:{}}".format(f"{lhs:5s}:", lhs_width) for lhs in ["GROUP"] + elements
        ]
        candidates = "{:{}}".format(f"{'cand':5s}:", lhs_width)
        sep_index = [lhs_width]
        constraint = self._origin.right
        while constraint is not self._origin:
            if (
                constraint.left == self._origin
                or constraint.left.group != constraint.group
            ):
                header = [v + "|" for v in header]
                header[0] += constraint.group.upper()
                candidates += "|"
            candidates += str(constraint.candidates)
            for i, v in enumerate(elements, start=1):
                val = constraint.data.get(v)
                header[i] += " " if val is None else str(val)
            if (
                constraint.right == self._origin
                or constraint.right.group != constraint.group
            ):
                sep_index.append(len(header[1]))
                header[0] += " " * (len(header[1]) - len(header[0]))
            constraint = constraint.right

        sep_line = "".join(
            ["+" if i in sep_index else "-" for i in range(sep_index[-1])]
        )
        candidates = "\n".join([sep_line, candidates])
        table = []
        option = self._origin.down
        while option is not self._origin:
            num = option.data.get("num")
            if num == 1:
                table.append(f"{sep_line}")
            lhs = f"{str(option):{lhs_width}s}"
            table.append(lhs)
            constraint = self._origin.right
            while constraint is not self._origin:
                if len(table[-1]) in sep_index:
                    table[-1] += "|"
                table[-1] += str(num) if constraint.set.issubset(option.set) else " "
                constraint = constraint.right
            option = option.down
        return "\n".join([v for v in [intro] + header + [candidates] + table])


    def define_constraint(self, group, data):
        Constraint(self._origin, group, data)

    def define_option(self, data):
        # This function depends on all constraints being defined first!
        option = Option(self._origin, data)
        constraint = self._origin.right
        while constraint is not self._origin:
            if constraint.set.issubset(option.set):
                Cell(constraint, option)
            constraint = constraint.right
        self._options[tuple([data.get(v) for v in ["row", "col", "num"]])] = option

    def define_given(self, *ref):
        self._given.append(self._options[tuple(ref)])

    def algo_x(self):
        # If the matrix A has no columns, the current partial solution is a valid solution; terminate successfully.
        column = self._origin.right 
        if column.count == 0:
            return
        #Otherwise choose a column c (deterministically).
        least = column.candidates
        curr = column
        while curr is not self._origin:
            if least > curr.candidates:
                least = curr.candidates
                column = curr
            curr = curr.right
        #Choose a row r such that Ar, c = 1 (nondeterministically).
        cell = column.down
        row = cell.option
        #Include row r in the partial solution.
        self._solution.append(row)
        #For each column j such that Ar, j = 1,
            #for each row i such that Ai, j = 1,
                #delete row i from matrix A.
            #delete column j from matrix A.
        #Repeat this algorithm recursively on the reduced matrix A.)


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
                self.table.define_constraint(
                    group, {k: v for k, v in zip(elements, data)}
                )

        for i in range(9**2):
            d = {}
            d["row"], d["col"] = divmod(i, 9)
            for d["num"] in range(9):
                d["box"] = 3 * (d.get("col") // 3) + (d.get("row") // 3)
                data = {k: v + 1 for k, v in d.items()}
                self.table.define_option(data)

    def solve(self, puzzle):
        for row, arr in enumerate(puzzle, start=1):
            for col, num in enumerate(arr, start=1):
                if num:
                    self.table.define_given(row, col, num)

        with open("DLX.txt", "w") as DLX:
            DLX.write(f"{self.table}")
        self.table.algo_x()         
    
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
