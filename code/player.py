import pygame
from os import walk
from entity import Entity

class Player(Entity):
    def __init__(self, pos, path, groups, collision_sprites, create_bullet) -> None:
        super().__init__(pos, path, groups, collision_sprites)
        
        # bullet
        self.create_bullet = create_bullet
        self.bullet_shot = False

        # health
        self.health = 5

    def check_death(self):
        if self.health <= 0:
            pygame.quit()
            exit()

    def get_status(self):
        # idle
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split('_')[0] + '_idle'
        
        # attacking
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def animate(self, dt):
        current_animation = self.animations[self.status]

        self.frame_index += 7 * dt
        if int(self.frame_index) == 2 and self.attacking and not self.bullet_shot:
            bullet_start_pos = self.rect.center + self.bullet_direction * 80
            self.create_bullet(bullet_start_pos, self.bullet_direction)
            self.bullet_shot = True
            self.shoot_sound.play()

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.attacking:

            # horizontal input
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
            
            # vertical input
            if keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            elif keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            else:
                self.direction.y = 0

            # attack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.direction = pygame.Vector2()
                self.frame_index = 0
                self.bullet_shot = False
                match self.status.split('_')[0]:
                    case 'left': self.bullet_direction = pygame.Vector2(-1, 0)
                    case 'right': self.bullet_direction = pygame.Vector2(1, 0)
                    case 'up': self.bullet_direction = pygame.Vector2(0, -1)
                    case 'down': self.bullet_direction = pygame.Vector2(0, 1)

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
        self.blink()
        self.vulnerability_timer()
        self.check_death()
