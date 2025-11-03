import pygame,random
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surface = pygame.Surface((50, 50))
        self.surface.fill((255, 0, 0))
        self.rect = self.surface.get_rect()
    def update(self, pressed_keys):
        match pressed_keys:
            case _ if pressed_keys[K_UP]:
                self.rect.move_ip(0, -1)
            case _ if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, 1)
            case _ if pressed_keys[K_LEFT]:
                self.rect.move_ip(-1, 0)
            case _ if pressed_keys[K_RIGHT]:
                self.rect.move_ip(1, 0)
                
        match self.rect:
            case _ if self.rect.left < 0:
                self.rect.left = 0
            case _ if self.rect.right > screen_width:
                self.rect.right = 800
            case _ if self.rect.top < 0:
                self.rect.top = 0
            case _ if self.rect.bottom > screen_height:
                self.rect.bottom = 600
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surface = pygame.Surface((30, 30))
        self.surface.fill((0, 0, 255))
        self.rect = self.surface.get_rect(
            center=(
            random.randint(0, screen_width),
                random.randint(0, screen_height),)
        )   
        
        def update(self):
            self.rect.move_ip(-1, 0)
            if self.rect.right < 0:
                self.kill()
        
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
player = Player()
enemy1 = Enemy()
enemies = pygame.sprite.Group()
enemies.add(enemy1)
all_sprites = pygame.sprite.Group()
all_sprites.add(player,enemies)
running = True

while running:
    for event in pygame.event.get():
        if ((event.type == KEYDOWN) and (event.key == K_ESCAPE)) or (event.type == pygame.QUIT):
            pygame.quit()
            running = False
    player.update(pygame.key.get_pressed())
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (0, 0, 0), (750, 300), 15)
    for entity in all_sprites:
        screen.blit(entity.surface,entity.rect)
    if pygame.sprite.spritecollideany(player, enemies):
        player.kill()
        running = False
    pygame.display.flip()
    