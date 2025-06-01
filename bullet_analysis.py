import pygame
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.font_manager as fm

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

# 初始化 Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Prediction Analysis")

# 設置 Pygame 中文字體
try:
    FONT = pygame.font.Font("msjh.ttc", 24)  # 嘗試載入微軟正黑體
except:
    try:
        FONT = pygame.font.Font("mingliu.ttc", 24)  # 嘗試載入細明體
    except:
        FONT = pygame.font.Font(None, 24)  # 如果都失敗，使用預設字體
        print("警告：無法載入中文字體，部分文字可能無法正確顯示")

clock = pygame.time.Clock()

# 顏色定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)


class Target:
    def __init__(self, x, y, mode=1):
        self.rect = pygame.Rect(x, y, 20, 20)  # 縮小目標大小
        self.speed = 2.0
        self.mode = mode
        self.castle_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
        self.pos = pygame.Vector2(x, y)
        self.original_pos = pygame.Vector2(x, y)

    def reset(self):
        self.pos = pygame.Vector2(self.original_pos)
        self.rect.center = self.pos

    def update(self):
        if self.mode == 1:  # 直線模式 (normal mode)
            # 簡單的水平移動
            self.pos.x += self.speed
            # 如果移動到畫面右側，重置到左側
            if self.pos.x > WIDTH:
                self.pos.x = 0
        else:  # 環繞模式
            # 朝向城堡移動
            dir_to_castle = self.castle_pos - self.pos
            if dir_to_castle.length() != 0:
                dir_to_castle = dir_to_castle.normalize()
                self.pos += dir_to_castle * self.speed
        self.rect.center = self.pos

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)


class OldBullet:
    def __init__(self, start_pos, target, speed=8):
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.speed = speed
        self.rect = pygame.Rect(start_pos[0], start_pos[1], 8, 8)
        self.original_pos = pygame.Vector2(start_pos)

        # 舊版預測邏輯
        target_pos = pygame.Vector2(target.rect.center)
        if target.mode == 1:  # Linear Mode
            # 使用簡單的追趕邏輯
            distance_to_target = (target_pos - self.pos).length()
            time_to_reach = distance_to_target / self.speed
            target_future_x = target_pos.x + (target.speed * time_to_reach)
            future_pos = pygame.Vector2(target_future_x, target_pos.y)
        else:  # Surround Mode
            dir_to_castle = pygame.Vector2(WIDTH//2, HEIGHT//2) - target_pos
            if dir_to_castle.length() != 0:
                dir_to_castle = dir_to_castle.normalize()
                target_velocity = dir_to_castle * target.speed
                future_pos = target_pos + target_velocity * 20
            else:
                future_pos = target_pos

        direction = future_pos - self.pos
        self.velocity = direction.normalize() * speed if direction.length() != 0 else pygame.Vector2(0, 0)

    def reset(self):
        self.pos = pygame.Vector2(self.original_pos)
        self.rect.center = self.pos

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)


class NewBullet:
    def __init__(self, start_pos, target, speed=8):
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.speed = speed
        self.rect = pygame.Rect(start_pos[0], start_pos[1], 8, 8)
        self.original_pos = pygame.Vector2(start_pos)

        # 新版預測邏輯
        target_pos = pygame.Vector2(target.rect.center)
        
        if target.mode == 1:  # normal mode
            target_velocity = pygame.Vector2(target.speed, 0)
        else:  # surround mode
            dir_to_castle = target.castle_pos - target_pos
            if dir_to_castle.length() != 0:
                dir_to_castle = dir_to_castle.normalize()
                target_velocity = dir_to_castle * target.speed
            else:
                target_velocity = pygame.Vector2(0, 0)

        rel_pos = pygame.Vector2(target.rect.center) - self.pos
        
        # 使用二次方程求解碰撞時間
        a = target_velocity.dot(target_velocity) - self.speed ** 2
        b = 2 * rel_pos.dot(target_velocity)
        c = rel_pos.dot(rel_pos)
        
        t = 0
        if abs(a) < 0.001:
            if abs(b) > 0.001:
                t = -c / b
        else:
            discriminant = b ** 2 - 4 * a * c
            if discriminant >= 0:
                sqrt_d = math.sqrt(discriminant)
                t1 = (-b + sqrt_d) / (2 * a)
                t2 = (-b - sqrt_d) / (2 * a)
                valid_times = [t for t in [t1, t2] if t > 0]
                if valid_times:
                    t = min(valid_times)

        if t > 0:
            prediction_factor = 1.05
            future_pos = pygame.Vector2(target.rect.center) + target_velocity * t * prediction_factor
            max_prediction_distance = 400
            if (future_pos - self.pos).length() > max_prediction_distance:
                future_pos = pygame.Vector2(target.rect.center) + target_velocity * t
        else:
            future_pos = pygame.Vector2(target.rect.center)

        direction = future_pos - self.pos
        self.velocity = direction.normalize() * speed if direction.length() != 0 else pygame.Vector2(0, 0)

    def reset(self):
        self.pos = pygame.Vector2(self.original_pos)
        self.rect.center = self.pos

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)


class Plant:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = 30
        self.shoot_cooldown = 0
        self.shoot_delay = 60  # 發射冷卻時間（幀數）
        
    def draw(self, screen):
        # 繪製植物主體（深綠色圓形）
        pygame.draw.circle(screen, DARK_GREEN, (int(self.pos.x), int(self.pos.y)), self.size//2)
        
        # 繪製葉子（淺綠色）
        leaf_points = [
            (self.pos.x - self.size//2, self.pos.y),
            (self.pos.x - self.size//4, self.pos.y - self.size//4),
            (self.pos.x, self.pos.y),
        ]
        pygame.draw.polygon(screen, LIGHT_GREEN, leaf_points)
        
        leaf_points = [
            (self.pos.x - self.size//2, self.pos.y),
            (self.pos.x - self.size//4, self.pos.y + self.size//4),
            (self.pos.x, self.pos.y),
        ]
        pygame.draw.polygon(screen, LIGHT_GREEN, leaf_points)
        
        # 繪製發射器（深綠色矩形）
        shooter_rect = pygame.Rect(self.pos.x, self.pos.y - 5, self.size//2, 10)
        pygame.draw.rect(screen, DARK_GREEN, shooter_rect)
        
    def get_shooter_pos(self):
        # 返回發射點位置（在發射器的右端）
        return pygame.Vector2(self.pos.x + self.size//2, self.pos.y)

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


def visualize_simulation(bullet_class, mode=1, num_trials=5):
    hits = 0
    total_trials = 0

    # 創建植物（更靠近城堡的位置）
    plant_offset = 150  # 距離城堡的距離
    plant = Plant(WIDTH//2 - plant_offset, HEIGHT//2)

    while total_trials < num_trials:
        SCREEN.fill(WHITE)

        # 繪製城堡
        castle_rect = pygame.Rect(WIDTH//2 - 20, HEIGHT//2 - 20, 40, 40)
        pygame.draw.rect(SCREEN, GRAY, castle_rect)
        castle_text = FONT.render("Castle", True, BLACK)
        SCREEN.blit(castle_text, (WIDTH//2 - 30, HEIGHT//2 + 30))

        # 生成目標
        if mode == 1:  # 直線模式 (normal mode)
            # 在左側生成目標，讓它水平移動
            target = Target(0, random.randint(100, HEIGHT-100), mode=mode)
        else:  # 環繞模式
            angle = random.uniform(0, 2 * math.pi)
            radius = 300
            x = int(WIDTH//2 + math.cos(angle) * radius)
            y = int(HEIGHT//2 + math.sin(angle) * radius)
            target = Target(x, y, mode=mode)

        # 從植物發射子彈
        bullet = bullet_class(plant.get_shooter_pos(), target)

        hit = False
        steps = 0

        # 模擬迴圈
        while steps < 200 and not hit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # 更新位置
            target.update()
            bullet.update()
            plant.update()

            # 清除畫面
            SCREEN.fill(WHITE)

            # 繪製城堡
            pygame.draw.rect(SCREEN, GRAY, castle_rect)
            castle_text = FONT.render("Castle", True, BLACK)
            SCREEN.blit(castle_text, (WIDTH//2 - 30, HEIGHT//2 + 30))

            # 繪製植物、目標和子彈
            plant.draw(SCREEN)
            target.draw(SCREEN)
            bullet.draw(SCREEN)

            # 檢查碰撞
            if bullet.rect.colliderect(target.rect):
                hit = True
                hits += 1

            # 顯示當前統計
            stats_text = f"Hits: {hits}/{total_trials} ({(hits/max(1, total_trials)*100):.1f}%)"
            text_surface = FONT.render(stats_text, True, BLACK)
            SCREEN.blit(text_surface, (10, 10))

            # 顯示模式資訊
            mode_text = "Linear Mode" if mode == 1 else "Surround Mode"
            mode_surface = FONT.render(mode_text, True, BLACK)
            SCREEN.blit(mode_surface, (10, 40))

            # 顯示版本資訊
            version_text = "Old Version" if bullet_class == OldBullet else "New Version"
            version_surface = FONT.render(version_text, True, BLACK)
            SCREEN.blit(version_surface, (10, 70))

            pygame.display.flip()
            clock.tick(60)
            steps += 1

        total_trials += 1
        pygame.time.wait(500)

    return hits/num_trials * 100

def run_simulation(bullet_class, num_trials=100, mode=1):
    hits = 0
    distances = []
    times_to_hit = []

    # 創建植物（更靠近城堡的位置）
    plant_offset = 150  # 距離城堡的距離
    plant = Plant(WIDTH//2 - plant_offset, HEIGHT//2)

    for _ in range(num_trials):
        if mode == 1:  # 直線模式 (normal mode)
            # 在左側生成目標，讓它水平移動
            target = Target(0, random.randint(100, HEIGHT-100), mode=mode)
        else:  # 環繞模式
            angle = random.uniform(0, 2 * math.pi)
            radius = 300
            x = int(WIDTH//2 + math.cos(angle) * radius)
            y = int(HEIGHT//2 + math.sin(angle) * radius)
            target = Target(x, y, mode=mode)

        bullet = bullet_class(plant.get_shooter_pos(), target)

        hit = False
        steps = 0

        while steps < 200 and not hit:
            target.update()
            bullet.update()

            if bullet.rect.colliderect(target.rect):
                hit = True
                hits += 1
                times_to_hit.append(steps)
                distances.append(pygame.Vector2(plant.get_shooter_pos()).distance_to(
                    pygame.Vector2(target.rect.center)))
                break
            steps += 1

        if not hit:
            times_to_hit.append(200)
            distances.append(-1)

    return hits, distances, times_to_hit

def plot_results():
    modes = [1, 2]
    trials = 10000

    results = {
        'Old': {'mode1': None, 'mode2': None},
        'New': {'mode1': None, 'mode2': None}
    }

    # 先進行視覺化展示
    print("\n=== Visual Simulation Demo ===")
    for mode in modes:
        mode_name = "Linear" if mode == 1 else "Surround"
        print(f"\n{mode_name} Mode:")

        print("Old Version simulating...")
        old_visual_accuracy = visualize_simulation(OldBullet, mode, 5)
        pygame.time.wait(1000)

        print("New Version simulating...")
        new_visual_accuracy = visualize_simulation(NewBullet, mode, 5)
        pygame.time.wait(1000)

    # 進行大量模擬測試
    print("\n=== Bulk Simulation Test ===")
    print(f"Total trials per mode: {trials}")

    for mode in modes:
        old_hits, old_distances, old_times = run_simulation(OldBullet, trials, mode)
        new_hits, new_distances, new_times = run_simulation(NewBullet, trials, mode)

        results['Old'][f'mode{mode}'] = {
            'hits': old_hits,
            'accuracy': old_hits/trials*100,
            'avg_time': sum(t for t in old_times if t < 200)/old_hits if old_hits > 0 else 0
        }

        results['New'][f'mode{mode}'] = {
            'hits': new_hits,
            'accuracy': new_hits/trials*100,
            'avg_time': sum(t for t in new_times if t < 200)/new_hits if new_hits > 0 else 0
        }

    # 繪製結果圖表
    plt.figure(figsize=(15, 5))

    # 命中率比較
    plt.subplot(131)
    x = np.arange(2)
    width = 0.35
    plt.bar(x - width/2, [results['Old']['mode1']['accuracy'], results['Old']['mode2']['accuracy']],
            width, label='Old Version', color='lightcoral')
    plt.bar(x + width/2, [results['New']['mode1']['accuracy'], results['New']['mode2']['accuracy']],
            width, label='New Version', color='lightgreen')
    plt.ylabel('Accuracy (%)')
    plt.title('Accuracy Comparison')
    plt.xticks(x, ['Linear Mode', 'Surround Mode'])
    plt.legend()

    # 平均命中時間比較
    plt.subplot(132)
    plt.bar(x - width/2, [results['Old']['mode1']['avg_time'], results['Old']['mode2']['avg_time']],
            width, label='Old Version', color='lightcoral')
    plt.bar(x + width/2, [results['New']['mode1']['avg_time'], results['New']['mode2']['avg_time']],
            width, label='New Version', color='lightgreen')
    plt.ylabel('Average Hit Time (frames)')
    plt.title('Hit Time Comparison')
    plt.xticks(x, ['Linear Mode', 'Surround Mode'])
    plt.legend()

    # 改進百分比
    plt.subplot(133)
    improvement_mode1 = (results['New']['mode1']['accuracy'] - results['Old']
                        ['mode1']['accuracy']) / results['Old']['mode1']['accuracy'] * 100
    improvement_mode2 = (results['New']['mode2']['accuracy'] - results['Old']
                        ['mode2']['accuracy']) / results['Old']['mode2']['accuracy'] * 100
    plt.bar(x, [improvement_mode1, improvement_mode2], color='lightblue')
    plt.ylabel('Improvement (%)')
    plt.title('Performance Improvement')
    plt.xticks(x, ['Linear Mode', 'Surround Mode'])

    plt.tight_layout()

    # 保存圖表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'bullet_analysis_{timestamp}.png')
    plt.close()

    # 打印詳細結果
    print(f"\nTotal trials: {trials}")
    print("\nLinear Mode:")
    print(f"Old Version accuracy: {results['Old']['mode1']['accuracy']:.2f}%")
    print(f"New Version accuracy: {results['New']['mode1']['accuracy']:.2f}%")
    print(f"Improvement: {improvement_mode1:.2f}%")
    print("\nSurround Mode:")
    print(f"Old Version accuracy: {results['Old']['mode2']['accuracy']:.2f}%")
    print(f"New Version accuracy: {results['New']['mode2']['accuracy']:.2f}%")
    print(f"Improvement: {improvement_mode2:.2f}%")


if __name__ == "__main__":
    plot_results()   