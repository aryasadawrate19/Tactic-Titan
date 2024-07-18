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

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # logs the move, so we can undo it later or keep history
        self.whiteToMove = not self.whiteToMove  # Swaps players.


class Move:
    # Maps keys to values
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getChessNotation(self):
        piece = self.pieceMoved[1]
        moveString = ''

        # Piece notation
        if piece != 'P':  # Pawn does not need piece notation
            moveString += piece

        # Capture notation
        if self.pieceCaptured != "--":
            if piece == 'P':  # Pawn captures need to add the file from where it started
                moveString += self.colsToFiles[self.startCol]
            moveString += 'x'

        # Destination square
        moveString += self.getRankFile(self.endRow, self.endCol)

        return moveString

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
