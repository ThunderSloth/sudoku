# This is a sudoku solver that makes use of the dancing links algorithm.
# Eli Bell
# 2023-10-23


class Node:
    def __init__(self):
        self.up = None
        self.down = None
        self.right = None
        self.left = None


class Origin(Node):
    def __init__(self):
        super().__init__()


class Header(Node):
    def __init__(self, row: int, col: int, box: int, num: int):
        super().__init__()
        self.row = row
        self.col = col
        self.box = box
        self.num = num


class Constraint(Header):
    def __init__(self, group, *data: tuple[int, ...]):
        super().__init__(row, *data)
        self.group = group


class Option(Header):
    def __init__(self, row: int, col: int, num: int):
        box = 3 * (col // 3) + (row // 3)
        super().__init__(row, col, box, num)


class Table:
    def __init__(self):
        self.origin = Origin()
        self.origin.up = self.origin
        self.origin.right = self.origin
        self.origin.down = self.origin
        self.origin.left = self.origin

    def add_constraint(self, *data):
        head = Constraint(*data)
        self.origin.left.right = head
        head.left = self.origin.left
        head.right = self.origin
        self.origin.left = head

    def add_option(self, *data):
        head = Option(*data)
        self.origin.up.down = head
        head.up = self.origin.up
        head.down = self.origin
        self.origin.up = head

    def remove_constraint(self, head):
        current = head
        while current.right is not head:
            current.up.down = current.down
            current.down.up = current.up
            current = current.right

    def remove_option(self, head):
        current = head
        while current.down is not head:
            current.right.left = current.left
            current.left.right = current.right
            current = current.down

    def restore_constraint(self, head):
        current = head
        while current.right is not head:
            current.up.down = current
            current.down.up = current
            current = current.right

    def restore_option(self, head):
        current = head
        while current.down is not head:
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

        groups = [
            {"group": "cell", "row": True, "col": True, "box": False, "num": False},
            {"group": "row", "row": True, "col": False, "box": False, "num": True},
            {"group": "col", "row": False, "col": True, "box": False, "num": True},
            {"group": "box", "row": False, "col": False, "box": True, "num": True},
        ]

        for group in groups:
            data = []
            for k, v in group.items():
                if k == "group":
                    data[k] = v
                elif v
            for i in range(9**2):
                *n = divmod(i, 9)

               CONTINUE HERE             
                    row = group.get("row")
                    table.add_constraint(group, row, col, num)

        for i in range(9**2):
            row, col = divmod(i, 9)
            for num in range(1, 9):
                self.table.add_option(row, col, num)


Sudoku()
