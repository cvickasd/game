import pygame as pg
import sys
import json
pg.init()
pg.font.init()
font = pg.font.Font("шрифт\Motel King Medium(RUS by Slavchansky).ttf", 25)
pg.display.set_caption("MyGame")

W, H = 1000, 600
screen = pg.display.set_mode((W, H))

clock = pg.time.Clock()

background_images = [pg.transform.scale(pg.image.load(rf"image\oak_woods_v1.0\background\background_layer_{i}.png"), (W, H)).convert_alpha() for i in range(1, 4)]
location = 'menu'


# class
class GameSprite(pg.sprite.Sprite):
    def __init__(self, image:str, x:int, y:int, w:int, h:int) -> None:
        super().__init__()
        self.image = pg.transform.scale(pg.image.load(f'image\{image}'), (w, h)).convert_alpha()
        self.rect = self.image.get_rect(centerx=W//2, bottom=H)
        # self.rect = pg.Rect()
 
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image, x, y, w, h) -> None:
        super().__init__(image, x, y, w, h)
        self.speed = 5
        self.points = 0 # очки для второй игры

        self.lose = False # если враг дотронулся до игрока то lose равен True
        # типо куда смотрит
        self.side = 'right'
        self.time_mouse = 0 # чтобы нельзя была слишком быстро стрелять
        self.mouse = False # Знать нажата ли была кнопка
        self.JUMP_POWER = 12
        self.GRAVITY = 0.35 # Сила, которая будет тянуть нас вниз
        self.yvel = 0 # скорость вертикального перемещения
        self.xvel = 0
        self.onGround = False # На земле ли я?
        self.MOVE_SPEED = 5

        # Animations, image
        self.frame_animation = 0
        self.attack_frame = 0
        self.attack_time_out = 0
        self.bool_attack = False # Now attack?
        
        # типо стоять, я хз как на инглишь будет стоять
        self.stating_image_right = self.image
        self.stating_image_left = pg.transform.flip(self.stating_image_right, True, False)
        
        self.run_images_right = [pg.transform.scale(pg.image.load(fr"image\hero\run_{i}.png"), (w, h)) for i in range(1, 8)]
        
        self.run_images_left = [pg.transform.flip(i, True, False) for i in self.run_images_right]
        
        self.attack_images_right = [pg.transform.scale(pg.image.load(fr"image\hero\attack_{i}.png"), (w, h)) for i in range(1, 3)]
        self.attack_images_right.append(pg.transform.scale(pg.image.load(r"image\hero\attack_3.png"), (40, h)))
        self.attack_images_right.append(pg.transform.scale(pg.image.load(r"image\hero\attack_4.png"), (40, h)))
        self.attack_images_right.append(pg.transform.scale(pg.image.load(r"image\hero\attack_5.png"), (25, h)))
        
        self.attack_images_left = [pg.transform.flip(i, True, False) for i in self.attack_images_right]
        
    def update(self, platforms, HP=False):
        keys = pg.key.get_pressed()
        # left and right
        if keys[pg.K_RIGHT] or keys[pg.K_d]: # RIGHT
            self.xvel = self.MOVE_SPEED
            if self.frame_animation % 4 == 0:
                self.image = self.run_images_right[0]
            if self.frame_animation % 8 == 0:
                self.image = self.run_images_right[1]
            if self.frame_animation % 12 == 0:
                self.image = self.run_images_right[2]
            if self.frame_animation % 16 == 0:
                self.image = self.run_images_right[3]
            if self.frame_animation % 20 == 0:
                self.image = self.run_images_right[4]
            if self.frame_animation % 24 == 0:
                self.image = self.run_images_right[5]
            if self.frame_animation % 28 == 0:
                self.image = self.run_images_right[6]
            self.frame_animation += 0.5
            self.side = 'right'
        elif keys[pg.K_LEFT] or keys[pg.K_a]: # LEFT
            self.xvel = -self.MOVE_SPEED
            if self.frame_animation % 4 == 0:
                self.image = self.run_images_left[0]
            if self.frame_animation % 8 == 0:
                self.image = self.run_images_left[1]
            if self.frame_animation % 12 == 0:
                self.image = self.run_images_left[2]
            if self.frame_animation % 16 == 0:
                self.image = self.run_images_left[3]
            if self.frame_animation % 20 == 0:
                self.image = self.run_images_left[4]
            if self.frame_animation % 24 == 0:
                self.image = self.run_images_left[5]
            if self.frame_animation % 28 == 0:
                self.image = self.run_images_left[6]
            self.frame_animation += 0.5
            self.side = 'left'
        
        # attack
        if keys[pg.K_j] and self.attack_time_out <= 0 or pg.mouse.get_pressed()[0] and self.attack_time_out <= 0 :
            self.attack_time_out = 30

        elif self.attack_time_out > 0:
            self.bool_attack = True
            if self.attack_time_out % 6 == 0:
                self.attack_frame += 1
            self.attack_time_out -= 1
            if self.side == 'right':
                self.image = self.attack_images_right[self.attack_frame-1]
            if self.side == 'left':
                self.image = self.attack_images_left[self.attack_frame-1]
        if self.attack_time_out <= 0:
            self.attack_time_out = 0
            self.bool_attack = False
            self.attack_frame = 0

        # jump
        if keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_SPACE]: # прыгаем, только когда можем оттолкнуться от земли
            if self.onGround:
                self.yvel = -self.JUMP_POWER
        if not(keys[pg.K_LEFT] or keys[pg.K_RIGHT] or keys[pg.K_a] or keys[pg.K_d]) or self.bool_attack: # стоим, когда нет указаний идти   
            self.xvel = 0
            self.frame_animation = 0
            if self.side == "right" and not self.bool_attack:
                self.image = self.stating_image_right
            elif self.side == "left" and not self.bool_attack:
                self.image = self.stating_image_left
        if not self.onGround: # гравитация
            self.yvel += self.GRAVITY
        self.onGround = False;
        
        self.rect.y += self.yvel
        self.collide(0, self.yvel,platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self,xvel, yvel, pfs):
        # attack
        if pg.sprite.collide_rect(self, enemy) and self.attack_frame == 4 or self.attack_frame == 5 and self.bool_attack and pg.sprite.collide_rect(self, enemy):
            print('attack')
        # platforms
        for p in pfs:
            if pg.sprite.collide_rect(self, p):
                if xvel > 0:                      # если движется вправо
                    self.rect.right = p.rect.left # то не движется вправо
                if xvel < 0:                      # если движется влево
                    self.rect.left = p.rect.right # то не движется влево

                if yvel > 0:                      # если падает вниз
                    self.rect.bottom = p.rect.top # то не падает вниз
                    self.onGround = True          # и становится на что-то твердое
                    self.yvel = 0                 # и энергия падения пропадает

                if yvel < 0:                      # если движется вверх
                    self.rect.top = p.rect.bottom # то не движется вверх
                    self.yvel = 0                 # и энергия прыжка пропадает
                    
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, COLOR, image=False):
        pg.sprite.Sprite.__init__(self)
        if image:
            self.image = pg.transform.scale(pg.image.load(image), (PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.rect = self.rect = pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        if not image:
                self.image = pg.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))  
                self.image.fill(pg.Color(COLOR))
                self.rect = pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
# Camera
class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pg.Rect(0, 0, width, height)
	
    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
def camera_configure(camera, target_rect):

    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l+W / 2, -t+H / 2

    l = min(0, l)                  # Не движемся дальше левой границы
    l = max(-(camera.width-W), l)  # Не движемся дальше правой границы
    t = max(-(camera.height-H), t) # Не движемся дальше нижней границы
    t = min(0, t)                  # Не движемся дальше верхней границы

    return pg.Rect(l, t, w, h)  
with open("levels.json", "r", encoding="utf-8") as f:
    levels = json.load(f)
level = levels["level1"]["level"]

class Enemy(GameSprite):
    def __init__(self, image: str, x: int, y: int, w: int, h: int) -> None:
        super().__init__(image, x, y, w, h)
        self.speed = 1
        self.xvel = 0
        self.yvel = 0
        self.GRAVITY = 0.35
        self.onGround = False
        self.side = 'right'
        
        #image, animations
        self.frame_animation = 0
        
        self.stating = self.image
        self.run_images_right = [pg.transform.scale(pg.image.load(f"image/enemy/enemy_run{i}.png"), (w, h)) for i in range(1, 8)]
        self.run_images_left = [pg.transform.flip(i, True, False) for i in self.run_images_right]
    
    def update(self):
        if self.rect.x > player.rect.x:
            self.xvel = -self.speed
            if self.frame_animation % 4 == 0:
                self.image = self.run_images_left[0]
            if self.frame_animation % 8 == 0:
                self.image = self.run_images_left[1]
            if self.frame_animation % 12 == 0:
                self.image = self.run_images_left[2]
            if self.frame_animation % 16 == 0:
                self.image = self.run_images_left[3]
            if self.frame_animation % 20 == 0:
                self.image = self.run_images_left[4]
            if self.frame_animation % 24 == 0:
                self.image = self.run_images_left[5]
            if self.frame_animation % 28 == 0:
                self.image = self.run_images_left[6]
            self.frame_animation += 0.5
            self.side = 'left'
        else:
            self.xvel = self.speed
            if self.frame_animation % 4 == 0:
                self.image = self.run_images_right[0]
            if self.frame_animation % 8 == 0:
                self.image = self.run_images_right[1]
            if self.frame_animation % 12 == 0:
                self.image = self.run_images_right[2]
            if self.frame_animation % 16 == 0:
                self.image = self.run_images_right[3]
            if self.frame_animation % 20 == 0:
                self.image = self.run_images_right[4]
            if self.frame_animation % 24 == 0:
                self.image = self.run_images_right[5]
            if self.frame_animation % 28 == 0:
                self.image = self.run_images_right[6]
            self.frame_animation += 0.5
            self.side = 'right'

        self.rect.x += self.xvel
        if not self.onGround: # гравитация
            self.yvel += self.GRAVITY
        self.onGround = False;
        
        self.rect.y += self.yvel
        self.collide(0, self.yvel,platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self,xvel, yvel, pfs):
        for p in pfs:
            if pg.sprite.collide_rect(self, p):
                if xvel > 0:                      # если движется вправо
                    self.rect.right = p.rect.left # то не движется вправо
                if xvel < 0:                      # если движется влево
                    self.rect.left = p.rect.right # то не движется влево

                if yvel > 0:                      # если падает вниз
                    self.rect.bottom = p.rect.top # то не падает вниз
                    self.onGround = True          # и становится на что-то твердое
                    self.yvel = 0                 # и энергия падения пропадает

                if yvel < 0:                      # если движется вверх
                    self.rect.top = p.rect.bottom # то не движется вверх
                    self.yvel = 0                 # и энергия прыжка пропадает
    
def render_text(text, f, x=False, y=False):
    text_surface = f.render(text, True, (255,255,255))
    if not x and not y:
        screen.blit(text_surface, (W//2-f.size(text)[0]/2, H//2-f.size(text)[1]/2))            
    elif not x:
        screen.blit(text_surface, (W//2-f.size(text)[0]/2, y))
    elif not y:
        screen.blit(text_surface, (x, H//2-f.size(text)[1]/2))           
    elif x and y:
        screen.blit(text_surface, (x, y))

total_level_w = len(level[0])*30
total_level_h = len(level)*30

sprites = pg.sprite.Group()
camera = Camera(camera_configure, total_level_w, total_level_h)
player = Player('hero/1.png', 90, 120, 25, 50)
enemy = Enemy("enemy\enemy.png", 90, 120, 25, 50)
platforms = []
sprites.add(player)
sprites.add(enemy)

player.rect.x, player.rect.y = levels["level1"]["player_pos"][0], levels["level1"]["player_pos"][1]
enemy.rect.x, enemy.rect.y = levels["level1"]["enemy_pos"][0], levels["level1"]["enemy_pos"][1]
# menu image

image_menu = pg.transform.scale(pg.image.load("image/menu.png"), (800, 500))
image_button_play = pg.transform.scale(pg.image.load("image/menu_play.jpg"), (100, 50))
image_button_settings = pg.transform.scale(pg.image.load("image/menu_settings.jpg"), (100, 50))
image_button_exit = pg.transform.scale(pg.image.load("image/menu_exit.jpg"), (100, 50))


# level
PLATFORM_WIDTH = PLATFORM_HEIGHT = 30
x=y=0 # координаты
for row in level: # вся строка
    for col in row: # каждый символ
        if col == "-":
            #создаем блок, заливаем его цветом и рисеум его
            pf = Platform(x, y, "#036a96", "image/ground/block_up.png")
            sprites.add(pf)
            platforms.append(pf)
        if col == 'r':
            pf = Platform(x, y, "#036a96", "image/ground/block_up_right.png")
            sprites.add(pf)
            platforms.append(pf)    
        if col == "l":
            pf = Platform(x, y, "asdasd", "image/ground/block_up_left.png")        
            sprites.add(pf)
            platforms.append(pf)    
        if col == '1':
            pf = Platform(x, y, "asdasd", "image/ground/block_right.png")        
            sprites.add(pf)
            platforms.append(pf)    
        if col == '2':
            pf = Platform(x, y, "asdasd", "image/ground/block_left.png")        
            sprites.add(pf)
            platforms.append(pf)    
        if col == 'g':
            pf = Platform(x, y, "asdas", "image\ground\ground.png")
            sprites.add(pf)
            platforms.append(pf)
        if col == '4':
            pf = Platform(x, y, "asdas", "image/ground/block_down_up_left.png")
            sprites.add(pf)
            platforms.append(pf)
        if col == '5':
            pf = Platform(x, y, "asdas", "image/ground/block_up_down_right.png")
            sprites.add(pf)
            platforms.append(pf)
        if col == '6':
            pf = Platform(x, y, "asdas", "image/ground/block_down.png")
            sprites.add(pf)
            platforms.append(pf)
        if col == '7':
            pf = Platform(x, y, "asdas", "image/ground/block_up_down.png")
            sprites.add(pf)
            platforms.append(pf)
        x += PLATFORM_WIDTH #блоки платформы ставятся на ширине блоков
    y += PLATFORM_HEIGHT    #то же самое и с высотой
    x = 0                   #на каждой новой строчке начинаем с нуля

while True:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            sys.exit()
        if ev.type == pg.MOUSEBUTTONDOWN:
            mouse = pg.mouse.get_pos()
            print(mouse)

    # draw background
    for i in background_images:
        screen.blit(i, (0, 0))

    if location == 'menu':
        for i in background_images:
            screen.blit(i, (0, 0))
        render_text("MYGAME", font, False, 100)
        render_text("ИГРАТЬ", font, False, H//2-100)
        render_text("НАСТРОЙКИ", font)
        render_text("ВЫЙТИ", font, False, H//2+100)
        if pg.mouse.get_pressed()[0]:
            x, y = pg.mouse.get_pos() 
            if 440 <= x <= 555 and 195 <= y <= 225:
                location = 'game'
            elif 400 <= x <= 595 and 285 <= y <= 315:
                location = 'settings'
            elif 440 <= x <= 555 and 400 <= y <= 425:
                location = 'quit'
                run = False
                pg.quit()
            print(location)

    if location == 'game':
        pg.mouse.set_visible(False)
        player.update(platforms)
        camera.update(player)
        enemy.update()
        # draw sprites
        for e in sprites:
            screen.blit(e.image, camera.apply(e))

    pg.display.update()
    clock.tick(60)