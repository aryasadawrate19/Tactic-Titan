"""
Main driver file.
Handling user input.
Displaying current GameStatus object.
"""

import pygame as pg
import ChessEngine
import sys

WIDTH = HEIGHT = 800
DIMENSION = 8

SQUARE_SIZE = HEIGHT // DIMENSION

MAX_FPS = 15

IMAGES = {}


def loadImages():
    """
    Initialize a global directory of images.
    This will be called exactly once in the main.
    """
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("Assets/images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    """
    The main driver for our code.
    This will handle user input and updating the graphics.
    """
    pg.display.set_caption("Tactic Titan")
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    
    loadImages()  # do this only once before while loop
    
    running = True
    sqSelected = ()  # no square is selected initially, this will keep track of the last click of the user (tuple(row, col))
    playerClicks = []  # this will keep track of player clicks (two tuples)

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()
            # mouse handler            
            elif e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()  # (x, y) location of the mouse
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if sqSelected == (row, col):  # user clicked the same square twice
                    sqSelected = ()  # deselect
                    playerClicks = []  # clear clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)  # append for both 1st and 2nd click
                if len(playerClicks) == 2:  # after 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    if move in validMoves:
                        print(move.getChessNotation())   
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = ()  # reset user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]
            # key handler
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()


def drawGameState(screen, gs):
    """
    Responsible for all the graphics within current game state.
    """
    drawBoard(screen)  # draw squares on the board
    # add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


def drawBoard(screen):
    """
    Draw the squares on the board.
    The top left square is always light.
    """
    colors = [pg.Color("white"), pg.Color("black")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            pg.draw.rect(screen, color, pg.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


if __name__ == "__main__":
    main()
