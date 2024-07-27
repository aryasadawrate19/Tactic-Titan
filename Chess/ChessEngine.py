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

        self.moveFunction = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.moveLog = []
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()  # Square where en passant capture can happen
        # Castling rights
        self.whiteCastleKingSide = True
        self.whiteCastleQueenSide = True
        self.blackCastleKingSide = True
        self.blackCastleQueenSide = True
        self.castleRightsLog = [CastleRights(self.whiteCastleKingSide, self.blackCastleKingSide, self.whiteCastleQueenSide, self.blackCastleQueenSide)]

    """
    Takes a move as a parameter 
    """

    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = '--'
        self.moveLog.append(move)  # Log move
        self.whiteToMove = not self.whiteToMove  # Switch turns
        # Update king's position
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # If pawn moves twice next move can capture en passant
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()
        # If en passant move, must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--'
        # If pawn promotion changes piece
        if move.pawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N: ")  # We can make this part of the UI later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
        # Update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.whiteCastleKingSide, self.blackCastleKingSide,
                                                 self.whiteCastleQueenSide, self.blackCastleQueenSide))
        # Castle Moves
        if move.castle:
            if move.endCol - move.startCol == 2:  # King Side
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # Move rook
                self.board[move.endRow][move.endCol + 1] = '--'  # Empty space where rook was

    """
    Undo the last move
    """

    def undoMove(self):
        if len(self.moveLog) != 0:  # Make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turn back
            # Update the king's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.endCol)
            # Undo enpassant is different
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--'  # Removes the pawn that was added in the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # Puts the pawn on the correct square it was captured from
                self.enPassantPossible = (move.endRow, move.endCol)  # Allow en passant to happen on the next move
                # Undo a 2 square pawn advance should make enPassantPossible = () again
                if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                    self.enPassantPossible = ()
                # Give back castle rights if move took them away
                self.castleRightsLog.pop()  # Remove last moves updates
                castleRights = self.castleRightsLog[-1]
                self.whiteCastleKingSide = castleRights.wks
                self.blackCastleKingSide = castleRights.bks
                self.whiteCastleQueenSide = castleRights.wqs
                self.blackCastleQueenSide = castleRights.bqs
            # Undo castle
            if move.castle:
                if move.endCol - move.startCol == 2:  # Kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]  # Move rook
                    self.board[move.endRow][move.endCol - 1] = '--'  # Empty space where rook was
                else:  # Queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]  # Move rook
                    self.board[move.endRow][move.endCol + 1] = '--'  # Empty space where rook was
    """
    All moves considering checks
    """

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # Only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # To block a check you must move a piece into one of the squares between the enemy pieces and king
                check = self.checks[0]  # Check Information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # Enemy piece causing the check
                validSquares = []  # Squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # Once you get to piece and checks
                            break
                # Get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1):  # Go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K':  # Move doesn't move king, so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # Move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # Double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # Not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    """
    Determines if the current player is in check
    """

    """def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    """
    #Determines if the enemy can attack the square r,c
    """

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # Square is under attack
                self.whiteToMove = not self.whiteToMove  # Switch turns back
                return True
        return False"""

    """
    All moves without considering checks
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # Number of rows
            for c in range(len(self.board[r])):  # Number of columns in a given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # Calls the appropriate move function based on piece type
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    """

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        pawnPromotion = False

        if self.board[r+moveAmount][c] == '--':  # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r+moveAmount == backRow:  # If piece gets to back rank then it is a pawn promotion
                    pawnPromotion = True
                moves.append(Move((r, c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r+2*moveAmount][c] == '--':  # 2 square moves
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))

        if c-1 >= 0:  # Capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c-1][0] == enemyColor:
                    if r + moveAmount == backRow:  # If piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))
        if c+1 <= 7:  # Captures to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow:  # If piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant=True))

    """
    Gets all the rook moves for the rook located at the row, col and add these moves to the list
    """

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # Can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # Empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # Enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                    else:  # Friendly piece invalid
                        break
                else:  # Off board
                    break

    """
    Gets all the knight moves for the knight located at the row, col and add these moves to the list
    """

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # Not an ally piece (empty or enemy piece)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Gets all the bishop moves for the bishop located at the row, col and add these moves to the list
    """

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):  # Bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # Empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # Enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                    else:  # Friendly piece invalid
                        break
                else:  # Off board
                    break

    """
    Gets all the queen moves for the queen located at the row, col and add these moves to the list
    """

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
    Gets all the king moves for the king located at the row, col and add these moves to the list
    """

    def getKingMoves(self, r, c, moves):
        # kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an ally piece (empty or enemy piece)
                    # Place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # Place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    """
    Returns if the player is in check, a list of pins, and a list of checks
    """

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Checks outward from king for pins and checks, keeps track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # Reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here
                        # 1. Orthogonally away from king and piece is a rook
                        # 2. Diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. Any direction and piece is a queen
                        # 5. Any direction 1 square away and piece is a king (This is necessary to prevent a king move to a square controlled by another king)

                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # No piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # Piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # Enemy piece not applying checks
                            break
                else:
                    break  # Off board
        # Check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # Enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.whiteCastleQueenSide = False
            self.whiteCastleKingSide = False
        elif move.pieceMoved == 'bK':
            self.blackCastleQueenSide = False
            self.blackCastleKingSide = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 7:
                    self.whiteCastleKingSide = False
                elif move.startCol == 0:
                    self.whiteCastleQueenSide = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 7:
                    self.blackCastleKingSide = False
                elif move.startCol == 0:
                    self.blackCastleQueenSide = False
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # Maps keys to values
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion = False, castle = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        self.pawnPromotion = pawnPromotion
        self.castle = castle
        if enPassant:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'  # En Passant captures opposite coloured pawn
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

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
