import sys
import pygame
import random
import pymysql

# путь к файлам на любой ос
from os import path

img_dir = path.join(path.dirname(__file__), 'IMG')
snd_dir = path.join(path.dirname(__file__), 'SND')

#  Стандартные параметры игры ( ширина, высота, кадры )
WIDTH = 480
HEIGHT = 600
FPS = 60

POWERUP_TIME = 4000
meteor_speed1 = 1
meteor_speed2 = 6
fake_score = 1000

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SILVER = (192, 192, 192)

# Создание игры и окна
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кораблик")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')  # Шрифт


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_hp(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, int(fill), bar_height)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for live in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * live
        img_rect.y = y
        surf.blit(img, img_rect)


def new_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "В рамках этой увлекательной игры жанра Shoot 'em up (shmup)"
              , 18, int(WIDTH / 2), int(HEIGHT * 3 / 4))
    draw_text(screen, "Вы погрузитесь в потрясающую атмосферу космоса и станете"
              , 18, int(WIDTH / 2), int(HEIGHT * 3 / 4) + 25)
    draw_text(screen, "капитаном космического корабля, в задачу которого входит", 18, int(WIDTH / 2),
              int(HEIGHT * 3 / 4) + 50)
    draw_text(screen, "уничтожение многочисленных метеоритов!", 18, int(WIDTH / 2),
              int(HEIGHT * 3 / 4) + 75)
    for i in range(len(menu_items)):  # goes through each item
        make_button(screen, SILVER, BLACK, 120, 100 + (100 * i), int(WIDTH / 2), 60, menu_items[i])

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == 5:
                if event.button == 1:
                    for i in range(len(menu_items)):  # check every button
                        if button_check(event.pos, 120, 100 + (100 * i), int(WIDTH / 2), 60):
                            if i == 0:
                                return
                            elif i == 1:
                                show_leaderboard()
                                show_go_screen()
                                return
                            elif i == 2:
                                pygame.quit()
                                sys.exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def show_leaderboard():
    leader = ['some', 'problems', 'with', 'database', 'connection']
    con = pymysql.connect('localhost', 'root', 'toor', 'pygame')

    cursor = con.cursor()
    cursor.execute("SELECT * FROM leaderboard ORDER BY score DESC LIMIT 0,5")
    lbs = cursor.fetchall()
    if lbs:
        leader = []
        i = 1
        for lb in lbs:
            leader.append("Player " + str(i) + ":  " + str(lb[1]))
            i += 1

    screen.blit(background, background_rect)

    draw_text(screen, "Best scores:", 45, int(WIDTH / 2), 30)

    for j in range(len(leader)):  # goes through each item
        # make_button(screen, SILVER, BLACK, 120, 30 + (100 * j), int(WIDTH / 2), 60, leader[j])
        draw_text(screen, leader[j], 35, int(WIDTH / 2) - 80, 130 + (70 * j))

    make_button(screen, SILVER, BLACK, 120, 20 + (100 * (len(leader))), int(WIDTH / 2), 60, "Back")
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == 5:
                if event.button == 1:
                    if button_check(event.pos, 120, 10 + (100 * (len(leader))), int(WIDTH / 2), 60):
                        return

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def button_check(pos, x, y, x1, y1):
    return x <= pos[0] < x + x1 and y <= pos[1] < y + y1


def make_button(surface, color, text_color, x, y, width, height, text):
    pygame.draw.rect(surface, (0, 0, 0), (x - 1, y - 1, width + 3, height + 3), 1)  # makes outline around the box
    pygame.draw.rect(surface, color, (x, y, width, height))  # makes the box

    myfont = pygame.font.SysFont('Arial Black', 30)  # creates the font, size 15 (you can change this)
    label = myfont.render(text, 1, text_color)  # creates the label
    surface.blit(label, (x + 2, y))  # renders the label


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # инициализация встроенных классов Спрайт
        self.image = pygame.transform.scale(player_img, (65, 50))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = int(WIDTH / 2)
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.hp = 100
        self.shoot_delay = 750  # Время между появлением пуль
        self.last_shoot = pygame.time.get_ticks()
        self.lives = 3
        self.invisible = False
        self.invisible_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # тайм - аут для бонусов
        if self.power == 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power = 1
            self.power_time = pygame.time.get_ticks()

        # Вернуть игрока
        if self.invisible and pygame.time.get_ticks() - self.invisible_timer > 1100:
            self.invisible = False
            self.rect.centerx = int(WIDTH / 2)
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0

        key_press = pygame.key.get_pressed()  # Получение библиотеки True/False
        if key_press[pygame.K_LEFT]:
            self.speedx = -8
        if key_press[pygame.K_RIGHT]:
            self.speedx = 8
        if key_press[pygame.K_SPACE]:
            self.shoot()

        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power = 2
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    # Скрыть игрока
    def invis(self):
        self.invisible = True
        self.invisible_timer = pygame.time.get_ticks()
        self.rect.center = (int(WIDTH / 2), HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # print(self.radius)
        # if self.radius < 15:
        # self.hp = 0.75
        # elif 15 < self.radius < 36:
        # self.hp = 1
        # else:
        # self.hp = 1.5
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-110, -40)
        self.speedy = random.randrange(meteor_speed1, meteor_speed2)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0  # Свойство вращения
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  # Контроль скорости анимации

    # Вращение мобов
    def rotate(self):
        now = pygame.time.get_ticks()  # Текущее время
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)  # Смещение центра
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 15 or self.rect.left < -15 or self.rect.right > WIDTH + 15:
            self.speedx *= random.uniform(-1.01, -1.05)
        if self.rect.bottom > HEIGHT + 110:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-110, -40)
            self.speedy = random.randrange(meteor_speed1, meteor_speed2)
            self.speedx = random.randrange(-3, 3)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = - 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Exp(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = exp_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
        if self.frame == len(exp_anim[self.size]):
            self.kill()
        else:
            center = self.rect.center
            self.image = exp_anim[self.size][self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = center


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['hp', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # Выход за карту - смерть
        if self.rect.top > HEIGHT:
            self.kill()


# Графика
background = pygame.image.load(path.join(img_dir, 'background.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, 'player.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laser.png')).convert()
meteor_images = []
meteor_list = ['meteor_big1.png', 'meteor_big2.png', 'meteor_big3.png', 'meteor_big4.png', 'meteor_med1.png',
               'meteor_med2.png', 'meteor_small1.png', 'meteor_small2.png', 'meteor_tiny1.png', 'meteor_tiny2.png']

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

exp_anim = {}
exp_anim['lg'] = []  # Взрыв метеоритов от пуль
exp_anim['sm'] = []  # Взрыв от игрока
exp_anim['player'] = []

for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    exp_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    exp_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    exp_anim['player'].append(img)

powerup_images = {}
powerup_images['hp'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

# Музыка и звуковые эффекты
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
player_rip_sound = pygame.mixer.Sound(path.join(snd_dir, 'player_rip.wav'))
hp_sound = pygame.mixer.Sound(path.join(snd_dir, '2hp.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, '2power.wav'))
expl_sounds = []
for snd in ['explode_meteor1.wav', 'explode_meteor2.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
pygame.mixer.music.load(path.join(snd_dir, 'bg.ogg'))
pygame.mixer.music.set_volume(0.20)
pygame.mixer.music.play(loops=-1)

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
player = Player()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
all_sprites.add(player)
for i in range(8):
    new_mob()
score = 0

# Цикл игры
game_over = True
running = True
menu_items = ['Play', 'Leaderboard', 'Exit']

while running:

    if game_over:
        score = 0
        meteor_speed1 = 1
        meteor_speed2 = 6
        fake_score = 1000
        player.shoot_delay = 750
        show_go_screen()
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        player = Player()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        all_sprites.add(player)
        for i in range(8):
            new_mob()
        game_over = False

    # Держим цикл на правильной скорости
    clock.tick(FPS)

    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    all_sprites.update()

    # Сложность ХАРД
    if score > fake_score:
        meteor_speed1 += 1
        meteor_speed2 += 1
        fake_score += 1000
        player.shoot_delay -= 50
        if player.shoot_delay <= 300:
            player.shoot_delay = 300

    # Проверка столкновения игрока c мобом(проверяемый спрайт, группа для сравнения, удаляется ли обьект?) + тип столкн
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)  # Возвращает список справйтов
    for hit in hits:
        player.hp -= hit.radius * 2
        exp = Exp(hit.rect.center, 'sm')
        all_sprites.add(exp)
        new_mob()

        if player.hp <= 0:
            player_rip_sound.play()

            death_exp = Exp(player.rect.center, 'player')
            all_sprites.add(death_exp)
            player.invis()
            player.lives -= 1
            player.hp = 100
    # for i in mobs:
    # print(mobs.hp)
    # Проверка на столкновение пуль с мобом
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:  # Не дать мобам закончится
        # mobs.hp -= 1

        # if mobs.hp < 0:
        score += 60 - hit.radius
        random.choice(expl_sounds).play()
        exp = Exp(hit.rect.center, 'lg')
        all_sprites.add(exp)
        if random.random() > 0.92:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        new_mob()

    # Проверка на столкновение игрока с улучшениями
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'hp':
            hp_sound.play()
            player.hp += random.randrange(10, 30)
            if player.hp >= 100:
                player.hp = 100
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    if player.lives == 0 and not death_exp.alive():
        con = pymysql.connect('localhost', 'root', 'toor', 'pygame', autocommit=True)

        cursor = con.cursor()
        cursor.execute("INSERT INTO `leaderboard` (`score`) VALUES (%s)", str(score))
        game_over = True

    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, ("Счёт : " + str(score)), 18, int(WIDTH / 2), 10)
    draw_hp(screen, 5, 5, player.hp)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()
