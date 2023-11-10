# This is a sudoku solver that makes use of the dancing links algorithm.
# Eli Bell
# 2023-10-23

class Node():
    def __init__(self):
        self.n = None
        self.e = None
        self.s = None
        self.w = None

class Header(Node):
    def __init__(self, data):
        super().__init__(self)
        self.data = data        

class Array():
    def __init__(self):
        self.origin = Header(None)
        self.origin.n = self.origin
        self.origin.e = self.origin
        self.origin.s = self.origin
        self.origin.w = self.origin

    def add_item(self, data):
        head = Header(data)
        self.origin.w.e = head
        head.w = self.origin.w
        head.e = self.origin
        self.origin.w = head

    def add_option(self, data):
        head = Header(data)
        self.origin.n.s = head
        head.n = self.origin.n
        head.s = self.origin
        self.origin.n = head

    def remove_item(self, head):
        current = head
        while current.e is not head:
            current.n.s = current.s
            current.s.n = current.n
            current = current.e

    def remove_option(self, head):
        current = head
        while current.s is not head:
            current.e.w = current.w
            current.w.e = current.e
            current = current.s

    def restore_item(self, head):
        current = head
        while current.e is not head:
            current.n.s = current
            current.s.n = current
            current = current.e

    def restore_option(self, head):
        current = head
        while current.s is not head:
            current.e.w = current
            current.w.e = current
            current = current.s

    def add_cell(self, item, option):
        cell = Node()
        item.n.s = cell
        cell.n = item.n
        cell.s = item
        item.n = item
        option.w.e = cell
        cell.w = option.w
        cell.e = option
        option.w = cell
