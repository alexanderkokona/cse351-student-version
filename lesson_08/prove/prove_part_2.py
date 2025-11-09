"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: Alex Kokona

Purpose: Part 2 of assignment 8, finding the end of the maze using recursion
and threading. Each time we reach a fork, we spawn threads so paths are
searched concurrently.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

I would have each path/thread maintain a list of the coordinates it visited. When a thread reaches
the exit and sets the global stop flag, that same thread can then walk back through its stored list
and recolor those cells as the “final path.”

Why would it work?

Because only the thread that actually finds the exit sets stop = True. That thread’s own visited
sequence is therefore the successful route. Recoloring only that list will display the correct path.
"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED


def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


def explore(maze, row, col, color):
    """Recursive threaded search from (row, col)."""
    global stop, thread_count

    # stop if someone else already found exit
    if stop:
        return

    # can't move here
    if not maze.can_move_here(row, col):
        return

    # reached exit
    if maze.at_end(row, col):
        stop = True
        maze.move(row, col, (255, 255, 255))   # mark exit clearly
        return

    # mark current cell
    maze.move(row, col, color)

    moves = maze.get_possible_moves(row, col)

    # if more than one path, fork
    if len(moves) > 1:
        threads = []
        for r, c in moves:
            if stop:
                break
            thread_count += 1
            t = threading.Thread(target=explore, args=(maze, r, c, get_color()))
            t.start()
            threads.append(t)
        # wait for all child threads
        for t in threads:
            t.join()
    elif len(moves) == 1:
        # continue straight
        nr, nc = moves[0]
        explore(maze, nr, nc, color)
    else:
        # dead end
        maze.restore(row, col)


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    global stop, thread_count
    stop = False
    thread_count = 1

    start_row, start_col = maze.get_start_pos()
    first_color = get_color()

    # start the initial recursive search (in current thread)
    explore(maze, start_row, start_col, first_color)


def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

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


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()
