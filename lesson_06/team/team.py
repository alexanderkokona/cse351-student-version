""" 
Course: CSE 351
Team  : Week 06
File  : team_v3.py
Author: <Your Name>

Purpose: Final optimized version of the Week 06 team activity.

Optimizations added beyond the previous version:
- STEP 1: Precompute all positions for each word's first letter to skip scanning the entire board.
- STEP 2: Skip directions where the remaining letters would go out of bounds.
- STEP 3: Removed deepcopy(), replaced with lightweight tuple tracking.
- STEP 4: Minimal console output and per-word timing.
"""

import copy
import time

from cse351 import *

words = ['BOOKMARK', 'SURNAME', 'RETHINKING', 'HEAVY', 'IRONCLAD', 'HAPPY', 
         'JOURNAL', 'APPARATUS', 'GENERATOR', 'WEASEL', 'OLIVE', 
         'LINING', 'BAGGAGE', 'SHIRT', 'CASTLE', 'PANEL', 
         'OVERCLOCKING', 'PRODUCER', 'DIFFUSE', 'SHORE', 
         'CELL', 'INDUSTRY', 'DIRT', 
         'TEACHING', 'HIGHWAY', 'DATA', 'COMPUTER', 
         'TOOTH', 'COLLEGE', 'MAGAZINE', 'ASSUMPTION', 'COOKIE', 
         'EMPLOYEE', 'DATABASE', 'POET', 'COMPUTER', 'SAMPLE']


class bcolors:
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


class Board:

    SIZE = 25

    directions = (
        (1, 0),   # E
        (1, 1),   # SE
        (0, 1),   # S
        (-1, 1),  # SW
        (-1, 0),  # W
        (-1, -1), # NW
        (0, -1),  # N
        (1, -1)   # NE
    )

    def __init__(self):
        """Initialize the board and highlighting arrays"""
        self.size = self.SIZE
        self.highlighting = [[False for _ in range(self.SIZE)] for _ in range(self.SIZE)]

        # Provided static board
        self.board = [
            list("LSODAEOMAAIIASSAMGRCODAIR"),
            list("AVCSNTUUOHNCHABEUOMOCRGHAI"),
            list("ETHAASMS SCAOATNTSNHTAEPDH".replace(" ", "")),
            list("EISSS EWSLVRRHSEQSB SMERVKA".replace(" ", "")),
            list("RSSAHBBAL EEILBTRAWCKWWEOA".replace(" ", "")),
            list("UUGNIKNIHTERAVLLDNLHY SSTA".replace(" ", "")),
            list("MOCDMBNDUQMIAAHLENAPEKHIH"),
            list("LCOOKIEPUAOENTDQLQCNTJIDA"),
            list("CHGANVMMGYSREGELLLOCOFYRIN"),
            list("AEAGTOJAOUUWADEOVPOAONTUA"),
            list("AARECAZ WFOHAPCQSPTEVILOGA".replace(" ", "")),
            list("BVJEMIDFJTIEPACS HYXGRRZDE".replace(" ", "")),
            list("AYTLNAIDKGG EAMNI RONCLADDA".replace(" ", "")),
            list("GSWESDNUOIHYRGLLMIYDVMAJO"),
            list("GAEAAYARNWWOAU K NKT BIRTM".replace(" ", "")),
            list("AMASRCOAURALTOYCEOEEAFP P Y".replace(" ", "")),
            list("GPSSOIHVDSYPUBOROZTBPDMPM"),
            list("ELEUTJFIEDSM SLOKTUARDOPKH".replace(" ", "")),
            list("UELMANRCNRQEC RMYPSOZCAOSD".replace(" ", "")),
            list("CDGPRTEXYGCRDATMEDUDHOCAS"),
            list("ATNTEMOXESELRIOHUJQDBDIF F".replace(" ", "")),
            list("CDD INAKQNVKKOCNCQL OINDLUC".replace(" ", "")),
            list("AISOEGPGOMYOZCEDRDTUN IASS".replace(" ", "")),
            list("FRONGAAAACCPVRKD UAIARDZED".replace(" ", "")),
            list("DCDVAZNGSOLDIEIIDS SFCNUAI".replace(" ", ""))
        ]

    def highlight(self, row, col, on=True):
        self.highlighting[row][col] = on

    def get_letter(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.board[x][y]
        return ''

    def display(self):
        print()
        for row in range(self.size):
            for col in range(self.size):
                if self.highlighting[row][col]:
                    print(f'{bcolors.WARNING}{bcolors.BOLD}{self.board[row][col]}{bcolors.ENDC} ', end='')
                else:
                    print(f'{self.board[row][col]} ', end='')
            print()

    def _word_at_location(self, row, col, direction, word):
        """Check if word exists starting at (row, col) in given direction."""
        dir_x, dir_y = self.directions[direction]
        changes = []

        # Skip if word would go out of bounds
        end_x = row + dir_x * (len(word) - 1)
        end_y = col + dir_y * (len(word) - 1)
        if not (0 <= end_x < self.size and 0 <= end_y < self.size):
            return False

        for letter in word:
            if self.get_letter(row, col) == letter:
                changes.append((row, col))
                row += dir_x
                col += dir_y
            else:
                return False

        # If found, highlight
        for r, c in changes:
            self.highlight(r, c)
        return True

    def find_word(self, word):
        """Find and highlight the given word on the board."""
        print(f'Finding {word}...')
        first_char = word[0]

        # Precompute positions of first letter
        starts = [(r, c) for r in range(self.size) for c in range(self.size)
                  if self.board[r][c] == first_char]

        for (row, col) in starts:
            for d in range(8):
                if self._word_at_location(row, col, d, word):
                    return True
        return False


def main():
    board = Board()
    board.display()

    start = time.perf_counter()
    for word in words:
        w_start = time.perf_counter()
        if not board.find_word(word):
            print(f'Error: Could not find "{word}"')
        else:
            print(f'Found "{word}" in {time.perf_counter() - w_start:.4f}s')

    total_time = time.perf_counter() - start
    board.display()
    print(f'\nTotal time to find all words: {total_time:.4f}s')


if __name__ == '__main__':
    main()
