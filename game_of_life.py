#
# Copyright Chinmaya Acharya
#
# SPDX-License-Identifier : GPL-2.0-only
#

from functools import partial
import os
from PIL import Image, ImageTk
import threading
import time
import tkinter
import pygame

#
# TODO : Add cell wrapping to calculate neighbours
# TODO : Improve graphics
#

RULES_STRING='''
Rules:

1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.

2. Any live cell with two or three live neighbours lives on to the next generation.

3. Any live cell with more than three live neighbours dies, as if by overpopulation.

4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction
'''

COLUMN_SIZE=45
MAX_CELLS = 1035
CELL_SELECTED=" "
CELL_UNSELECTED=" "
LOOP_DELAY=0.1
STATIC_PATH=os.path.dirname(os.path.abspath(__file__)) + os.sep + "_static" + os.sep
GAME_LOGO_FILENAME="game_of_life.svg"

class CellState:
    CellStateAlive = 0
    CellStateDead  = 1

class Cell(object):
    def __init__(self):
        self.state = CellState.CellStateDead
        self.button = None
        self._x_coordinate = 0
        self._y_coordinate = 0
        self._next_state = CellState.CellStateAlive

    def makeAlive(self):
        self.state = CellState.CellStateAlive
        self.button.config(text=CELL_SELECTED, bg="green", fg="black")

    def makeDead(self):
        self.state = CellState.CellStateDead
        self.button.config(text=CELL_UNSELECTED, bg="grey", fg="black")

    def isAlive(self):
        return True if self.state == CellState.CellStateAlive else False

    def isDead(self):
        return True if self.state == CellState.CellStateDead else False
    
    def setCoordinates(self, x, y):
        self._x_coordinate = x
        self._y_coordinate = y

    def getCoordinates(self):
        return self._x_coordinate, self._y_coordinate
    
    def setNextStateAlive(self):
        self._next_state = CellState.CellStateAlive
    
    def setNextStateDead(self):
        self._next_state = CellState.CellStateDead

    def getNextState(self):
        return self._next_state


class GameOfLife(threading.Thread):
    def __init__(self, year_label, cells, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        self._thread_active_flag = False
        self._current_year = 0
        self._year_label = year_label
        self._cells = cells
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def run(self):
        if self._thread_active_flag is True:
            raise RuntimeError
        self._thread_active_flag = True
        while self._thread_active_flag is True:
            # Core logic
            self._current_year += 1
            # print("Year ", self._current_year)
            # Increment year in label
            self._year_label.config(text="Years: %d" %self._current_year)
            for cell in self._cells:
                # List neighours
                # cell coordinates are 3,3
                # Neighbours are (2,2), (2,3), (2,4), (3,2), (3,4), (4,2), (4,3), (4,4)
                # cell coordinates are x,y
                # Neighbours are (x-1,y-1), (x-1,y), (x-1,y+1), (x,y-1), (x,y+1), (x+1,y-1), (x+1,y), (x+1,y+1)
                cell_x, cell_y = cell.getCoordinates()
                neighbours_coordinates = [
                    (cell_x - 1, cell_y - 1),
                    (cell_x - 1, cell_y),
                    (cell_x - 1, cell_y + 1),
                    (cell_x, cell_y - 1),
                    (cell_x, cell_y + 1),
                    (cell_x + 1, cell_y - 1),
                    (cell_x + 1, cell_y),
                    (cell_x + 1, cell_y + 1),
                ]
                # print(cell_x, cell_y)
                # print(neighbours_coordinates)
                neighbour_indices = list()
                # Calculate index of neighbours, removing out-of-grid coordinates
                for x,y in neighbours_coordinates:
                    if x < 0 or y < 0:
                        # x or y is negative
                        pass
                    elif ((0 < (MAX_CELLS % COLUMN_SIZE)) and (x > ((MAX_CELLS // COLUMN_SIZE))) or
                          (0 == (MAX_CELLS % COLUMN_SIZE)) and (x > ((MAX_CELLS // COLUMN_SIZE) - 1))):
                        # x exceeds number of rows
                        pass
                    elif y > COLUMN_SIZE - 1:
                        # y exceeds number of columns
                        pass
                    else:
                        # All other cells are neighbours
                        neighbour_indices.append((x * COLUMN_SIZE) + y)
                # print(neighbour_indices)
                # Get number of alive neighbours
                alive_count, _ = self.countAliveCells(neighbour_indices)
                # Set the next state of current cell based on neighbour state
                if cell.isAlive():
                    # Current cell is alive
                    if alive_count < 2:
                        # Less than 2 alive neighbours
                        # Current cell will die due to underpopulation
                        cell.setNextStateDead()
                    elif alive_count > 3:
                        # More than 3 alive neighbours
                        # Current cell will die due to overpopulation
                        cell.setNextStateDead()
                    else:
                        # 2 or 3 alive neighbours
                        # Current cell will live on to the next generation
                        cell.setNextStateAlive()
                else:
                    # Current cell is dead
                    if alive_count == 3:
                        # Cell will come live due to reproduction
                        cell.setNextStateAlive()
                    else:
                        # Cell will stay dead
                        cell.setNextStateDead()
            
            # Next state of all cells updated
            # Change the state now
            for cell in self._cells:
                if CellState.CellStateAlive == cell.getNextState():
                    cell.makeAlive()
                else:
                    cell.makeDead()
                pass

            # Wait for a while before starting next iteration
            time.sleep(LOOP_DELAY)

    def stop(self, timeout=None):
        self._thread_active_flag = False
        self.join(timeout)

    def getCurrentYear(self):
        return self._current_year

    def setCurrentYear(self, year):
        self._current_year = year

    def countAliveCells(self, neighbour_indices):
        alive_count = 0
        dead_count = 0
        for index in neighbour_indices:
            if self._cells[index].isAlive():
                alive_count += 1
            else:
                dead_count += 1

        return alive_count, dead_count

def create_application():
    main_app = tkinter.Tk()
    main_app.state("zoomed")
    main_app.title("Conway's Game of Life")
    # Convert SVG to PNG
    logo = pygame.image.load(STATIC_PATH + GAME_LOGO_FILENAME)
    pygame.image.save(logo, STATIC_PATH + "logo.png")
    # Load PNG as icon
    icon = Image.open(STATIC_PATH + "logo.png")
    photo = ImageTk.PhotoImage(icon)
    main_app.wm_iconphoto(False, photo)
    return main_app

def on_click(index):
    if cells[index].isDead():
        cells[index].makeAlive()
    else:
        cells[index].makeDead()

def create_cells(main_app):
    cells = list()
    for i in range(0, MAX_CELLS):
        cell = tkinter.Button(main_app, text=CELL_UNSELECTED, height=1, width=2, command=partial(on_click, i))
        cell.bind("<<Button-1>>")
        c = Cell()
        c.button = cell
        c.makeDead()
        cells.append(c)
    return cells

def align_cells(cells):
    row = 0
    col = 0
    for i in range(0, len(cells)):
        if i and (i % COLUMN_SIZE) == 0:
            row = row + 1
            col = 0
        cells[i].button.grid(row=row, column=col)
        cells[i].setCoordinates(row, col)
        col = col + 1
    return row,col

def game_loop():
    # Run till all cells are dead and we don't have a pause semaphore
    global game
    run_button.config(state=tkinter.DISABLED)
    reset_button.config(state=tkinter.DISABLED)
    for cell in cells:
        cell.button.config(state=tkinter.DISABLED)
    pause_button.config(state=tkinter.NORMAL)
    game.start()

def game_pause():
    # Run till all cells are dead and we don't have a pause semaphore
    global game
    game.stop(timeout=1)
    current_year = game.getCurrentYear()
    del game
    game = GameOfLife(year_label=year_label, cells=cells)
    game.setCurrentYear(current_year)
    run_button.config(state=tkinter.NORMAL)
    reset_button.config(state=tkinter.NORMAL)
    pause_button.config(state=tkinter.DISABLED)
    for cell in cells:
        cell.button.config(state=tkinter.NORMAL)

def cell_reset():
    # Reset all cells to make them dead
    global game
    for cell in cells:
        cell.makeDead()
    # Reset year count to 0
    game.setCurrentYear(0)
    # Reset year label also
    year_label.config(text="Years: 0")

# Create main application window
main_app = create_application()
# Create cells and align in tabular format
# cells is an array of Cell objects
cells = create_cells(main_app)
row, col = align_cells(cells)

# Create run and pause buttons
run_button = tkinter.Button(main_app, text="Run", borderwidth=2, width=5, height=2, relief='raised', command=game_loop, font=("Helvetica", 16))
run_button.bind("<<Button-1>>")
run_button.grid(row=row+2, column=0, columnspan=6)

year_label = tkinter.Label(main_app, text="Years: 0", borderwidth=2, width=10, height=3, font=("Helvetica", 16))
year_label.bind("<<Label-1>>")
year_label.grid(row=row+2, column=6, columnspan=6)

pause_button = tkinter.Button(main_app, state=tkinter.DISABLED, text="Pause", borderwidth=2, width=5, height=2, relief='raised', command=game_pause, font=("Helvetica", 16))
pause_button.bind("<<Button-1>>")
pause_button.grid(row=row+2, column=12, columnspan=6)

reset_button = tkinter.Button(main_app, text="Reset", borderwidth=2, width=5, height=2, relief='raised', command=cell_reset, font=("Helvetica", 16))
reset_button.bind("<<Button-1>>")
reset_button.grid(row=row+2, column=18, columnspan=6)

help_label = tkinter.Label(main_app, text=RULES_STRING, borderwidth=2, wraplength=250, justify='left', font=("Helvetica", 16))
help_label.bind("<<Label-1>>")
help_label.grid(row=0, column=COLUMN_SIZE + 1, columnspan=4, rowspan=50)

game = GameOfLife(year_label=year_label, cells=cells)

main_app.mainloop()

