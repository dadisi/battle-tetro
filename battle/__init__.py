import pygame
import random
import sys
import time
from battle.palette import *
from battle.templates import *
from battle.configs import *
from pygame.locals import *


BG_COLOR = BLACK
BORDER_COLOR = (DARK_RED, DARK_CYAN)
TEXT_COLOR = WHITE
TEXT_SHADOW = GRAY
COLORS = (DARK_BLUE, DARK_GREEN, DARK_RED, DARK_YELLOW)
LIGHT_COLORS = (BLUE, GREEN, RED, YELLOW)
pygame.init()

assert len(COLORS) == len(LIGHT_COLORS)  # each color must have a light color


def check_for_quit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)


def terminate():
    pygame.quit()
    sys.exit()


def check_for_key_press():
    """
    Go through event queue looking for a KEYUP event.
    Grab KEYDOWN events and remove them from the event queue.
    """
    check_for_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

from battle.utils import get_new_piece, is_valid_position


class BattleTetro(object):
    clock = None
    surface = None
    fonts = dict(basic=None, big=None)
    now = None
    players = list()

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fonts['basic'] = pygame.font.Font('freesansbold.ttf', 18)
        self.fonts['big'] = pygame.font.Font('freesansbold.ttf', 100)
        pygame.display.set_caption('Tetromino')

    def execute(self):
        while True:
            #if random.randint(0, 1) == 0:
            #    pygame.mixer.music.load('sound/tetrisb.mid')
            #else:
            #    pygame.mixer.music.load('sound/tetrisc.mid')
            #pygame.mixer.music.play(-1, 0.0)
            self.run_game()
            #pygame.mixer.music.stop()
            self.show_text_screen('Game Over')

    def run_game(self):
        # Setup variable for the start of the game
        self.now = time.time()
        player_count = 2  # self.get_number_of_players()  # TODO: Work this out as network or local. Two is max.
        falling_piece = get_new_piece()
        next_piece = get_new_piece()

        for i in range(player_count):
            from battle.player import Player
            player = Player(self.now, i, (player_count == 1))
            player.border_color = BORDER_COLOR[i]
            player.falling_piece = falling_piece.copy()
            player.next_piece = next_piece.copy()
            self.players.append(player)

        while True:
            now = time.time()
            stop_play = True
            for player in self.players:
                player.now = now
                if player.falling_piece is None:
                    # No falling piece in play, so start a new piece at the top
                    player.update_falling_piece(now)
                player.game_over = not is_valid_position(player.board, player.falling_piece)
                stop_play = player.game_over and stop_play

            if stop_play:
                return  # can't fit a new piece on the board, so game over

            check_for_quit()
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == K_p:
                        if len(self.players) > 1:
                            continue
                        # Pausing the game
                        self.surface.fill(BG_COLOR)
                        #pygame.mixer.music.stop()
                        self.show_text_screen('Paused')  # pause until a key press
                        #pygame.mixer.music.play(-1, 0.0)
                        now = time.time()
                        for player in self.players:
                            player.last_fall_time = now
                            player.last_move_down_time = now
                            player.last_move_sideways_time = now
                    else:
                        for player in self.players:
                            player.handle_event(KEYUP, event.key)

                elif event.type == KEYDOWN:
                    for player in self.players:
                            player.handle_event(KEYDOWN, event.key)

            now = time.time()
            for player in self.players:
                player.calculate_moves(now)
            # draw everything from the board on to the screen
            self.surface.fill(BG_COLOR)
            self.draw_status(self.players[0].score, self.players[0].level)
            self.draw_next_piece()
            for player in self.players:
                self.draw_board(player.board, player.board_offset, player.border_color)
                if player.falling_piece is not None:
                    self.draw_piece(player.falling_piece, offset=player.board_offset)

            pygame.display.update()
            self.clock.tick(FPS)

    def show_text_screen(self, text):
        """
        This function displays large text in the
        center of the screen until a key is pressed.
        Draw the text drop shadow
        @param text:
        """
        title_surface, title_rect = self.make_text_objects(text, self.fonts['big'], TEXT_SHADOW)
        title_rect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))
        self.surface.blit(title_surface, title_rect)

        # Draw the text
        title_surface, title_rect = self.make_text_objects(text, self.fonts['big'], TEXT_COLOR)
        title_rect.center = (int(WINDOW_WIDTH / 2) - 3, int(WINDOW_HEIGHT / 2) - 3)
        self.surface.blit(title_surface, title_rect)

        # Draw the additional "Press a key to play." text.
        press_key_surface, press_key_rect = self.make_text_objects('Press a key to play.', self.fonts['basic'], TEXT_COLOR)
        press_key_rect.center = (int(WINDOW_WIDTH / 2), 20)
        self.surface.blit(press_key_surface, press_key_rect)

        while check_for_key_press() is None:
            pygame.display.update()
            self.clock.tick()

        self.surface.fill(BG_COLOR)
        pygame.display.flip()

    def get_number_of_players(self):
        self.surface.fill(BG_COLOR)
        text = 'Players?'
        title_surface, title_rect = self.make_text_objects(text, self.fonts['big'], TEXT_SHADOW)
        title_rect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))
        self.surface.blit(title_surface, title_rect)

        # Draw the text
        title_surface, title_rect = self.make_text_objects(text, self.fonts['big'], TEXT_COLOR)
        title_rect.center = (int(WINDOW_WIDTH / 2) - 3, int(WINDOW_HEIGHT / 2) - 3)
        self.surface.blit(title_surface, title_rect)

        # Draw the additional "Press a key to play." text.
        press_key_surface, press_key_rect = self.make_text_objects('Press Enter 1 or 2.', self.fonts['basic'], TEXT_COLOR)
        press_key_rect.center = (int(WINDOW_WIDTH / 2), 20)
        self.surface.blit(press_key_surface, press_key_rect)

        font = pygame.font.Font(None, 50)
        num_players = ""
        while True:
            for evt in pygame.event.get():
                if evt.type == KEYDOWN:
                    if evt.unicode.isalpha():
                        num_players += evt.unicode
                    elif evt.key == K_BACKSPACE:
                        name = num_players[:-1]
                    elif evt.key == K_RETURN:
                        num_players = ""
                elif evt.type == QUIT:
                    return

            block = font.render(num_players, True, TEXT_COLOR)
            rect = block.get_rect()
            rect.center = self.surface.get_rect().center
            self.surface.blit(block, rect)
            pygame.display.update()
        return int(num_players)

    def draw_box(self, box_x, box_y, color, pixel_x=None, pixel_y=None, offset=0):
        """
        Draw a single box (each tetromino piece has four boxes)
        at xy coordinates on the board. Or, if pixel_x & pixel_y
        are specified, draw to the pixel coordinates stored in
        pixel_x & pixel_y (this is used for the "Next" piece).

        @param box_x:
        @param box_y:
        @param color:
        @param pixel_x:
        @param pixel_y:
        """
        if color == BLANK:
            return
        if pixel_x is None and pixel_y is None:
            pixel_x, pixel_y = BattleTetro.convert_pixel_to_coordinates(box_x, box_y, offset)
        pygame.draw.rect(self.surface, COLORS[color], (pixel_x + 1, pixel_y + 1, BOX_SIZE - 1, BOX_SIZE - 1))
        pygame.draw.rect(self.surface, LIGHT_COLORS[color], (pixel_x + 1, pixel_y + 1, BOX_SIZE - 4, BOX_SIZE - 4))

    def draw_board(self, board, offset=0, border_color=BORDER_COLOR[0]):
        """
        Draw the border around the border.

        @param board:
        """
        pygame.draw.rect(self.surface, border_color, (X_MARGIN - 3 + offset, TOP_MARGIN - 7, (BOARD_WIDTH * BOX_SIZE) + 8,
                                                     (BOARD_HEIGHT * BOX_SIZE) + 8), 5)

        # Fill the background of the board
        pygame.draw.rect(self.surface, BG_COLOR, (X_MARGIN + offset, TOP_MARGIN, BOX_SIZE * BOARD_WIDTH, BOX_SIZE * BOARD_HEIGHT))

        # Draw the individual boxes on the board
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                self.draw_box(x, y, board[x][y], offset=offset)

    def draw_status(self, score, level):
        """
        Draw the score text

        @param score:
        @param level:
        """
        score_surface = self.fonts['basic'].render('Score: %s' % score, True, TEXT_COLOR)
        score_rect = score_surface.get_rect()
        score_rect.topleft = (WINDOW_WIDTH - 140, 20)
        self.surface.blit(score_surface, score_rect)

        # Draw the level text
        level_surface = self.fonts['basic'].render('Level: %s' % level, True, TEXT_COLOR)
        level_rect = level_surface.get_rect()
        level_rect.topleft = (WINDOW_WIDTH - 140, 50)
        self.surface.blit(level_surface, level_rect)

    def draw_piece(self, piece, pixel_x=None, pixel_y=None, offset=0):
        shape_to_draw = SHAPES[piece['shape']][piece['rotation']]
        if pixel_x is None and pixel_y is None:
            # if pixel_x & pixel_y have not been specified, use the location stored in the piece data structure.
            pixel_x, pixel_y = self.convert_pixel_to_coordinates(piece['x'], piece['y'], offset)

        # Draw each of the blocks that make up the piece
        for x in range(TEMPLATE_WIDTH):
            for y in range(TEMPLATE_HEIGHT):
                if shape_to_draw[x][y] not in (BLANK, POISON):
                    self.draw_box(None, None, piece['color'], pixel_x + (x * BOX_SIZE), pixel_y + (y * BOX_SIZE))

    def draw_next_piece(self):
        """
        Draw the "Next" text.
        """
        next_surface = self.fonts['basic'].render('Next:', True, TEXT_COLOR)
        next_rect = next_surface.get_rect()
        next_rect.topleft = (WINDOW_WIDTH - 120, 100)
        self.surface.blit(next_surface, next_rect)

        for key, player in enumerate(self.players):
            # Draw the "next" piece
            self.draw_piece(player.next_piece, pixel_x=WINDOW_WIDTH-140, pixel_y=120+(int(key) * 90))

    @staticmethod
    def convert_pixel_to_coordinates(box_x, box_y, offset=0):
        """
        Convert the given xy coordinates of the board to xy
        coordinates of the location on the screen.
        """
        return X_MARGIN + offset + (box_x * BOX_SIZE), TOP_MARGIN + (box_y * BOX_SIZE)

    @staticmethod
    def make_text_objects(text, font, color):
        surface = font.render(text, True, color)
        return surface, surface.get_rect()


if __name__ == '__main__':
    BattleTetro().execute()
