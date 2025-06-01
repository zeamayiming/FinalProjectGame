import pygame
from bullet import Bullet


class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((102, 255, 102))
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 10
        self.range = 200
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 1000

    def shoot(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return None

        candidates = [e for e in enemies if pygame.Vector2(
            e.rect.center).distance_to(self.rect.center) <= self.range]
        if not candidates:
            return None

        target = min(candidates, key=lambda e: e.rect.centerx)
        self.last_shot = now
        return Bullet(self.rect.center, target)

    def set_bullet_image(self, img):
        # 若未來 bullet 改為帶圖片可使用
        self.bullet_img = img
