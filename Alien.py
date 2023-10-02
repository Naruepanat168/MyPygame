#Workshop 16: เกม Alien Objects

import sys, pygame, random
from pygame.locals import *

SCREEN_W = 600
SCREEN_H = 400
BLUESKY = (200, 220, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
FPS = 30

pygame.init()
pygame.display.set_caption('Alien Objects')
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
screen_rect = screen.get_rect()

clock = pygame.time.Clock()
img_path = r'assets/pygame/images'
font_path = r'assets/pygame/fonts'
snd_path = r'assets/pygame/sounds'

win = False
lose = False
game_over = False
explosion_end = False
total_score = 0

group_object = pygame.sprite.Group()


#--------------- Object Sprite ---------------
bomb_img = pygame.image.load(fr'{img_path}/bomb.png')
diamond_img = pygame.image.load(fr'{img_path}/diamond.png')
star_img = pygame.image.load(fr'{img_path}/star.png')
objects = [bomb_img, star_img, diamond_img]

class Object(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Object, self).__init__()
        self.image = None
        self.object_type = None
        self.score = 0

        i = random.randrange(1, 10)
        if i in range(1, 6):
            self.image = objects[0]
            self.object_type = 'bomb'
        elif i in range(6, 9):
            self.image = objects[1]
            self.object_type = 'star'
            self.score = 5              
        else:
            self.image = objects[2]
            self.object_type = 'diamond'
            self.score = 10         

        self.rect = self.image.get_rect(midbottom=pos)
        self.speedy = 10

    def update(self):
        self.rect.move_ip(0, self.speedy)
        if self.rect.top > SCREEN_H:
            self.kill()
            

#--------------- Alien Sprite ---------------
alien_img = pygame.image.load(fr'{img_path}/alien-ship.png')
alien_img = pygame.transform.scale(alien_img, (31, 21))

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super(Alien, self).__init__()
        self.image = alien_img

        start_x = random.randint(-200, 0)
        start_y = random.randint(0, SCREEN_H // 3)
        self.rect = self.image.get_rect(
            left=start_x, top=start_y
        )
        self.speedy = random.randrange(-5, 5)
        self.speedx = 5
        
        self.has_object = False
        self.drop_object = SCREEN_W

        r = random.randint(1, 10)
        if r >= 5: 
            self.has_object = True
            self.distance_drop_object = \
                    random.randint(50, SCREEN_W - 50)

    def update(self):
        self.rect.move_ip(self.speedx, self.speedy)
        if self.rect.left > SCREEN_W:
            self.kill()
        
        if self.rect.top <= 0 or (self.rect.centery >= screen_rect.centery):
            self.speedy *= -1

        if self.has_object and self.rect.centerx >= self.distance_drop_object:
            obj = Object(self.rect.midbottom)
            group_object.add(obj)
            self.has_object = False


#--------------- Cart Sprite ---------------
cart_img = pygame.image.load(fr'{img_path}/cart.png')
cart_img = pygame.transform.scale(cart_img, (40, 40))

class Cart(pygame.sprite.Sprite):
    def __init__(self):
        super(Cart, self).__init__()
        self.image = cart_img
        self.rect = self.image.get_rect(
            bottom=SCREEN_H - 5, centerx=screen_rect.centerx
        )
        self.speedx = 10

    def update(self, keys):
        #รถเข็นจะเลื่อนได้เฉพาะในแนวซ้าย-ขวา
        if keys[K_RIGHT]: 
            self.rect.move_ip(self.speedx, 0)
            if self.rect.right >  SCREEN_W:
                self.rect.right = SCREEN_W

        elif keys[K_LEFT]: 
            self.rect.move_ip(-self.speedx, 0)
            if self.rect.left < 0:
                self.rect.left = 0    


#--------------- Explosion Sprite ---------------
exp_img =  pygame.image.load(fr'{img_path}/explosion.png') 
exp_num_rows = 3       
exp_num_cols = 3        
exp_subimg_w = exp_img.get_width() // exp_num_rows  
exp_subimg_h = exp_img.get_height() // exp_num_cols 
exp_subimgs = []        

for r in range(exp_num_rows):
    for c in range(exp_num_cols):
        x = c * exp_subimg_w
        y = r * exp_subimg_h
        img = exp_img.subsurface(x, y, exp_subimg_w, exp_subimg_h)
        exp_subimgs.append(img)

exp_num_subimgs = len(exp_subimgs)          
exp_repeat = FPS // exp_num_subimgs  
exp_last_frame = (exp_repeat * exp_num_subimgs) - 1    

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):       
        super(Explosion, self).__init__()
        self.image = exp_subimgs[0]
        left = pos[0] - (exp_subimg_w // 2)
        top = pos[1] - (exp_subimg_h // 2)
        self.rect = pygame.Rect(
            left, top, exp_subimg_w, exp_subimg_w
        )
        self.index = 0

    def update(self):
        global explosion_end
        if self.index >= exp_last_frame:
            self.kill()
            explosion_end = True
        else:
            i = self.index // exp_repeat
            self.image = exp_subimgs[i]
            screen.blit(self.image, self.rect)
            self.index += 1


#--------------- Images and Sounds ---------------
cover = pygame.image.load(fr'{img_path}/alien-cover.jpg')
bg_sky = pygame.image.load(fr'{img_path}/sky-with-stars.jpg')

intro_snd = pygame.mixer.Sound(fr'{snd_path}/stagepop.wav')
bg_snd = pygame.mixer.Sound(fr'{snd_path}/outer-space.wav')
exp_snd = pygame.mixer.Sound(fr'{snd_path}/explosion.wav')
beep_snd = pygame.mixer.Sound(fr'{snd_path}/beep.wav')


#--------------- Text & Intro Screen ---------------
def draw_text(text, size, colour, x, y, fontfile=None):
    #ถ้าไม่ระบุชื่อไฟล์ของฟอนต์ ให้ใช้ฟอนต์ของระบบ
    if fontfile == None:
        font = pygame.font.SysFont(None, size)
    else:
        font = pygame.font.Font(fontfile, size)

    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(midtop=(x, y))
    screen.blit(text_surface, text_rect)

def intro_screen():
    intro_snd.play(-1)
    screen.fill(BLUE)

    #ภาพหน้าปก ซึ่งจะแสดงเป็นพื้นหลังของหน้าจอเริ่มต้น
    screen.blit(cover, cover.get_rect())    #วาดภาพหน้าปก

    #ชื่อเกม ใช้ฟอนต์ที่ชื่อ Hyperblox
    
    draw_text("Use arrow keys to move the cart", 24, CYAN, 
            screen_rect.centerx, 200)

    #แสดงปุ่ม EXIT
    btn_exit_image = pygame.image.load(fr'{img_path}/btn-exit.png')
    btn_exit_rect = btn_exit_image.get_rect(
        right=screen_rect.centerx - 50, top=320
    )

    #แสดงปุ่ม START
    btn_start_image = pygame.image.load(fr'{img_path}/btn-start.png')
    btn_start_rect = btn_start_image.get_rect(
        left=screen_rect.centerx + 50, top=320
    )

    screen.blit(btn_start_image, btn_start_rect)
    screen.blit(btn_exit_image, btn_exit_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                #ถ้าคลิกที่ปุ่ม START ให้เริ่มเล่นเกม
                if btn_start_rect.collidepoint(pygame.mouse.get_pos()):
                    intro_snd.stop()
                    waiting = False
                #ถ้าคลิกปุ่ม EXIT ให้ออกจากเกม
                elif btn_exit_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit()
                    sys.exit()    


#---------------------------------------------
playing = False
running = True
while running:
    if not playing:
        intro_screen()

        playing = True

        game_over = False
        total_score = 0
        win = False
        lose = False
        explosion_end = False

        cart = Cart()
        group_cart = pygame.sprite.Group()
        group_cart.add(cart)

        group_alien = pygame.sprite.Group()

        ADD_alien = pygame.USEREVENT + 1
        pygame.time.set_timer(ADD_alien, 500)

        group_explosion = pygame.sprite.Group()

        bg_snd.play(-1)

    for e in pygame.event.get():
        if e.type == QUIT:
            running = False    
            pygame.quit()
            sys.exit()
        elif e.type == ADD_alien and not game_over:
            alien = Alien()
            group_alien.add(alien)

        #ถ้าคลิกเมาส์เมื่อจบเกมแล้ว ให้เข้าสู่หน้าจอเริ่มต้น
        elif e.type == MOUSEBUTTONDOWN and game_over:
            playing = False


    screen.fill(BLACK) 
    screen.blit(bg_sky, bg_sky.get_rect())  #แสดงภาพพื้นหลัง

    keys = pygame.key.get_pressed()
    group_alien.update()
    group_object.update()
    group_cart.update(keys)
    group_explosion.update()

    group_alien.draw(screen)
    group_object.draw(screen)
    group_cart.draw(screen)
    group_explosion.draw(screen)

    #ถ้าจบเกม ให้แสดงข้อความว่าเป็นผู้แพ้หรือชนะ
    if game_over: 
        bg_snd.stop()   #หยุดเล่นเสียงเบื้องหลัง  
        if win:         #ถ้าชนะ ให้แสดงข้อความ
            draw_text('You Win', 60, BLUE, screen_rect.centerx, 150)

        elif explosion_end and lose: #ถ้าแสดงภาพระเบิดครบแล้ว ให้แสดงข้อความว่าแพ้
            draw_text('You Lose', 60, RED, screen_rect.centerx, 150)

        #ไม่ว่าจะแพ้หรือชนะ ให้แสดงข้อความต่อไปนี้ 
        #ถ้าแพ้ ต้องแสดงภาพระเบิดครบแล้ว   
        if explosion_end or win:
            draw_text('Click mouse to continue...', 24, GREEN, 
                        screen_rect.centerx, 300)
    
    #แสดงแต้มที่ได้ในขณะนั้น
    text = f'score: {total_score}%'
    draw_text(text, 24, WHITE, 50, 10)

    pygame.display.flip()
    clock.tick(FPS)

    #ตรวจสอบการชนระหว่างวัตถุกับรถเข็น
    hits = pygame.sprite.groupcollide(
            group_object, group_cart, True, False, 
            pygame.sprite.collide_mask
    )
    if len(hits) > 0:
        for hit in hits:
            first_hit = hit
            break
        
        #ถ้าวัตถุที่ชนคือระเบิด
        if first_hit.object_type == 'bomb':
            center = first_hit.rect.center
            explosion = Explosion(center)
            group_explosion.add(explosion)
            exp_snd.play()            
            game_over = True
            lose = True

        #ถ้าวัตถุที่ชนคือเพชรหรือดาว
        else:
            total_score += first_hit.score
            beep_snd.play()


    #ถ้าได้แต้มครบ 100
    if total_score >= 100:
        game_over = True
        win = True
    
    #ถ้าจบเกมให้ทำลายรถเข็น เพื่อป้องกันการชนซ้ำ
    if game_over:
        for c in group_cart:
            c.kill()        
    
