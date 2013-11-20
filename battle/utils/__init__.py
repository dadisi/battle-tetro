from battle.configs import *
from battle.templates import *
from battle import COLORS
import random

pieces = []


def convert_pixel_to_coordinates(box_x, box_y, offset=0):
    """
    Convert the given xy coordinates of the board to xy
    coordinates of the location on the screen.
    """
    return X_MARGIN + offset + (box_x * BOX_SIZE), TOP_MARGIN + (box_y * BOX_SIZE)


def get_new_piece():
    """
    Return a random new piece in a random rotation, color, and location.
    """
    shape = random.choice(list(SHAPES.keys()))
    new_piece = {
        'shape': shape,
        'rotation': random.randint(0, len(SHAPES[shape]) - 1),
        'x': random.randint(0 + TEMPLATE_WIDTH, BOARD_WIDTH - TEMPLATE_WIDTH),
        'y': -2,  # start it above the board (i.e. less than 0)
        'color': random.randint(0, len(COLORS) - 1)
    }
    return new_piece


def get_blank_board():
    """
    Create and return a new blank board data structure.
    """
    board = []
    for i in range(BOARD_WIDTH):
        board.append([BLANK] * BOARD_HEIGHT)
    return board


def calculate_level_and_fall_frequency(score):
    """
    Based on the score, return the level player is on and
    how many seconds pass until a falling piece falls one space.

    @param score:
    """
    level = int(score / 10) + 1
    fall_frequency = 0.27 - (level * 0.02)
    return level, fall_frequency


def get_new_piece(turn=None):
    """
    Return a random new piece in a random rotation, color, and location.
    """
    if turn is not None and turn < len(pieces):
        return pieces[turn]
    shape = random.choice(list(SHAPES.keys()))
    new_piece = {
        'shape': shape,
        'rotation': random.randint(0, len(SHAPES[shape]) - 1),
        'x': random.randint(0 + TEMPLATE_WIDTH, BOARD_WIDTH - TEMPLATE_WIDTH),
        'y': -2,  # start it above the board (i.e. less than 0)
        'color': random.randint(0, len(COLORS) - 1)
    }
    pieces.append(new_piece)
    return new_piece


def is_on_board(x, y):
    return (0 <= x < BOARD_WIDTH) and y < BOARD_HEIGHT


def is_valid_position(board, piece, adj_x=0, adj_y=0):
    """
    Return True if the piece is within the board and not colliding.
    """
    for x in range(TEMPLATE_WIDTH):
        for y in range(TEMPLATE_HEIGHT):
            is_above_board = y + piece['y'] + adj_y < 0
            if is_above_board or SHAPES[piece['shape']][piece['rotation']][x][y] in (BLANK, POISON):
                continue
            if not is_on_board(x + piece['x'] + adj_x, y + piece['y'] + adj_y):
                return False
            if board[x + piece['x'] + adj_x][y + piece['y'] + adj_y] != BLANK:
                return False
    return True
