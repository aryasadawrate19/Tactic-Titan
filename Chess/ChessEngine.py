import numpy as np

"""
This class is responsible for storing all the information
about the current state of a chess game. It will also
be responsible for determining the valid moves at the 
current state. It will also keep a move log.
"""


class GameState:
    # Board is a 8x8 2d numpy array, each element of the array has 2 characters
    # The first character represents the color of the piece 'b' or 'w'
    # The second character represents the type of the piece 'K', 'Q', 'R', 'N', 'B', 'P'

    def __init__(self):
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]])

        self.whiteToMove = True
        self.moveLog = []
