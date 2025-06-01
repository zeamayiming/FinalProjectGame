import pygame
import math


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, speed=8):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((178, 34, 34))
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.speed = speed

        # 計算目標的實際移動方向和速度
        if hasattr(target, 'speed'):
            target_pos = pygame.Vector2(target.rect.center)

            # 根據不同模式計算目標的移動方向
            if hasattr(target, 'mode') and target.mode == 2:  # surround 模式
                if hasattr(target, 'castle'):
                    # 計算殭屍到城堡的方向
                    dir_to_castle = pygame.Vector2(
                        target.castle.rect.center) - target_pos
                    if dir_to_castle.length() != 0:
                        dir_to_castle = dir_to_castle.normalize()
                        target_velocity = dir_to_castle * target.speed
                    else:
                        target_velocity = pygame.Vector2(0, 0)
                else:
                    target_velocity = pygame.Vector2(0, 0)
            else:  # normal 模式
                # 從左到右移動
                target_velocity = pygame.Vector2(target.speed, 0)
        else:
            target_velocity = pygame.Vector2(0, 0)

        shooter_pos = self.pos
        rel_pos = pygame.Vector2(target.rect.center) - shooter_pos

        # 使用二次方程求解碰撞時間
        a = target_velocity.dot(target_velocity) - self.speed ** 2
        b = 2 * rel_pos.dot(target_velocity)
        c = rel_pos.dot(rel_pos)

        # 計算最佳射擊時間
        t = 0
        if abs(a) < 0.001:  # 特殊情況：目標速度與子彈速度相近
            if abs(b) > 0.001:
                t = -c / b
        else:
            discriminant = b ** 2 - 4 * a * c
            if discriminant >= 0:
                sqrt_d = math.sqrt(discriminant)
                t1 = (-b + sqrt_d) / (2 * a)
                t2 = (-b - sqrt_d) / (2 * a)
                # 選擇最早的正時間
                valid_times = [t for t in [t1, t2] if t > 0]
                if valid_times:
                    t = min(valid_times)

        # 計算預測位置並設置子彈速度
        if t > 0:
            # 由於子彈速度變快，減少預測提前量
            prediction_factor = 1.05  # 從 1.1 降低到 1.05
            future_pos = pygame.Vector2(
                target.rect.center) + target_velocity * t * prediction_factor

            # 由於子彈速度變快，可以增加最大預測距離
            max_prediction_distance = 400  # 從 300 增加到 400
            if (future_pos - shooter_pos).length() > max_prediction_distance:
                future_pos = pygame.Vector2(
                    target.rect.center) + target_velocity * t
        else:
            future_pos = pygame.Vector2(target.rect.center)

        # 計算子彈方向和速度
        direction = future_pos - shooter_pos
        if direction.length() != 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.Vector2(0, 0)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if self.rect.colliderect(self.target.rect):
            self.target.health -= 1
            if self.target.health <= 0:
                self.target.kill()
            if hasattr(self, 'score_display'):
                self.score_display.add(100)
            self.kill()
