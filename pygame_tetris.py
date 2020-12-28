#!python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from copy import deepcopy
from os.path import join, dirname, expanduser
import pickle
import random
import sys


# const
BLACK = pygame.Color('#333333')
GREY = pygame.Color('#808080')
WHITE = pygame.Color('#fafafa')
LIGHT = pygame.Color('#bdbdbd')
FPS = 60


# Returns path containing content - either locally or in pyinstaller tmp file
def resourcePath():
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        return join(sys._MEIPASS)
    return join(dirname(__file__))


class Game:
    """Create a single-window app"""

    def __init__(self):
        """Initialize pygame and the application"""
        pygame.init()

        # Настройка окна
        self.windowSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # pygame.display.set_mode((800, 880))
        pygame.display.set_caption('TETRIS')

        self.TILE = min(self.windowSurface.get_width() // 17, self.windowSurface.get_height() // 22)
        self.gameSurface = self.windowSurface.subsurface(
            pygame.Rect(self.windowSurface.get_width() / 2 - self.TILE * 17 / 2,
                        self.windowSurface.get_height() / 2 - self.TILE * 22 / 2,
                        self.TILE * 17, self.TILE * 22))
        self.boardSurface = self.gameSurface.subsurface(
            pygame.Rect(self.TILE, self.TILE, self.TILE * 10, self.TILE * 20))
        self.infoSurface = self.gameSurface.subsurface(
            pygame.Rect(self.TILE * 12, self.TILE, self.TILE * 4, self.TILE * 20))
        self.grid = [pygame.Rect(x * self.TILE, y * self.TILE, self.TILE, self.TILE) for x in range(10) for y in
                     range(20)]

        # Фигуры
        self.figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                            [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                            [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                            [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, -1)],
                            [(-1, 0), (-1, -1), (-1, 1), (0, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        self.figures = [[pygame.Rect(x + 5, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in self.figures_pos]
        self.figure_rect = pygame.Rect(0, 0, self.TILE - 2, self.TILE - 2)

        self.figure, self.next_figure = deepcopy(random.choice(self.figures)), deepcopy(random.choice(self.figures))
        self.random_color = lambda: (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
        self.color, self.next_color = self.random_color(), self.random_color()

        # Матрица игрового поля
        self.field = [[0 for i in range(10)] for j in range(20)]

        self.clock = pygame.time.Clock()
        self.count_frame = 0
        self.left, self.right, self.down, self.up = False, False, False, False

        # Параметры анимации движения
        self.anim_count, self.anim_speed, self.anim_limit = 0, 1, FPS

        self.best = 0
        self.score = 0
        self.level = 1

        # текст
        self.game_font = pygame.font.Font(join(resourcePath(), 'PressStart2P-Regular.ttf'), int(self.TILE / 1.5))
        self.next_text = self.game_font.render('next', True, WHITE)
        self.best_text = self.game_font.render('best', True, WHITE)
        self.lines_text = self.game_font.render('lines', True, WHITE)
        self.level_text = self.game_font.render('level', True, WHITE)
        self.gameover_text = self.game_font.render('game over', True, WHITE)

        # меню
        self.pos = self.boardSurface.get_abs_offset()
        self.select = 1
        self.select_symbol = self.game_font.render('>', True, WHITE)

        self.resume_text = self.game_font.render('resume', True, WHITE)
        self.resume_button = self.resume_text.get_rect(x=self.pos[0], y=self.pos[1])
        self.resume_button.x += self.boardSurface.get_width() / 2 - self.resume_text.get_width() / 2
        self.resume_button.y += self.TILE * 8 + self.TILE * 0.15

        self.newgame_text = self.game_font.render('new game', True, WHITE)
        self.newgame_button = self.newgame_text.get_rect(x=self.pos[0], y=self.pos[1])
        self.newgame_button.x += self.boardSurface.get_width() / 2 - self.newgame_text.get_width() / 2
        self.newgame_button.y += self.TILE * 9 + self.TILE * 0.15

        self.music_text = self.game_font.render('music', True, WHITE)
        self.music_button = self.music_text.get_rect(x=self.pos[0], y=self.pos[1])
        self.music_button.x += self.boardSurface.get_width() / 2 - self.music_text.get_width() / 2
        self.music_button.y += self.TILE * 10 + self.TILE * 0.15

        self.sound_text = self.game_font.render('sound', True, WHITE)
        self.sound_button = self.sound_text.get_rect(x=self.pos[0], y=self.pos[1])
        self.sound_button.x += self.boardSurface.get_width() / 2 - self.sound_text.get_width() / 2
        self.sound_button.y += self.TILE * 11 + self.TILE * 0.15

        self.exit_text = self.game_font.render('exit', True, WHITE)
        self.exit_button = self.exit_text.get_rect(x=self.pos[0], y=self.pos[1])
        self.exit_button.x += self.boardSurface.get_width() / 2 - self.exit_text.get_width() / 2
        self.exit_button.y += self.TILE * 12 + self.TILE * 0.15

        # info
        self.pos_info = self.infoSurface.get_abs_offset()
        self.menu_button = pygame.Rect(self.pos_info[0] + self.TILE / 2, self.pos_info[1] + self.TILE * 19, self.TILE,
                                       self.TILE)
        self.info_button = pygame.Rect(self.pos_info[0] + 2 * self.TILE + self.TILE / 2,
                                       self.pos_info[1] + self.TILE * 19, self.TILE, self.TILE)
        self.info_font = pygame.font.Font(join(resourcePath(), 'PressStart2P-Regular.ttf'), int(self.TILE / 3))
        self.info_text = ['',
                          'TETRIS',
                          '',
                          'Collect as many lines',
                          'of tetramino shapes',
                          'as possible until',
                          'the playing field is full.',
                          '',
                          'Keyboard & Joystick:',
                          '<Left>/<Right> - move',
                          '<Up>/<Joy0> - rotate/select',
                          '<Down> - down/select',
                          '<Space>/<Joy1> - drop',
                          '<Esc>/<Joy2> - menu',
                          '<i>/<Joy3> - info',
                          '<r> - resume',
                          '<n> - new game',
                          '<m> - music',
                          '<s> - sound',
                          '<e> - exit',
                          '',
                          'Touch:',
                          '<Swipe Left/Right> - move',
                          '<Swipe Up> - rotate',
                          '<Swipe Down> - down',
                          '<Long Swipe Down> - drop',
                          '',
                          'Powered by PyGame ;)',
                          '(c) A.V.Bezdolny, 2020',
                          '* ver. 1.0 *']

        # анимация исчезновения линий
        self.anim_lines = False
        self.count_anim_lines = 0

        self.game_over = False
        self.pause = False
        self.info = False

        # музыка
        self.music = True
        pygame.mixer.music.load(join(resourcePath(), 'music.ogg'))
        pygame.mixer.music.play(-1)

        # звуки
        self.sound = True
        self.sound_move = pygame.mixer.Sound(join(resourcePath(), 'move.ogg'))
        self.sound_rotate = pygame.mixer.Sound(join(resourcePath(), 'rotate.ogg'))
        self.sound_line = pygame.mixer.Sound(join(resourcePath(), 'line.ogg'))
        self.sound_level = pygame.mixer.Sound(join(resourcePath(), 'level.ogg'))
        self.sound_pause = pygame.mixer.Sound(join(resourcePath(), 'pause.ogg'))
        self.sound_place = pygame.mixer.Sound(join(resourcePath(), 'place.ogg'))
        self.sound_game_over = pygame.mixer.Sound(join(resourcePath(), 'game_over.ogg'))

        # Initialize the joystick
        pygame.joystick.init()

        # Touch
        self.block = False
        self.block_count = 0

        # Начальное состояние звездного неба
        self.star_list = []
        for i in range(120):
            size = random.randint(4, 12)
            x = random.randint(0, self.windowSurface.get_width() - size)
            y = random.randint(0, self.windowSurface.get_height() - size)
            self.star_list.append([x, y, size])

        self.dx = 0
        self.dy = 0
        self.rotate = False
        
        # load data
        try:
            with open(join(expanduser('~'), 'pygame_tetris.dat'), 'rb') as f:  # заменить путь на 'pygame_tetris.dat' для android
                data = pickle.load(f)
                self.best = data['best']
                self.score = data['score']
                self.level = data['level']
                self.game_over = data['game_over']
                self.anim_speed = data['anim_speed']
                self.sound = data['sound']
                self.music = data['music']
                if not self.music: pygame.mixer.music.pause()
                self.color = data['color']
                self.next_color = data['next_color']
                self.figure = data['figure']
                self.next_figure = data['next_figure']
                self.field = data['field']
                self.pause = True
        except:  # FileNotFoundError and other
            pass

    def save_data(self):
        with open(join(expanduser('~'), 'pygame_tetris.dat'), 'wb') as f:  # заменить путь на 'pygame_tetris.dat' для android
            data = {
                'best' : self.best,
                'score' : self.score,
                'level' : self.level,
                'game_over' : self.game_over,
                'anim_speed' : self.anim_speed,
                'sound' : self.sound,
                'music' : self.music,
                'color' : self.color,
                'next_color' : self.next_color,
                'figure' : self.figure,
                'next_figure' : self.next_figure,
                'field' : self.field
            }
            pickle.dump(data, f)
    
    def new_game(self):
        self.select = 2
        self.figure, self.next_figure = deepcopy(random.choice(self.figures)), deepcopy(random.choice(self.figures))
        self.color, self.next_color = self.random_color(), self.random_color()
        self.field = [[0 for i in range(10)] for j in range(20)]
        self.anim_count, self.anim_speed, self.anim_limit = 0, 1, FPS
        self.anim_lines = False
        self.count_anim_lines = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        self.pause = False
        self.info = False

    def exit(self):
        self.save_data()
        pygame.quit()
        sys.exit(0)

    def key_left(self):
        self.dx = -1
        self.left = True
        self.count_frame = 0

    def key_right(self):
        self.dx = 1
        self.right = True
        self.count_frame = 0

    def key_up(self):
        if self.pause:
            self.select -= 1
            if self.select < 1: self.select = 5
        else:
            self.rotate = True
            self.up = True
            self.count_frame = 0

    def key_down(self):
        if self.pause:
            self.select += 1
            if self.select > 5: self.select = 1
        else:
            self.dy = 1
            self.down = True
            self.count_frame = 0
            if self.sound: self.sound_move.play()

    def drop(self):
        self.anim_limit = 3

    def set_music(self):
        self.music = False if self.music else True
        if self.music: pygame.mixer.music.unpause()
        if not self.music: pygame.mixer.music.pause()

    def set_sound(self):
        self.sound = False if self.sound else True

    def get_pause(self):
        self.info = False
        self.pause = False if self.pause else True
        self.select = 1
        self.anim_limit = FPS
        if self.sound: self.sound_pause.play()
        self.save_data()
        return True

    def get_info(self):
        self.pause = False
        self.info = False if self.info else True
        self.anim_limit = FPS
        if self.sound: self.sound_pause.play()

    def resume(self):
        self.pause = False
        self.info = False

    def activate_menu_item(self):
        if self.select == 1:
            self.resume()
        elif self.select == 2:
            self.new_game()
        elif self.select == 3:
            self.set_music()
        elif self.select == 4:
            self.set_sound()
        elif self.select == 5:
            self.exit()

    def run(self):
        """Run the main event loop"""
        while True:
            self.dx = 0
            self.dy = 0
            self.rotate = False

            # "горячее" подключение джойстика
            try:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
            except:
                joystick = None

            # События
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                # keyboard
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.key_left()
                    if event.key == pygame.K_RIGHT:
                        self.key_right()
                    if event.key == pygame.K_DOWN:
                        self.key_down()
                    if event.key == pygame.K_UP:
                        self.key_up()
                    if event.key == pygame.K_SPACE:
                        self.drop()
                    if event.key == pygame.K_m:
                        self.set_music()
                    if event.key == pygame.K_s:
                        self.set_sound()
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_AC_BACK:  # android back_button
                        self.get_pause()
                    if event.key == pygame.K_i:
                        self.get_info()
                    if event.key == pygame.K_r and (self.pause or self.info):
                        self.resume()
                    if event.key == pygame.K_e:
                        self.exit()
                    if event.key == pygame.K_n:
                        self.new_game()
                    if event.key == pygame.K_RETURN and self.pause:
                        self.activate_menu_item()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.left = False
                    if event.key == pygame.K_RIGHT:
                        self.right = False
                    if event.key == pygame.K_DOWN:
                        self.down = False
                    if event.key == pygame.K_UP:
                        self.up = False

                # joystick hat
                if event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 0):  # Нейтралка ;)
                        if self.left or self.right or self.down:
                            self.left, self.right, self.down = False, False, False
                        elif self.up:
                            self.up = False
                    elif event.value == (-1, 0):  # LEFT
                        self.key_left()
                    elif event.value == (1, 0):  # RIGHT
                        self.key_right()
                    elif event.value == (0, -1):  # DOWN
                        self.key_down()
                    elif event.value == (0, 1):  # UP
                        self.key_up()

                # joystick buttons
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A
                        # menu actions
                        if self.pause:
                            self.activate_menu_item()
                        # rotate
                        else:
                            self.key_up()
                    if event.button == 1:  # B
                        # drop
                        self.drop()
                    if event.button == 2:  # X
                        # menu
                        self.get_pause()
                    if event.button == 3:  # Y
                        # info
                        self.get_info()

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:  # A
                        self.up = False

                # mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos  # get mouse position
                    if self.resume_button.collidepoint(mouse_pos) and self.pause:
                        self.select = 1
                        self.resume()
                    elif self.newgame_button.collidepoint(mouse_pos) and self.pause:
                        self.select = 2
                        self.new_game()
                    elif self.music_button.collidepoint(mouse_pos) and self.pause:
                        self.select = 3
                        self.set_music()
                    elif self.sound_button.collidepoint(mouse_pos) and self.pause:
                        self.select = 4
                        self.set_sound()
                    elif self.exit_button.collidepoint(mouse_pos) and self.pause:
                        self.select = 5
                        self.exit()
                    # info board
                    elif self.menu_button.collidepoint(mouse_pos):
                        self.get_pause()
                    elif self.info_button.collidepoint(mouse_pos):
                        self.get_info()

                # touch
                if event.type == FINGERMOTION and event.finger_id == 0 and not self.block:
                    touch_dx = event.dx * self.windowSurface.get_width()
                    touch_dy = event.dy * self.windowSurface.get_height()
                    if abs(touch_dx) > self.TILE / 10 or abs(touch_dy) > self.TILE / 10:
                        # horizontal
                        if abs(touch_dx) >= abs(touch_dy):
                            if touch_dx < 0:
                                self.dx = -1  # left
                            elif touch_dx > 0:
                                self.dx = 1  # right
                        # vertical
                        else:
                            if touch_dy < 0:
                                self.rotate = True  # up
                            elif touch_dy > 0:
                                if abs(touch_dy) > self.TILE:
                                    self.drop()
                                else:
                                    self.dy = 1  # down
                                    if self.sound: self.sound_move.play()
                        self.block = True

                # window
                if event.type == WINDOWFOCUSLOST:
                    self.get_pause()

            # Графика
            self.windowSurface.fill(BLACK)

            # Нанесение на поверхность белых прямоугольников - снега ;)
            for star in self.star_list:
                star[1] += star[2] / 4  # скорость

                if star[1] > self.windowSurface.get_height() + star[2]:
                    star[2] = random.randint(4, 12)
                    star[0] = random.randint(0, self.windowSurface.get_width() - star[2])
                    star[1] = -star[2]

                pygame.draw.rect(self.windowSurface, LIGHT, (star[0], star[1], star[2], star[2]))

            # draw grid
            [pygame.draw.rect(self.boardSurface, GREY, i_rect, 1) for i_rect in self.grid]

            # зажатие клавиши управления
            if self.left or self.right or self.down or self.up:
                self.count_frame += 1
                if self.count_frame > 9:
                    self.count_frame = 0
                    if self.left:
                        self.dx = -1
                    if self.right:
                        self.dx = 1
                    if self.down:
                        self.dy = 1
                        if self.sound: self.sound_move.play()
                    if self.up:
                        self.rotate = True

            # touch
            if self.block:
                self.block_count += 1
                if self.block_count > 6:
                    self.block_count = 0
                    self.block = False

            # move x
            if self.dx != 0 and not self.anim_lines and not self.game_over and not self.pause and not self.info:
                if self.sound: self.sound_move.play()
                figure_old = deepcopy(self.figure)
                for i in range(4):
                    self.figure[i].x += self.dx
                    if self.figure[i].x < 0 or self.figure[i].x > 9 or self.field[self.figure[i].y][self.figure[i].x]:
                        self.figure = deepcopy(figure_old)
                        break

            # rotate
            if self.rotate and not self.anim_lines and not self.game_over and not self.pause and not self.info:
                if self.sound: self.sound_rotate.play()
                figure_old = deepcopy(self.figure)

                # квадрат не вращать !!!
                matrix = [[self.figure[j].x, self.figure[j].y] for j in range(4)]
                max_x = max([m[0] for m in matrix])
                min_x = min([m[0] for m in matrix])
                max_y = max([m[1] for m in matrix])
                min_y = min([m[1] for m in matrix])
                rez = max_x - min_x, max_y - min_y

                if not (rez[0] == 1 and rez[1] == 1):
                    # вращение
                    center = self.figure[0]
                    for i in range(4):
                        x = self.figure[i].y - center.y
                        y = self.figure[i].x - center.x
                        self.figure[i].x = center.x - x
                        self.figure[i].y = center.y + y

                    # проверка выхода за границы или пересечения
                    coord = [[self.figure[j].x, self.figure[j].y, 0] for j in range(4)]

                    min_x = min([m[0] for m in coord])
                    if min_x < 0:
                        for a in range(4):
                            coord[a][0] += abs(min_x)

                    max_x = max([m[0] for m in coord])
                    if max_x > 9:
                        for a in range(4):
                            coord[a][0] -= abs(max_x - 9)

                    max_y = max([m[1] for m in coord])
                    if max_y > 19:
                        for a in range(4):
                            coord[a][1] -= abs(max_y - 19)

                    for a in range(4):
                        coord[a][2] = (1 if self.field[coord[a][1]][coord[a][0]] else 0) if (
                                0 <= coord[a][1] <= 19 and 0 <= coord[a][0] <= 9) else 0

                    if 1 not in (c[2] for c in coord):
                        for i in range(4):
                            self.figure[i].x = coord[i][0]
                            self.figure[i].y = coord[i][1]
                    else:
                        # проверка по горизонтали
                        max_x = max([X[0] for X in coord])
                        min_x = min([X[0] for X in coord])
                        max_zx = max([Z[0] for Z in coord if Z[2] == 1])
                        max_zy = max([Z[1] for Z in coord if Z[2] == 1])

                        if max_zx > min_x and not self.field[max_zy][max_zx - 1]:
                            # двигаем влево
                            for i in range(4):
                                coord[i][0] -= abs(max_x - max_zx + 1)
                        elif max_zx < max_x and not self.field[max_zy][max_zx + 1]:
                            # двигаем вправо
                            for i in range(4):
                                coord[i][0] += abs(max_zx - min_x + 1)

                        # проверка по вертикали
                        max_y = max([Y[1] for Y in coord])
                        min_y = min([Y[1] for Y in coord])
                        max_zx = max([Z[0] for Z in coord if Z[2] == 1])
                        max_zy = max([Z[1] for Z in coord if Z[2] == 1])

                        if max_zy > min_y and not self.field[max_zy - 1][max_zx]:
                            # двигаем вверх
                            for i in range(4):
                                coord[i][1] -= abs(max_y - max_zy + 1)
                        elif max_zy < max_y and not self.field[max_zy + 1][max_zx]:
                            # двигаем вниз
                            for i in range(4):
                                coord[i][1] += abs(max_zy - min_y + 1)

                        for a in range(4):
                            coord[a][2] = (1 if self.field[coord[a][1]][coord[a][0]] else 0) if (
                                    0 <= coord[a][1] <= 19 and 0 <= coord[a][0] <= 9) else 0

                        if 1 not in (c[2] for c in coord):
                            for i in range(4):
                                self.figure[i].x = coord[i][0]
                                self.figure[i].y = coord[i][1]
                                if not (0 <= coord[i][1] <= 19 and 0 <= coord[i][0] <= 9):
                                    self.figure = deepcopy(figure_old)
                                    break
                        else:
                            self.figure = deepcopy(figure_old)
            # move y
            if not self.anim_lines and not self.game_over and not self.pause and not self.info:
                self.anim_count += self.anim_speed
                if self.anim_count >= self.anim_limit or self.dy > 0:
                    self.anim_count = 0
                    figure_old = deepcopy(self.figure)
                    for i in range(4):
                        self.figure[i].y += 1
                        if self.figure[i].y > 19 or self.field[self.figure[i].y][self.figure[i].x]:
                            for j in range(4):
                                # noinspection PyTypeChecker
                                self.field[figure_old[j].y][figure_old[j].x] = self.color
                            self.figure, self.color = self.next_figure, self.next_color
                            self.next_figure, self.next_color = deepcopy(random.choice(self.figures)), self.random_color()
                            self.anim_limit = FPS

                            if self.sound: self.sound_place.play()

                            # check game_over
                            for t in range(4):
                                if self.field[self.figure[t].y][self.figure[t].x]:
                                    self.game_over = True
                                    if self.sound: self.sound_game_over.play()

                                    # anim game_over
                                    for i_rect in self.grid:
                                        pygame.draw.rect(self.boardSurface, self.random_color(), i_rect)
                                        pygame.display.flip()
                                        self.clock.tick(150)
                                    break
                            break

            # check anim_lines
            if not self.game_over and not self.pause and not self.info:
                for row in range(19, -1, -1):
                    count = 0
                    for i in range(10):
                        if self.field[row][i]:
                            count += 1
                    if count == 10:
                        for j in range(10):
                            # noinspection PyTypeChecker
                            self.field[row][j] = WHITE
                        self.anim_lines = True

            line, lines = 19, 0
            if self.anim_lines:
                self.count_anim_lines += 1
                if self.count_anim_lines == 10:
                    self.count_anim_lines = 0
                    self.anim_lines = False

                    # check lines
                    for row in range(19, -1, -1):
                        count = 0
                        for i in range(10):
                            if self.field[row][i]:
                                count += 1
                            self.field[line][i] = self.field[row][i]
                        if count < 10:
                            line -= 1
                        else:
                            lines += 1

            # score
            old_score = self.score
            self.score += lines
            if lines != 0:
                if self.sound: self.sound_line.play()
                if self.score > self.best: self.best = self.score

                next_level = False
                s = ((i + 1) * 10 for i in range(100))
                for e in s:
                    if self.score >= e > old_score:
                        next_level = True
                        break

                if next_level:
                    self.anim_speed += 0.5
                    self.level += 1
                    if self.sound: self.sound_level.play()

            # draw figure
            for i in range(4):
                self.figure_rect.x = self.figure[i].x * self.TILE
                self.figure_rect.y = self.figure[i].y * self.TILE
                pygame.draw.rect(self.boardSurface, self.color, self.figure_rect)

            # draw field
            for y, raw in enumerate(self.field):
                for x, col in enumerate(raw):
                    if col:
                        self.figure_rect.x, self.figure_rect.y = x * self.TILE, y * self.TILE
                        pygame.draw.rect(self.boardSurface, col, self.figure_rect)

            # draw info
            self.infoSurface.blit(self.next_text, (self.infoSurface.get_width() / 2 - self.next_text.get_width() / 2, 0))
            self.infoSurface.blit(self.best_text, (self.infoSurface.get_width() / 2 - self.best_text.get_width() / 2, self.TILE * 6))
            best_value = self.game_font.render(str(self.best), True, WHITE)
            self.infoSurface.blit(best_value, (self.infoSurface.get_width() / 2 - best_value.get_width() / 2, self.TILE * 7))
            self.infoSurface.blit(self.lines_text, (self.infoSurface.get_width() / 2 - self.lines_text.get_width() / 2, self.TILE * 9))
            lines_value = self.game_font.render(str(self.score), True, WHITE)
            self.infoSurface.blit(lines_value, (self.infoSurface.get_width() / 2 - lines_value.get_width() / 2, self.TILE * 10))
            self.infoSurface.blit(self.level_text, (self.infoSurface.get_width() / 2 - self.level_text.get_width() / 2, self.TILE * 12))
            level_value = self.game_font.render(str(self.level), True, WHITE)
            self.infoSurface.blit(level_value, (self.infoSurface.get_width() / 2 - level_value.get_width() / 2, self.TILE * 13))

            # draw button's
            # menu button
            pygame.draw.rect(self.infoSurface, WHITE, (self.TILE / 2, self.TILE * 19, self.TILE, self.TILE / 5))
            pygame.draw.rect(self.infoSurface, WHITE, (self.TILE / 2, self.TILE * 19 + 2 * self.TILE / 5, self.TILE, self.TILE / 5))
            pygame.draw.rect(self.infoSurface, WHITE, (self.TILE / 2, self.TILE * 19 + 4 * self.TILE / 5, self.TILE, self.TILE / 5))
            # info button
            pygame.draw.rect(self.infoSurface, WHITE, (3 * self.TILE - self.TILE / 5, self.TILE * 19, 2 * self.TILE / 5, self.TILE / 5))
            pygame.draw.rect(self.infoSurface, WHITE,
                             (3 * self.TILE - 2 * self.TILE / 5, self.TILE * 19 + 2 * self.TILE / 5, 2 * self.TILE / 5, self.TILE / 5 / 2))
            pygame.draw.rect(self.infoSurface, WHITE,
                             (3 * self.TILE - self.TILE / 5, self.TILE * 19 + 2 * self.TILE / 5, 2 * self.TILE / 5, 3 * self.TILE / 5))
            pygame.draw.rect(self.infoSurface, WHITE,
                             (2 * self.TILE + self.TILE / 2, self.TILE * 19 + self.TILE - self.TILE / 5 / 2, self.TILE, self.TILE / 5 / 2))

            # draw next figure
            for i in range(4):
                self.figure_rect.x = self.next_figure[i].x * self.TILE - self.TILE * 3
                self.figure_rect.y = self.next_figure[i].y * self.TILE + self.TILE
                pygame.draw.rect(self.infoSurface, self.next_color, self.figure_rect)

            if self.game_over:
                pygame.draw.rect(self.boardSurface, BLACK, (1, self.TILE * 9, self.TILE * 10 - 2, self.TILE * 3))
                self.boardSurface.blit(self.gameover_text,
                                       (self.boardSurface.get_width() / 2 - self.gameover_text.get_width() / 2,
                                        self.TILE * 10 + self.TILE * 0.15))

            if self.info:
                pygame.draw.rect(self.boardSurface, BLACK, (1, self.TILE * 2, self.TILE * 10 - 2, self.TILE * 16))
                for i, row in enumerate(self.info_text):
                    info_render = self.info_font.render(row, True, WHITE)
                    self.boardSurface.blit(info_render, (self.boardSurface.get_width() / 2 - info_render.get_width() / 2,
                                                         self.TILE * 2 + info_render.get_height() * (i + 1) * 1.5))

            if self.pause:
                pygame.draw.rect(self.boardSurface, BLACK, (1, self.TILE * 7, self.TILE * 10 - 2, self.TILE * 7))
                self.boardSurface.blit(self.select_symbol, (self.TILE, self.TILE * (7 + self.select) + self.TILE * 0.15))
                self.boardSurface.blit(self.resume_text,
                                       (self.boardSurface.get_width() / 2 - self.resume_text.get_width() / 2, self.TILE * 8 + self.TILE * 0.15))
                self.boardSurface.blit(self.newgame_text,
                                       (self.boardSurface.get_width() / 2 - self.newgame_text.get_width() / 2, self.TILE * 9 + self.TILE * 0.15))
                self.boardSurface.blit(self.music_text,
                                       (self.boardSurface.get_width() / 2 - self.music_text.get_width() / 2, self.TILE * 10 + self.TILE * 0.15))
                self.boardSurface.blit(self.sound_text,
                                       (self.boardSurface.get_width() / 2 - self.sound_text.get_width() / 2, self.TILE * 11 + self.TILE * 0.15))
                self.boardSurface.blit(self.exit_text,
                                       (self.boardSurface.get_width() / 2 - self.exit_text.get_width() / 2, self.TILE * 12 + self.TILE * 0.15))

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    Game().run()
