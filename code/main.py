import pygame, sys
from pytmx.util_pygame import load_pygame
from player import Player
from sprite import Sprite, Bullet
from monster import Coffin, Cactus
from settings import * 


class AllSprites(pygame.sprite.Group):
	def __init__(self, *sprites) -> None:
		super().__init__(*sprites)
		self.offset = pygame.Vector2()
		self.display_surface = pygame.display.get_surface()
		self.bg = pygame.image.load('graphics/other/bg.png').convert()

	def custom_draw(self, player):
		# change the offset vect
		self.offset.x = player.rect.centerx - WINDOW_WIDTH/2
		self.offset.y = player.rect.centery - WINDOW_HEIGHT/2

		# blit the surfaces
		# background
		self.display_surface.blit(self.bg, -self.offset)

		# sprites
		for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
			offset_rect = sprite.image.get_rect(center = sprite.rect.center)
			offset_rect.center -= self.offset
			self.display_surface.blit(sprite.image, offset_rect)
			# try:
			# 	hit_off_rect = sprite.hitbox.copy()
			# 	hit_off_rect.center -= self.offset
			# 	pygame.draw.rect(self.display_surface, (30, 30, 200), hit_off_rect, 2)
			# 	pygame.draw.rect(self.display_surface, (40, 200, 40), offset_rect, 2)				
			# except:
			# 	pygame.draw.rect(self.display_surface, (40, 200, 40), offset_rect, 2)				


class Game:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Western shooter')
		self.clock = pygame.time.Clock()

		# bullets
		self.bullet_surf = pygame.image.load('graphics/other/particle.png').convert_alpha()

		# groups 
		self.all_sprites = AllSprites()
		self.obstacles = pygame.sprite.Group()
		self.bullets = pygame.sprite.Group()
		self.monsters = pygame.sprite.Group()

		self.setup()
		self.music = pygame.mixer.Sound('sound/music.mp3')
		self.music.set_volume(0.1)
		self.music.play(loops = -1)

	def setup(self):
		tmx_map = load_pygame('data/map.tmx')

		# tiles
		for x, y, tile in tmx_map.get_layer_by_name('Fence').tiles():
			Sprite((x * 64, y * 64), tile, [self.all_sprites, self.obstacles])
		
		# objects
		for obj in tmx_map.get_layer_by_name('Objects'):
			Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacles])
		
		for obj in tmx_map.get_layer_by_name('Entities'):
			match obj.name:
				case 'Player':
					self.player = Player(
						pos = (obj.x, obj.y),
						path = PATHS["player"],
						groups = self.all_sprites,
						collision_sprites = self.obstacles,
						create_bullet = self.create_bullet
					)
				case 'Coffin':
					Coffin((obj.x, obj.y), PATHS['coffin'], [self.all_sprites, self.monsters], self.obstacles, self.player)
				case 'Cactus':
					Cactus((obj.x, obj.y), PATHS['cactus'], [self.all_sprites, self.monsters], self.obstacles, self.player, self.create_bullet)

	def bullet_collision(self):

		# objects bullet collision
		for obstacle in self.obstacles.sprites():
			pygame.sprite.spritecollide(obstacle, self.bullets, True)
		
		# monsters bullet collision
		for bullet in self.bullets.sprites():
			sprites = pygame.sprite.spritecollide(bullet, self.monsters, False, pygame.sprite.collide_mask)

			if sprites:
				bullet.kill()
				for sprite in sprites:
					sprite.damage()

		# player bullet collision
		if pygame.sprite.spritecollide(self.player, self.bullets, True, pygame.sprite.collide_mask):
			self.player.damage()

	def create_bullet(self, pos, direction):
		Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullets])

	def run(self):
		while True:

			# event loop 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			# delta time
			dt = self.clock.tick() * 0.001
			self.bullet_collision()

			pygame.display.set_caption(f'Western shooter {self.clock.get_fps():.0f}fps')
			# update groups
			self.all_sprites.update(dt)

			# draw groups
			self.display_surface.fill('black')
			self.all_sprites.custom_draw(self.player)

			pygame.display.update()


if __name__ == '__main__':
	game = Game()
	game.run()