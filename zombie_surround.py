import pygame
import random
import math
import config


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, zombie_img, mode=1):
        super().__init__()
        self.original_image = pygame.transform.scale(zombie_img, (40, 40))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 2
        self.speed = 1.0
        self.mode = mode
        self.plants = None
        self.castle = None
        self.target_x = 0
        self.target_y = 0

    def bind_context(self, plants, castle):
        self.plants = plants
        self.castle = castle

    def update(self):
        if self.castle:
            # 檢查是否碰到植物
            plant_hits = pygame.sprite.spritecollide(self, self.plants, False)
            if plant_hits:
                for plant in plant_hits:
                    plant.health -= 1
                    if plant.health <= 0:
                        plant.kill()
            else:
                # 沒有碰到植物時才移動
                if self.mode == 1:  # 從左邊來的模式
                    self.rect.x += self.speed
                else:  # 從四面八方來的模式
                    # 計算到目標的方向向量
                    dx = self.target_x - self.rect.centerx
                    dy = self.target_y - self.rect.centery
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance != 0:
                        # 標準化方向向量並乘以速度
                        self.rect.x += (dx / distance) * self.speed
                        self.rect.y += (dy / distance) * self.speed

            # 檢查是否碰到城堡
            if self.rect.colliderect(self.castle.rect):
                self.castle.health -= 1
                self.kill()

    @staticmethod
    def generate_zombie(zombie_img, mode=1):
        """
        根據模式生成殭屍
        mode 1: 從左邊生成
        mode 2: 從四面八方生成
        """
        if mode == 1:
            # 從左邊生成
            x = -50
            y = random.randint(100, config.HEIGHT - 250)
        else:
            # 從四面八方生成
            angle = random.uniform(0, 2 * math.pi)
            x = int(config.WIDTH // 2 + math.cos(angle) * 500)  # 以畫面中心為圓心
            y = int(config.HEIGHT // 2 + math.sin(angle) * 500)

        return Zombie(x, y, zombie_img, mode)
