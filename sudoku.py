import tkinter as tk

class Cell:
    def __init__(self, row, column, box, given):
        self.row = row
        self.column = column
        self.box = box
        self.candidates = {given} if given else set(range(1,10))
        self.is_given = bool(given)

    def get_candidates(self):
        return self.candidates.copy()

    def get_solution(self):
        return next(iter(self.candidates)) if len(self.candidates) == 1 else None

    def get_is_given(self):
        return self.is_given

    def remove_candidates(self, candidates):
        self.candidates -= candidates

class House:
    def __init__(self):
        self.cells = set()

    def add_cell(self, cell):
        self.cells.add(cell)

class Row(House):
    def __init__(self):
        super().__init__()

class Column(House):
    def __init__(self):
        super().__init__()

class Box(House):
    def __init__(self):
        super().__init__()

class Grid:
    def __init__(self, grid):
        self.grid = grid
        self.rows = [Row() for _ in range(9)]
        self.columns = [Column() for _ in range(9)]
        self.boxes = [Box() for _ in range(9)]
        self.cells = []
        for i in range(9**2):
            row,column = divmod(i,9)
            box = 3*(row//3) + (column//3)
            self.cells.append(Cell(row, column, box, grid[row][column]))
            self.rows[row].add_cell(self.cells[-1])
            self.columns[column].add_cell(self.cells[-1])
            self.boxes[box].add_cell(self.cells[-1])


class SudokuGUI:

    def __init__(self, sudoku):
        '''Construct a 3x3 frame to represent each 9-square box.
        Divide each box with a 3x3 subframe to represent individual cells.
        Finally, divide each cell with a 3x3 subsubframe to represent note-numbers.
        I would have simply made one giant grid and drew lines where I needed,
        but TKinter doesn't support transparent bounding boxes.'''
        self.sudoku = sudoku
        win_size = 500
        root = tk.Tk()
        root.title('Sudoku')
        root.geometry(f'{win_size}x{win_size}')
        self.frame = tk.Frame()
        self.frame.pack(expand=True, fill=tk.BOTH)
        self.frame.rowconfigure(list(range(3)), weight=1, uniform='row')
        self.frame.columnconfigure(list(range(3)), weight=1, uniform='col')
        self.numbers = [dict() for _ in range((9**2))]
        for i in range(9):
            box_row, box_col = divmod(i, 3)
            box = tk.Frame(self.frame, highlightthickness=2, highlightbackground='black')
            box.grid(row=box_row, column=box_col, sticky='nsew')
            box.rowconfigure(list(range(3)), weight=1, uniform='box')
            box.columnconfigure(list(range(3)), weight=1, uniform='box')
            for j in range(9):
                cell_row, cell_col = divmod(j, 3)
                cell = tk.Frame(box, highlightthickness=1, highlightbackground='black')
                cell.grid(row=cell_row, column=cell_col, sticky='nsew')
                cell.rowconfigure(list(range(3)), weight=1, uniform='cell')
                cell.columnconfigure(list(range(3)), weight=1, uniform='cell')
                x = (box_col*3) + cell_col
                y = (box_row*3) + cell_row
                cell_id = y * 9 + x
                num = tk.Label(box, text=' ', font=('', 40))
                num.grid(row=cell_row, column=cell_col, padx=1, pady=1, sticky='nsew')
                num.lower()
                self.numbers[cell_id]['solution'] = num
                self.numbers[cell_id]['notes'] = []
                for m in range(9):
                    subcell_row, subcell_col = divmod(m, 3)
                    subcell = tk.Frame(cell)
                    subcell.grid(row=subcell_row, column=subcell_col, sticky='nesw')
                    note = tk.Label(subcell, text=str(m+1), font=('', 10))
                    note.grid(row=subcell_row, column=subcell_col, sticky='nsew')
                    self.numbers[cell_id]['notes'].append(note)

    def display(self):
        for i, cell in enumerate(self.sudoku.cells):
            solution = cell.get_solution()
            if solution:
                self.numbers[i]['solution'].config(
                    text=str(solution), 
                    fg='black' if cell.get_is_given() else 'blue')
                self.numbers[i]['solution'].lift()
            else:
                candidates = cell.get_candidates()
                for j in range(9):
                    if j+1 not in candidates:
                        self.numbers[i]['notes'][j].config(text='')
        self.frame.mainloop()

def sudoku_solver(puzzle):
    sudoku = Grid(puzzle)
    gui = SudokuGUI(sudoku)
    gui.display()

puzzle = [[7, 0, 0, 0, 0, 0, 0, 0, 3], [0, 0, 3, 1, 0, 5, 7, 0, 0], [0, 2, 0, 7, 9, 3, 0, 8, 0], [0, 8, 0, 3, 0, 1, 0, 6, 0], [0, 0, 1, 0, 0, 0, 8, 0, 0], [0, 7, 0, 9, 0, 8, 0, 4, 0], [0, 3, 0, 0, 4, 9, 0, 7, 0], [0, 0, 7, 5, 0, 2, 9, 0, 0], [9, 0, 0, 0, 0, 7, 0, 0, 5]]

sudoku_solver(puzzle)


            
