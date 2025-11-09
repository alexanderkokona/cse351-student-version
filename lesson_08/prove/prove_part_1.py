"""
Course: CSE 251 
Assignment: 08 Prove Part 1
File:   prove_part_1.py
Author: Alex Kokona

Purpose: Part 1 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:

- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- Complete any TODO comments.
"""

import sys
import cv2

from screen import Screen
from maze import Maze
from cse351 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)      # path color
SLOW_SPEED = 100
FAST_SPEED = 1
speed = SLOW_SPEED


def solve_path(maze):
    """ Solve the maze and return the path found between the start and end positions.  
        The path is a list of positions, (row, col) """
    start_row, start_col = maze.get_start_pos()
    path = []

    def dfs(row, col):
        # can't move here
        if not maze.can_move_here(row, col):
            return False

        # reached the end
        if maze.at_end(row, col):
            path.append((row, col))
            return True

        # move onto this cell and show it
        maze.move(row, col, COLOR)

        # try all possible moves (maze already shuffles them)
        for nr, nc in maze.get_possible_moves(row, col):
            if dfs(nr, nc):
                # if child call found the end, add current cell to path
                path.append((row, col))
                return True

        # dead end → restore to visited/gray
        maze.restore(row, col)
        return False

    dfs(start_row, start_col)
    path.reverse()
    return path


def get_path(log, filename):
    """ Do not change this function """
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    path = solve_path(maze)

    log.write(f'Drawing commands to solve = {screen.get_command_count()}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True

    return path


def find_paths(log):
    """ Do not change this function """

    files = (
        'very-small.bmp',
        'very-small-loops.bmp',
        'small.bmp',
        'small-loops.bmp',
        'small-odd.bmp',
        'small-open.bmp',
        'large.bmp',
        'large-loops.bmp',
        'large-squares.bmp',
        'large-open.bmp'
    )

    log.write('*' * 40)
    log.write('Part 1')
    for filename in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        path = get_path(log, filename)
        log.write(f'Found path has length     = {len(path)}')
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_paths(log)


if __name__ == "__main__":
    main()
