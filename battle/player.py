import pygame
from battle import time, MOVE_DOWN_FREQ, BOARD_HEIGHT, BOARD_WIDTH, BLANK, POISON, SHAPES, BOX_SIZE, \
    TEMPLATE_HEIGHT, TEMPLATE_WIDTH, MOVE_SIDE_WAYS_FREQ
from utils import get_new_piece, get_blank_board, calculate_level_and_fall_frequency, is_valid_position
from pygame.locals import *

BOARD_OFFSET = [int(((BOX_SIZE * BOARD_WIDTH) / 2) + 60) * -1, int(((BOX_SIZE * BOARD_WIDTH) / 2) - 47)]
LEFT_CONTROLS = (K_q, K_w, K_a, K_s, K_d, K_SPACE)
RIGHT_CONTROLS = (K_UP, K_DOWN, K_LEFT, K_RIGHT, K_INSERT, K_HOME)
CONTROLS = (LEFT_CONTROLS, RIGHT_CONTROLS)


class Player(object):
    board = None
    border_color = None
    board_offset = 0
    now = None
    last_move_down_time = now
    last_move_sideways_time = now
    last_fall_time = now
    moving_down = False  # Note: there is no moving_up variable
    moving_left = False
    moving_right = False
    score = 0
    level = 0
    turn = 0
    fall_frequency = 0
    falling_piece = None
    next_piece = None
    controls = tuple()

    def __init__(self, now=None, player_num=0, single_player=True):
        if not now:
            self.now = time.time()
        else:
            self.now = now
        self.board = get_blank_board()
        self.last_move_down_time = self.last_fall_time = self.last_move_sideways_time = self.now
        self.update_level()
        self.turn = 1
        if single_player:
            self.controls = LEFT_CONTROLS + RIGHT_CONTROLS
        else:
            self.controls = CONTROLS[player_num]
            self.board_offset = BOARD_OFFSET[player_num]

    def update_level(self):
        self.level, self.fall_frequency = calculate_level_and_fall_frequency(self.score)

    def update_falling_piece(self, now):
        self.falling_piece = self.next_piece
        self.turn += 1
        self.next_piece = get_new_piece(self.turn)
        self.last_fall_time = now

    def remove_completed_line(self):
        """
        Remove any completed lines on the board, move everything above them
        down, and return the number of complete lines.
        """
        num_lines_removes = 0
        y = BOARD_HEIGHT - 1  # Start y at the bottom of the board
        while y >= 0:
            complete, bonus = self.is_completed_line_with_bonus(y)
            if complete:
                # Remove the line and pull boxes down by one line.
                for pull_down_y in range(y, 0, -1):
                    for x in range(BOARD_WIDTH):
                        self.board[x][pull_down_y] = self.board[x][pull_down_y - 1]
                # Set very top line to blank
                for x in range(BOARD_WIDTH):
                    self.board[x][0] = BLANK
                num_lines_removes += 1
                if bonus:
                    num_lines_removes += 4
                # Note on the next iteration of the loop, y is the same.
                # This is so that is the line that was pulled down is also
                # complete, it will be removed.
            else:
                y -= 1
        if num_lines_removes:
            self.score += num_lines_removes
            self.update_level()

    def is_completed_line_with_bonus(self, y):
        """
        Return True is the line filled with boxes with no gaps.
        """
        bonus = True
        block_color = None
        for x in range(BOARD_WIDTH):
            if self.board[x][y] in (BLANK, POISON):
                return False, False
            if block_color is None:
                block_color = self.board[x][y]
            if bonus:
                bonus = block_color == self.board[x][y]
        return True, bonus

    def handle_event(self, event_type, key):
        if key not in self.controls:
            return 
        if event_type == KEYUP:
            if key in (K_LEFT, K_a):
                self.moving_left = False
            elif key in (K_RIGHT, K_d):
                self.moving_right = False
            elif key in (K_DOWN, K_s):
                self.moving_down = False

        elif event_type == KEYDOWN:
            # moving the block sideways
            if key in (K_LEFT, K_a) and is_valid_position(self.board, self.falling_piece, adj_x=-1):
                self.falling_piece['x'] -= 1
                self.moving_left = True
                self.moving_right = False
                self.last_move_sideways_time = self.now
            elif key in (K_RIGHT, K_d) and is_valid_position(self.board, self.falling_piece, adj_x=1):
                self.falling_piece['x'] += 1
                self.moving_left = False
                self.moving_right = True
                self.last_move_sideways_time = self.now
            # Rotating the block (if there is room to rotate)
            elif key in (K_UP, K_w):
                self.falling_piece['rotation'] = (self.falling_piece['rotation'] + 1) % len(SHAPES[self.falling_piece['shape']])
                if not is_valid_position(self.board, self.falling_piece):
                    self.falling_piece['rotation'] = (self.falling_piece['rotation'] - 1) % len(SHAPES[self.falling_piece['shape']])
            elif key == K_q:
                self.falling_piece['rotation'] = (self.falling_piece['rotation'] - 1) % len(SHAPES[self.falling_piece['shape']])
                if not is_valid_position(self.board, self.falling_piece):
                    self.falling_piece['rotation'] = (self.falling_piece['rotation'] + 1) % len(SHAPES[self.falling_piece['shape']])

            # Make the block fall faster with the down key
            elif key in (K_DOWN, K_s):
                self.moving_down = True
                if is_valid_position(self.board, self.falling_piece, adj_y=1):
                    self.falling_piece['y'] += 1
                self.last_move_down_time = self.now

            # Move the current block all the way down
            elif key == K_SPACE:
                self.moving_down = False
                self.moving_left = False
                self.moving_right = False
                for i in range(1, BOARD_HEIGHT):
                    if not is_valid_position(self.board, self.falling_piece, adj_y=i):
                        break
                self.falling_piece['y'] += i - 1

    def calculate_moves(self, now):
        # Handling moving the block because of user input
        if (self.moving_left or self.moving_right) and now - self.last_move_sideways_time > MOVE_SIDE_WAYS_FREQ:
            if self.moving_left and is_valid_position(self.board, self.falling_piece, adj_x=-1):
                self.falling_piece['x'] -= 1
            elif self.moving_right and is_valid_position(self.board, self.falling_piece, adj_x=1):
                self.falling_piece['x'] += 1
            self.last_move_sideways_time = now
        if self.moving_down and now - self.last_move_down_time > MOVE_DOWN_FREQ and is_valid_position(self.board, self.falling_piece, adj_y=1):
            self.falling_piece['y'] += 1
            self.last_move_down_time = now

        # Let the piece fall if it is time to fall
        if now - self.last_fall_time > self.fall_frequency:
            # See if the piece has landed.
            if not is_valid_position(self.board, self.falling_piece, adj_y=1):
                # falling piece has landed, set it on the self.board
                self.add_to_board(self.falling_piece)
                self.remove_completed_line()
                self.falling_piece = None
            else:
                # piece did not land just move it down one block
                self.falling_piece['y'] += 1
                self.last_fall_time = now

    def add_to_board(self, piece):
        """
        Fill in the board based on piece's location, shape, and rotation
        """
        for x in range(TEMPLATE_WIDTH):
            for y in range(TEMPLATE_HEIGHT):
                if SHAPES[piece['shape']][piece['rotation']][x][y] != BLANK:
                    self.board[x + piece['x']][y + piece['y']] = piece['color']
