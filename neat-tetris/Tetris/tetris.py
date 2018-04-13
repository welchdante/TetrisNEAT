from random import randrange as rand
# import pygame, sys
from pprint import pprint
import neat

# The configuration
cell_size = 18
cols = 10
rows = 22
maxfps = 30

# colors = [
#     (0, 0, 0),
#     (255, 85, 85),
#     (100, 200, 115),
#     (120, 108, 245),
#     (255, 140, 50),
#     (50, 120, 52),
#     (146, 202, 73),
#     (150, 161, 218),
#     (35, 35, 35)  # Helper color for background grid
# ]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    board += [[1 for x in range(cols)]]
    return board


class Tetris(object):
    def __init__(self, genome, config):
        # pygame.init()
        # pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        # self.default_font = pygame.font.Font(
        #     pygame.font.get_default_font(), 12)
        #
        # self.screen = pygame.display.set_mode((self.width, self.height))
        # pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.game_end_info = {}
        self.genome = genome
        self.neural_network = neat.nn.FeedForwardNetwork.create(genome, config)
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.lines = 0
        self.score = 0
        self.holes = 0
        self.bumpiness = 0

        # pygame.time.set_timer(pygame.USEREVENT + 1, 1)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    # def draw_matrix(self, matrix, offset):
    #     off_x, off_y = offset
    #     for y, row in enumerate(matrix):
    #         for x, val in enumerate(row):
    #             if val:
                    # pygame.draw.rect(
                    #     self.screen,
                    #     colors[val],
                    #     pygame.Rect(
                    #         (off_x + x) *
                    #         cell_size,
                    #         (off_y + y) *
                    #         cell_size,
                    #         cell_size,
                    #         cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [2, 1000, 2500, 10000, 40000]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            # pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        # pygame.display.update()
        # sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                                self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while (not self.drop(True)):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def move_decision(self, board, current_piece, next_piece):
        nn_input = []
        for i in range(len(board)):
            for block in board[i]:
                if block > 0:
                    block = 1
                nn_input.append(block)

        current_piece_input = self.get_piece(current_piece)
        for element in current_piece_input:
            nn_input.append(element)

        next_piece_input = self.get_piece(next_piece)
        for element in next_piece_input:
            nn_input.append(element)

        output = self.neural_network.activate(nn_input)
        max_index = output.index(max(output))
        if max_index == 0:
            self.move(+1)
        elif max_index == 1:
            self.move(-1)
        elif max_index == 2:
            self.drop(True)
        else:
            self.rotate_stone()

    def get_piece(self, piece):
        if piece == [[1, 1, 1], [0, 1, 0]]:
            return [1, 0, 0, 0, 0, 0, 0]
        elif piece == [[0, 1, 1], [1, 1, 0]]:
            return [0, 1, 0, 0, 0, 0, 0]
        elif piece == [[1, 1, 0], [0, 1, 1]]:
            return [0, 0, 1, 0, 0, 0, 0]
        elif piece == [[1, 0, 0], [1, 1, 1]]:
            return [0, 0, 0, 1, 0, 0, 0]
        elif piece == [[0, 0, 1], [1, 1, 1]]:
            return [0, 0, 0, 0, 1, 0, 0]
        elif piece == [[1, 1, 1, 1]]:
            return [0, 0, 0, 0, 0, 1, 0]
        else:
            return [0, 0, 0, 0, 0, 0, 1]

    def calculate_holes(self):
        count = 0
        for col in range(len(self.board[0]) - 1):
            hit_block = False
            for row in range(len(self.board)):
                if self.has_block(row, col):
                    hit_block = True
                else:
                    if hit_block:
                        count += 1
        self.holes = count

    def calculate_bumpiness(self):
        count = 0
        for col in range(len(self.board[0]) - 1):
            height_1 = self.get_column_height(col)
            height_2 = self.get_column_height(col + 1)
            if height_1 > height_2:
                count += (height_1 - height_2)
            else:
                count += (height_2 - height_1)
        self.bumpiness = count

    def get_column_height(self, col):
        for row in range(len(self.board) - 1):
            if self.has_block(row, col):
                return rows - row
        return 0

    def has_block(self, row, col):
        if self.board[row][col] != 0:
            return True
        else:
            return False

    def run(self):
        # key_actions = {
        #     'ESCAPE': self.quit,
        #     'LEFT': lambda: self.move(-1),
        #     'RIGHT': lambda: self.move(+1),
        #     'DOWN': lambda: self.drop(True),
        #     'UP': self.rotate_stone,
        #     'p': self.toggle_pause,
        #     'SPACE': self.start_game,
        #     'RETURN': self.insta_drop
        # }
        #
        # self.gameover = False
        # self.paused = False

        # dont_burn_my_cpu = pygame.time.Clock()

        while not self.gameover:
#             self.screen.fill((0, 0, 0))
#             if self.paused:
#                 self.center_msg("Paused")
#             else:
#                 pygame.draw.line(self.screen,
#                                  (255, 255, 255),
#                                  (self.rlim + 1, 0),
#                                  (self.rlim + 1, self.height - 1))
#                 self.disp_msg("Next:", (
#                     self.rlim + cell_size,
#                     2))
#                 self.disp_msg("Score: %d\n\nLevel: %d\
# \nLines: %d" % (self.score, self.level, self.lines),
#                               (self.rlim + cell_size, cell_size * 5))
#                 self.draw_matrix(self.bground_grid, (0, 0))
#                 self.draw_matrix(self.board, (0, 0))
#                 self.draw_matrix(self.stone,
#                                  (self.stone_x, self.stone_y))
#                 self.draw_matrix(self.next_stone,
#                                  (cols + 1, 2))
#             pygame.display.update()
#
#             for event in pygame.event.get():
#                 if event.type == pygame.USEREVENT + 1:
#                     self.drop(False)
#                 elif event.type == pygame.QUIT:
#                     self.quit()
#                 elif event.type == pygame.KEYDOWN:
#                     for key in key_actions:
#                         if event.key == eval("pygame.K_" + key):
#                             key_actions[key]()

            self.move_decision(self.board, self.stone, self.next_stone)

            if self.gameover:
                self.calculate_holes()
                self.calculate_bumpiness()
                self.game_end_info = {
                    'score': self.score,
                    'holes': self.holes,
                    'bumpiness': self.bumpiness
                }
                return self.game_end_info, self.genome

            # dont_burn_my_cpu.tick(maxfps)


if __name__ == '__main__':
    App = TetrisApp()
    App.run()
