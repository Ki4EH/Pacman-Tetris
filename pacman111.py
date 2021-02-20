import pygame
import pygame_gui
import sqlite3
import os
import sys
import random
import openpyxl


pygame.init()
# музыка
enter_sound = pygame.mixer.Sound('pacman_pics_n_fields/japan88 фонмуз для входа.mp3')
mainmenu_sound = pygame.mixer.Sound('pacman_pics_n_fields/bank account фонмуз для главменю.mp3')
pacman_screen_sound = pygame.mixer.Sound('pacman_pics_n_fields/пакман заставка музыка.mp3')
pacman_game_sound = pygame.mixer.Sound('pacman_pics_n_fields/пакман игра музыка.mp3')
tetris_game_sound = pygame.mixer.Sound('pacman_pics_n_fields/тетрис музыка.mp3')

width, height = 800, 700
size = width, height
FPS = 60
# те или иные проверки и списки для игры
ENEMY_EVENT_TYPE = 30
PACMAN_EATING = False
ATE_GHOSTS_NUM = []
GHOSTS_COLORS = []
pac_eat_prov = 0
# очки текущей игры пакман
this_game_points = 0
# переменные для базы данных
pmg_factor = 0
pidentification = 0
btp = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
win = pygame.display.set_mode(size)


# ==========================================ПАКМАН=============================================

# закрытие игры
def terminate():
    pygame.quit()
    sys.exit()


# загрузка изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('pacman_pics_n_fields', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# загрузка уровней
def load_level(filename):
    filename = "pacman_pics_n_fields/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# вход или регистрация.
def enter_screen():
    enter = pygame.display.set_mode(size)
    running = True
    fon = pygame.transform.scale(load_image('вход.jpg'), (width, height))
    enter.blit(fon, (0, 0))
    manager = pygame_gui.UIManager((800, 700))
    regbutton = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((475, 25), (300, 150)),
        text='РЕГИСТРАЦИЯ',
        manager=manager)
    enterbutton = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((475, 200), (300, 150)),
        text='ВХОД В ИГРУ',
        manager=manager)
    while running:
        manager.update(clock.tick(50))
        manager.draw_ui(enter)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == regbutton:
                        enterbutton.kill()
                        regbutton.kill()
                        conect_to_bd(True)
                    if event.ui_element == enterbutton:
                        enterbutton.kill()
                        regbutton.kill()
                        conect_to_bd(False)
            manager.process_events(event)
        pygame.display.flip()


# связываем с базой данных
def conect_to_bd(reg_or_enter):
    enter = pygame.display.set_mode(size)
    running = True
    nn_txt = None
    pw_txt = None
    fon = pygame.transform.scale(load_image('связь с бд.jpg'), (width, height))
    enter.blit(fon, (0, 0))
    manager = pygame_gui.UIManager((800, 700))
    nickname = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((475, 175), (300, 500)),
        manager=manager)
    password = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((475, 350), (300, 500)),
        manager=manager)
    while running:
        font1 = pygame.font.SysFont("Times New Roman", 25, bold=True)
        label1 = font1.render("ПОСЛЕ КАЖДОГО ВВОДА НАЖИМАЙТЕ КЛАВИШУ ENTER!!!", 1, (0, 255, 255))
        screen.blit(label1, (15, 20))
        font2 = pygame.font.SysFont("Times New Roman", 70, bold=True)
        label2 = font2.render("ВВЕДИТЕ НИКНЕЙМ:", 1, (0, 255, 255))
        screen.blit(label2, (25, 100))
        font3 = pygame.font.SysFont("Times New Roman", 70, bold=True)
        label3 = font3.render("ВВЕДИТЕ ПАРОЛЬ:", 1, (0, 255, 255))
        screen.blit(label3, (105, 275))
        pygame.display.update()
        manager.update(clock.tick(50))
        manager.draw_ui(enter)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                enter_screen()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.text == '':
                        font4 = pygame.font.SysFont("Times New Roman", 60, bold=True)
                        label4 = font4.render("ПРИДУМАЙТЕ НИКНЕЙМ", 1, (255, 0, 0))
                        label5 = font4.render("И ПАРОЛЬ!!!", 1, (255, 0, 0))
                        screen.blit(label4, (10, 375))
                        screen.blit(label5, (250, 475))
                        pygame.display.update()
                    elif event.ui_element == nickname:
                        nn_txt = event.text
                    elif event.ui_element == password:
                        pw_txt = event.text
                    if nn_txt is not None and pw_txt is not None:
                        global pidentification
                        global pmg_factor
                        global btp
                        cur.execute("SELECT nickname, password FROM information WHERE nickname = ? AND password = ?",
                                    (nn_txt, pw_txt))
                        # регистрация
                        if reg_or_enter:
                            if cur.fetchone() is None:
                                cur.execute(f"INSERT INTO information (nickname, password) VALUES (?, ?)",
                                            (nn_txt, pw_txt))
                                con.commit()
                                pidentification = (cur.execute(
                                    f"SELECT playerid FROM information WHERE nickname = ? AND password = ?",
                                        (nn_txt, pw_txt)).fetchone())[0]
                                cur.execute(f"INSERT INTO pacman_top (playerid, best_game_pacman_time,"
                                            f" best_game_pacman_points, factor) VALUES (?, ?, ?, ?)",
                                            (pidentification, 0, 0, pmg_factor))
                                con.commit()
                                cur.execute(f"INSERT INTO tetris_top (playerid, best_tetris_points) VALUES (?, ?)",
                                            (pidentification, 0))
                                con.commit()
                                # обновление ексель файла с пакман топом
                                update_pacman_top_xl()
                                # обновление ексель файла с тетрис топом
                                update_tetris_top_xl()



                                # создание двух файлов !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



                                start_screen()
                            else:
                                font4 = pygame.font.SysFont("Times New Roman", 40, bold=True)
                                label4 = font4.render("ПРИДУМАЙТЕ ПАЖАЛУЙСТА ДРУГОЙ", 1, (255, 0, 0))
                                label5 = font4.render("ПАРОЛЬ И / ИЛИ НИКНЕЙМ!!!", 1, (255, 0, 0))
                                screen.blit(label4, (10, 550))
                                screen.blit(label5, (125, 600))
                        # вход
                        else:
                            if cur.fetchone() is None:
                                font4 = pygame.font.SysFont("Times New Roman", 47, bold=True)
                                label4 = font4.render("НЕПРАВИЛЬНО ВВЕДЁН ПАРОЛЬ", 1, (255, 0, 0))
                                label5 = font4.render("И / ИЛИ НИКНЕЙМ!!!", 1, (255, 0, 0))
                                screen.blit(label4, (10, 550))
                                screen.blit(label5, (150, 600))
                            else:
                                pidentification = (cur.execute(f"SELECT playerid FROM information WHERE nickname = ?"
                                                               f" AND password = ?", (nn_txt, pw_txt)).fetchone())[0]
                                pmg_factor = cur.execute(f"SELECT factor FROM pacman_top"
                                                         f" WHERE playerid = {pidentification}").fetchone()[0]
                                btp = cur.execute(f"SELECT best_tetris_points FROM tetris_top"
                                                              f" WHERE playerid = {pidentification}").fetchone()[0]
                                start_screen()
            manager.process_events(event)
        pygame.display.flip()


# обновление ексель файла с пакман топом
def update_pacman_top_xl():
    book = openpyxl.load_workbook('pacman_pics_n_fields/топ пакмана.xlsx')
    sheet = book.active

    for i, row in enumerate(cur.execute("SELECT nickname, factor, best_game_pacman_time, best_game_pacman_points"
                                            " FROM pacman_top JOIN information ON"
                                            " pacman_top.playerid = information.playerid").fetchall()):
        for j, col in enumerate(row):
            c = sheet.cell(row=i + 1, column=j + 1)
            c.value = col
    book.save('pacman_pics_n_fields/топ пакмана.xlsx')


# заставка игры. главное меню.
def start_screen():
    global pmg_factor
    global pidentification
    main_menu_screen = pygame.display.set_mode(size)
    enter_sound.stop()
    mainmenu_sound.set_volume(0.15)
    mainmenu_sound.play(-1)
    running = True
    fon = pygame.transform.scale(load_image('заставка.jpg'), (width, height))
    main_menu_screen.blit(fon, (0, 0))
    ptp = cur.execute(f"SELECT topnum FROM pacman_top WHERE playerid = {pidentification}").fetchone()[0]
    ttp = cur.execute(f"SELECT topnum FROM tetris_top WHERE playerid = {pidentification}").fetchone()[0]
    font = pygame.font.SysFont("Times New Roman", 35, bold=True)
    label1 = font.render(f"МЕСТО В ПАКМАН ТОПЕ: {ptp}", 1, (0, 255, 0))
    label2 = font.render(f"МЕСТО В ТЕТРИС ТОПЕ: {ttp}", 1, (0, 255, 0))
    screen.blit(label1, (5, 5))
    screen.blit(label2, (5, 45))
    manager = pygame_gui.UIManager((800, 700))
    pacmanbutton = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((575, 10), (200, 100)),
        text='ПАКМАН',
        manager=manager)
    tetrisbutton = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((575, 125), (200, 100)),
        text='ТЕТРИС',
        manager=manager)
    toppacman = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((575, 240), (200, 100)),
        text='ТОП ПАКМАН',
        manager=manager)
    toptetris = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((575, 355), (200, 100)),
        text='ТОП ТЕТРИС',
        manager=manager)
    gamespacman = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((575, 470), (200, 100)),
        text='ИГРЫ ПАКМАН',
        manager=manager)
    gamestetris = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((575, 585), (200, 100)),
        text='ИГРЫ ТЕТРИС',
        manager=manager)
    while running:
        manager.update(clock.tick(50))
        manager.draw_ui(main_menu_screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == pacmanbutton:
                        tetrisbutton.kill()
                        pacmanbutton.kill()
                        mainmenu_sound.stop()
                        pacman_screen()
                    if event.ui_element == tetrisbutton:
                        tetrisbutton.kill()
                        pacmanbutton.kill()
                        tetris_game_sound.set_volume(0.10)
                        tetris_game_sound.play(-1)
                        mainmenu_sound.stop()
                        main(win)
                    if event.ui_element == toppacman:
                        os.startfile('pacman_pics_n_fields\топ пакмана.xlsx')
                    if event.ui_element == toptetris:
                        os.startfile('pacman_pics_n_fields\топ тетриса.xlsx')
                    if event.ui_element == gamespacman:
                        pass
                    if event.ui_element == gamestetris:
                        pass
            manager.process_events(event)
        pygame.display.flip()


# заставка пакмана.
def pacman_screen():
    pacman_screen = pygame.display.set_mode(size)
    muzprov = 0
    clock = pygame.time.Clock()
    pacman_screen_sound.play()
    running = True
    pmfon = pygame.transform.scale(load_image('заставка пакман.jpg'), (width, height))
    pacman_screen.blit(pmfon, (0, 0))
    manager1 = pygame_gui.UIManager((800, 700))
    propustit = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((200, 500), (400, 150)),
        text='ПРОПУСТИТЬ ЗАСТАВКУ',
        manager=manager1)
    while running:
        manager1.update(clock.tick(50))
        manager1.draw_ui(pacman_screen)
        if 4250 <= muzprov:
            pacman_screen_sound.stop()
            pacman_game()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pacman_screen_sound.stop()
                start_screen()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == propustit:
                        propustit.kill()
                        pacman_screen_sound.stop()
                        pacman_game()
            manager1.process_events(event)
        muzprov += clock.tick(50)
        pygame.display.flip()


# сама игра пакман
def pacman_game():
    generate_level(load_level('level.txt'))
    pacman_game_sound.set_volume(0.05)
    pacman_game_sound.play(-1)
    running = True
    start_game_time = pygame.time.get_ticks()
    prov = pygame.time.get_ticks()
    global pac_eat_prov
    global PACMAN_EATING
    global GHOSTS_COLORS
    global ATE_GHOSTS_NUM
    global pmg_factor
    global pidentification
    global this_game_points
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pacman_game_sound.stop()
                GHOSTS_COLORS = []
                PACMAN_EATING = False
                ATE_GHOSTS_NUM = []
                pac_eat_prov = 0
                player_group.update(True)
                ghosts_group.update(True)
                start_screen()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                player_group.update()
        if pygame.time.get_ticks() - prov > 200:
            prov = pygame.time.get_ticks()
            tiles_group.draw(screen)
            coin_group.draw(screen)
            player_group.draw(screen)
            ghosts_group.draw(screen)
            all_sprites.update()
        if PACMAN_EATING:
            if (pygame.time.get_ticks() - pac_eat_prov) / 1000 > 10:
                for egn in ATE_GHOSTS_NUM:
                    ghosts_group.add(Ghosts(egn, 9, 10))
                i = 0
                for ghosts in ghosts_group:
                    ghosts.image = GHOSTS_COLORS[i]
                    i += 1
                PACMAN_EATING = False
                ATE_GHOSTS_NUM = []
                pac_eat_prov = 0
        if not coin_group:
            # добавление времени и очков игры в табличный файл !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            this_game_time = pygame.time.get_ticks() - start_game_time
            nfactor = this_game_points / this_game_time * 1000000
            font = pygame.font.SysFont("Times New Roman", 75, bold=True)
            label = font.render("ПОБЕДА!!!", 1, (0, 255, 255))
            label1 = font.render(f"коэффициент: {nfactor}", 1, (0, 255, 255))
            label2 = font.render(f"время: {this_game_time} мс", 1, (0, 255, 255))
            label3 = font.render(f"очки: {this_game_points}", 1, (0, 255, 255))
            screen.blit(label, (200, 200))
            screen.blit(label1, (10, 275))
            screen.blit(label2, (10, 350))
            screen.blit(label3, (10, 425))
            pygame.display.update()
            pacman_game_sound.stop()
            pygame.time.delay(3500)
            player_group.update(True)
            ghosts_group.update(True)
            if nfactor >= pmg_factor:
                pmg_factor = nfactor
                cur.execute(f"UPDATE pacman_top SET best_game_pacman_time = {this_game_time},"
                            f" best_game_pacman_points = {this_game_points},"
                            f" factor = {pmg_factor}"
                            f" WHERE playerid = {pidentification}")
                con.commit()
                truetop = cur.execute("SELECT playerid, best_game_pacman_time, best_game_pacman_points, factor"
                                      " FROM pacman_top ORDER BY factor DESC").fetchall()
                cur.execute("DELETE from pacman_top")
                con.commit()
                cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE Name = 'pacman_top'")
                for i in truetop:
                    cur.execute(f"INSERT INTO pacman_top (playerid, best_game_pacman_time, best_game_pacman_points,"
                                f" factor) VALUES (?, ?, ?, ?)", (i[0], i[1], i[2], i[3]))
                con.commit()
                # обновление ексель файла с пакман топом
                update_pacman_top_xl()
            GHOSTS_COLORS = []
            ATE_GHOSTS_NUM = []
            PACMAN_EATING = False
            start_screen()
        pygame.display.flip()
    pygame.quit()


tile_height = height // 22
tile_width = width // 19
tile_images = {
    'wall': load_image('стена.png'),
    'empty': load_image('пол.png')}
coin_images = {
    'small': pygame.transform.scale(load_image("coin.png", -1), (tile_width // 2, tile_height // 2)),
    'big': pygame.transform.scale(load_image("coin.png", -1), (tile_width, tile_height))}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class PacmanAnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.frames = []
        self.cut_sheet(pygame.transform.scale(load_image('pacman2.jpg', -1), (tile_width * 6, tile_height)), 6, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * self.pos_x, tile_height * self.pos_y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self, killing=False):
        # убирание спрайта чтобы при новой игре не было старых данных
        if killing:
            self.kill()

        # следующий шаг пакмана
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]:
            if self.pos_y == 10 and self.pos_x == 18:
                self.pos_x = 0
            elif load_level('level.txt')[self.pos_y][self.pos_x + 1] != '#':
                self.pos_x += 1
        elif pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]:
            if self.pos_y == 10 and self.pos_x == 0:
                self.pos_x = 18
            elif load_level('level.txt')[self.pos_y][self.pos_x - 1] != '#':
                self.pos_x -= 1
        elif (pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]) \
                and load_level('level.txt')[self.pos_y - 1][self.pos_x] != '#':
            self.pos_y -= 1
        elif (pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]) \
                and load_level('level.txt')[self.pos_y + 1][self.pos_x] != '#':
            self.pos_y += 1
        self.rect = self.image.get_rect().move(tile_width * self.pos_x, tile_height * self.pos_y)

        global PACMAN_EATING
        global ATE_GHOSTS_NUM
        global GHOSTS_COLORS
        global pac_eat_prov
        global this_game_points
        # соприкосновение с приведениями
        if pygame.sprite.spritecollideany(self, ghosts_group):
            if PACMAN_EATING:
                for ghost in ghosts_group:
                    if ghost.rect.x == tile_width * self.pos_x and ghost.rect.y == tile_height * self.pos_y:
                        this_game_points += 250
                        ATE_GHOSTS_NUM.append(ghost.image)
                        ghosts_group.remove(ghost)
            else:
                font = pygame.font.SysFont("Times New Roman", 125, bold=True)
                label = font.render("Ты проиграл!", 1, (0, 255, 255))
                screen.blit(label, (10, 250))
                pygame.display.update()
                pacman_game_sound.stop()
                pygame.time.delay(2000)
                player_group.update(True)
                ghosts_group.update(True)
                GHOSTS_COLORS = []
                start_screen()

        # соприкосновение с монетами
        if pygame.sprite.spritecollideany(self, coin_group):
            for coins in coin_group:
                if coins.rect.x == tile_width * self.pos_x + 10 and coins.rect.y == tile_height * self.pos_y + 10:
                    coin_group.remove(coins)
                    this_game_points += 100
                elif coins.rect.x == tile_width * self.pos_x and coins.rect.y == tile_height * self.pos_y:
                    this_game_points += 50
                    for ghosts in ghosts_group:
                        ghosts.image = pygame.transform.scale(load_image("мёртвое приведение.jpg", -1),
                                                              (tile_width, tile_height))
                    coin_group.remove(coins)
                    PACMAN_EATING = True
                    pac_eat_prov = pygame.time.get_ticks()


class Coin(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(coin_group, all_sprites)
        self.image = coin_images[tile_type]
        self.pos_x = pos_x
        self.pos_y = pos_y
        if tile_type == 'small':
            self.rect = self.image.get_rect().move(tile_width * self.pos_x + 10, tile_height * self.pos_y + 10)
        elif tile_type == 'big':
            self.rect = self.image.get_rect().move(tile_width * self.pos_x, tile_height * self.pos_y)


class Ghosts(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        super().__init__(ghosts_group, all_sprites)
        self.image = image
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(tile_width * self.pos_x, tile_height * self.pos_y)

    def update(self, killing=False):
        if killing:
            self.kill()
        actions = ['self.pos_x += 1', 'self.pos_x -= 1', 'self.pos_y -= 1', 'self.pos_y += 1']
        action = random.choice(actions)
        if action == 'self.pos_x += 1':
            if self.pos_y == 10 and self.pos_x == 18:
                self.pos_x = 0
            elif load_level('level.txt')[self.pos_y][self.pos_x + 1] != '#':
                self.pos_x += 1
        elif action == 'self.pos_x -= 1':
            if self.pos_y == 10 and self.pos_x == 0:
                self.pos_x = 18
            elif load_level('level.txt')[self.pos_y][self.pos_x - 1] != '#':
                self.pos_x -= 1
        elif action == 'self.pos_y += 1' and load_level('level.txt')[self.pos_y - 1][self.pos_x] != '#':
            self.pos_y -= 1
        elif action == 'self.pos_y -= 1' and load_level('level.txt')[self.pos_y + 1][self.pos_x] != '#':
            self.pos_y += 1
        self.rect = self.image.get_rect().move(tile_width * self.pos_x, tile_height * self.pos_y)


# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
ghosts_group = pygame.sprite.Group()


def generate_level(level):
    global GHOSTS_COLORS
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '/':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                PacmanAnimatedSprite(x, y)
            elif level[y][x] == '.':
                Tile('empty', x, y)
                Coin('small', x, y)
            elif level[y][x] == '0':
                Tile('empty', x, y)
                Coin('big', x, y)
            elif level[y][x] == '+':
                Tile('empty', x, y)
                yg = pygame.transform.scale(load_image("жёлтое приведение.jpg", -1), (tile_width, tile_height))
                rg = pygame.transform.scale(load_image("красное приведение.jpg", -1), (tile_width, tile_height))
                pg = pygame.transform.scale(load_image("розовое приведение.jpg", -1), (tile_width, tile_height))
                bg = pygame.transform.scale(load_image("синее приведение.jpg", -1), (tile_width, tile_height))
                colors = [yg, rg, pg, bg, yg, rg, pg, bg]
                for cs in colors:
                    GHOSTS_COLORS.append(cs)
                    ghosts_group.add(Ghosts(cs, x, y))





















#создание базы данных
con = sqlite3.connect("pacman-and-tetris-info.db")
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS information (
    playerid INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT,
    password TEXT
)""")
con.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS pacman_top (
    topnum                   INTEGER PRIMARY KEY AUTOINCREMENT,
    playerid                 INTEGER REFERENCES information (playerid), 
    best_game_pacman_time    REAL,
    best_game_pacman_points  INTEGER,
    factor                   REAL
)""")
con.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS tetris_top (
    topnum                   INTEGER PRIMARY KEY AUTOINCREMENT,
    playerid                 INTEGER REFERENCES information (playerid),
    best_tetris_points       INTEGER
)""")
con.commit()
enter_sound.set_volume(0.05)
enter_sound.play(-1)
enter_screen()