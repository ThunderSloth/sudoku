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
        self.data = []
        for v in data:
            self.data.append(v)


class Constraint(Header):
    def __init__(self, group, data):
        super().__init__(data)
        self.group = group


class Option(Header):
    def __init__(self, data):
        super().__init__(data)


class Table:
    def __init__(self):
        self.origin = Origin()
        self.origin.up = self.origin
        self.origin.right = self.origin
        self.origin.down = self.origin
        self.origin.left = self.origin

    def add_constraint(self, group, data):
        constraint = Constraint(group, data)
        self.origin.left.right = constraint
        constraint.left = self.origin.left
        constraint.right = self.origin
        self.origin.left = constraint

    def add_option(self, data):
        option = Option(data)
        self.origin.up.down = option
        option.up = self.origin.up
        option.down = self.origin
        self.origin.up = option
        constraint = self.origin.right
        while constraint is not self.origin:
            self.add_cell(constraint, option)
            constraint = constraint.right

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


class Sudoku:
    def __init__(self):
        self.table = Table()

        # bit-vectors indicating the elements that belong to each constraint group,
        # in order: row, column, box, number.
        groups = {"cell": "1100", "row": "1001", "col": "0101", "box": "0011"}
        for group, vector in groups.items():
            size = len(vector)
            items = [i for i in range(size) if int(vector[i])]
            for i in range(9**2):
                n = divmod(i, 9)
                data = [None] * size
                data[items[0]] = n[0]
                data[items[1]] = n[1]
                self.table.add_constraint(group, data)

        for i in range(9**2):
            row, col = divmod(i, 9)
            for num in range(9):
                box = 3 * (col // 3) + (row // 3)
                data = [row, col, box, num]
                self.table.add_option(data)


Sudoku()
