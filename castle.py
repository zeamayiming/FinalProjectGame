import pygame


class Castle(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.transform.scale(img, (100, 100))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(midleft=(150, 350))
        self.health = 1  # 初始血量
