"""
This is our main driver file. This will be responsible for handling user input
and displaying the current GameState.
"""

import pygame as pg
from Chess import ChessEngine

WIDTH = HEIGHT = 800  # 512 is another option
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on

IMAGES = {}

"""
Initialize a global dictionary of images. This will be called exactly once in the main
"""


def loadImages():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]

    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("Assets/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: Can access separate images as well (e.g. IMAGES[wP.png])


"""
The main driver for our code. This will handle user input and updating the graphics
"""


def main():
    pg.display.set_caption("Chess Engine")
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # Flag variable for when a move is made
    loadImages()
    running = True
    sqSelected = ()  # No square is selected, keeps track of the last click of the user (tuple: (row, col))
    playerClicks = []  # Keeps track of the player clicks (two tuples: [(6,4), (4,4)])

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            # mouse handlers
            elif e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()  # (x,y) location of the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):  # The user clicked the same square twice
                    sqSelected = ()  # Deselect
                    playerClicks = []  # Clears player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)  # Append for both 1st and 2nd clicks

                if len(playerClicks) == 2:  # After the 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = ()  # reset the clicked content
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]

            # key handlers
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:  # undo when 'Z' is pressed
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)  # Draw squares on the board
    # Add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board)  # Draw pieces on top of those squares


"""
Draw the squares on the board. 
The top left square is always white/light
"""


def drawBoard(screen):
    colors = [pg.Color("white"), pg.Color("black")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pg.draw.rect(screen, color, pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using the current GameState.board
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not an empty square
                screen.blit(IMAGES[piece], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
