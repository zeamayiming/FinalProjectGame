import pygame
import random
import os
import config

from word_bank_data import word_bank
from castle import Castle
from zombie import Zombie
from plant import Plant
from button import Button
from score import Score_display
from scoreboard import get_scoreboard_text, save_score

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# 字型
font = pygame.font.SysFont(None, 72)
feedback_font = pygame.font.SysFont(None, 48)

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("好壞喔！！從左邊來")
clock = pygame.time.Clock()
FPS = 60

# 初始化變數
word = random.choice(word_bank)
input_index = 0
letter_status = ["pending"] * len(word)
feedback = ""
score = 200
box_size = 70
margin = 10
start_y = 615
score_display = Score_display(feedback_font)
transparent_rect = pygame.Surface((67.5, 67.5), pygame.SRCALPHA)
transparent_rect.fill((0, 0, 0, 128))  # 黑色、透明度 128（中度透明）
start_ticks = pygame.time.get_ticks()  # 遊戲開始時間
level = 1                              # 初始關卡
zombie_speed = 1.0                     # 初始殭屍速度
LEVEL_INTERVAL = 10                    # 每10秒升級一次


# 載入圖片
castle_img = pygame.image.load(os.path.join(
    "pic", "castle_3.png")).convert_alpha()
zombie_img = pygame.image.load(
    os.path.join("pic", "ゴリ橋 和之.png")).convert_alpha()

# 遊戲實體
castle = Castle(castle_img)
all_sprites = pygame.sprite.Group()
zombie_sprites = pygame.sprite.Group()
zombie = Zombie(100, 200, zombie_img)
cha = 1
zombie.speed = cha
plants = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
all_sprites.add(castle)

zombie_timer = pygame.time.get_ticks()
zombie_interval = 1000
game_over = False
button_rect = pygame.Rect(12.5, 100, 75, 75)
paused = False

input_active = True
name_input = ""
show_scoreboard = False


stop = config.speed_stop
wrong = config.Wrong
button_stop = [0, 0, 0, 0, 0]

# 在畫面左邊由上到下排列 5 個技能按鈕
buttons = []
for i in range(5):
    image_path = f"skill_{i + 1}.png"
    pos = (50, 125 + i * 110)
    buttons.append(Button(image_path, pos))

button_costs = [5, 30, 30, 30, 30]  # 每個技能所需積分

# 音效
if not game_over:
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


# 繪圖函式
def draw_health_bar(surf, hp, max_hp, x, y):
    BAR_LENGTH = 40
    BAR_HEIGHT = 6
    fill = max(0, (hp / max_hp) * BAR_LENGTH)
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, config.DARK_RED, outline_rect)
    pygame.draw.rect(surf, config.DARK_GREEN, fill_rect)
    pygame.draw.rect(surf, config.BLACK, outline_rect, 1)


def draw_range(surface, x, y, radius):
    pygame.draw.circle(surface, config.BLACK, (x, y), radius, 1)


def reset_word():
    global word, input_index, letter_status, feedback
    word = random.choice(word_bank)
    input_index = 0
    letter_status = ["pending"] * len(word)
    feedback = ""


def draw_word():
    total_width = len(word) * (box_size + margin)
    start_x = max(100, min(config.WIDTH - total_width - 100,
                  (config.WIDTH - total_width) // 2 + 50))
    for i, char in enumerate(word):
        x = start_x + i * (box_size + margin)
        color = config.GRAY if letter_status[i] == "pending" else config.GREEN if letter_status[i] == "correct" else config.RED
        pygame.draw.rect(screen, color, (x, start_y, box_size, box_size))
        pygame.draw.rect(screen, config.BLACK,
                         (x, start_y, box_size, box_size), 3)
        text_surface = font.render(char.upper(), True, config.BLACK)
        text_rect = text_surface.get_rect(
            center=(x + box_size // 2, start_y + box_size // 2))
        screen.blit(text_surface, text_rect)


def draw_feedback():
    if feedback:
        text = feedback_font.render(
            feedback, True, (0, 125, 125) if feedback == "correct" else config.RED)
        text_rect = text.get_rect()
        text_rect.centerx = config.WIDTH // 2 + 50
        text_rect.top = start_y - 60
        pygame.draw.rect(screen, config.WHITE, text_rect.inflate(20, 10))
        pygame.draw.rect(screen, config.BLACK, text_rect.inflate(20, 10), 2)
        screen.blit(text, text_rect)


# 積分
def draw_score():
    integral_font = pygame.font.SysFont("Segoe UI Symbol", 36)
    integral_text = integral_font.render(
        f"∫:{score}", True, config.BLACK)
    screen.blit(integral_text, (2, 10))

# 顯示排行榜


# ... existing code ...

def draw_scoreboard():
    lines = get_scoreboard_text("normal")
    box_width = 400
    box_height = 40 * len(lines) + 40
    box_rect = pygame.Rect(0, 0, box_width, box_height)
    box_rect.centerx = config.WIDTH // 2
    box_rect.centery = config.HEIGHT // 2
    pygame.draw.rect(screen, config.WHITE, box_rect)
    pygame.draw.rect(screen, config.BLACK, box_rect, 2)
    y = box_rect.top + 20
    for line in lines:
        text = pygame.font.SysFont(None, 32).render(line, True, (0, 0, 0))
        screen.blit(text, (box_rect.left + 20, y))
        y += 35

# ... existing code ...

        if event.type == pygame.KEYDOWN and game_over and input_active:
            if event.key == pygame.K_RETURN:
                save_score(name_input, score_display.score, "normal")
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                name_input = name_input[:-1]
            else:
                if len(name_input) < 10 and event.unicode.isprintable():
                    name_input += event.unicode

# ... existing code ...


def draw_rect(s):
    screen.blit(transparent_rect, (17.5, 92.5 + s * 110))

    # 顯示冷卻倒數數字
    font_small = pygame.font.SysFont(None, 24)
    seconds = button_stop[s] // FPS + 1
    text_surface = font_small.render(f"{seconds}", True, config.WHITE)
    text_rect = text_surface.get_rect(center=(15 + 35, 90 + s * 110 + 35))
    screen.blit(text_surface, text_rect)


# 遊戲主迴圈
running = True
while running:
    if stop > 0:
        stop -= 1
    if wrong > 0:
        wrong -= 1

    # 計算遊戲經過秒數
    seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
    new_level = seconds_passed // LEVEL_INTERVAL + 1

    if new_level > level:
        level = new_level
        zombie_speed += 0.2  # 提升殭屍速度

    clock.tick(FPS)
    screen.fill(config.WHITE)
    pygame.draw.rect(screen, config.GRASS_GREEN, (config.GRASS_X_LEFT, config.GRASS_Y_TOP,
                     config.GRASS_X_RIGHT - config.GRASS_X_LEFT, config.GRASS_Y_BOTTOM - config.GRASS_Y_TOP))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = pygame.mouse.get_pos()
            if config.GRASS_X_LEFT + 70 <= x <= config.GRASS_X_RIGHT and config.GRASS_Y_TOP <= y <= config.GRASS_Y_BOTTOM and score >= 3:
                temp_plant = Plant(x, y)
                temp_plant.set_bullet_image(zombie_img)
                collides = any(temp_plant.rect.colliderect(e.rect)
                               for e in enemies) or temp_plant.rect.colliderect(castle.rect)
                if not collides:
                    plants.add(temp_plant)
                    all_sprites.add(temp_plant)
                    score -= 3
                    score_display.add(-3)
        # button 技能功能
        for i, btn in enumerate(buttons):
            if btn.is_clicked(event) and not game_over and button_stop[i] == 0:
                if i == 0 and score >= 5:
                    score -= 5
                    bonus = random.randint(0, 10)
                    score += bonus
                    score_display.add(bonus - 5)
                    button_stop[0] = 100
                if i == 1 and score >= 30:
                    score -= 30
                    score_display.add(-30)
                    for zombie in zombie_sprites:
                        zombie.kill()
                    button_stop[1] = 100
                    print(button_stop)
                if i == 2 and score >= 30:
                    score -= 30
                    score_display.add(-30)
                    stop = 100
                    button_stop[2] = 1000
                if i == 3 and score >= 30:
                    score -= 30
                    score_display.add(-30)
                    castle.health = config.blood_max
                    button_stop[3] = 100
                if i == 4 and score >= 30:
                    score -= 30
                    score_display.add(2470)
                    button_stop[4] = 100

        if event.type == pygame.KEYDOWN and game_over and input_active:
            if event.key == pygame.K_RETURN:
                save_score(name_input, score_display.score, "normal")
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                name_input = name_input[:-1]
            else:
                if len(name_input) < 10 and event.unicode.isprintable():
                    name_input += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if rank_btn.collidepoint(event.pos):
                show_scoreboard = not show_scoreboard

        if event.type == pygame.KEYDOWN and not game_over:
            if input_index < len(word):
                key_char = event.unicode.upper()
                expected_char = word[input_index].upper()
                if key_char.isalpha() and len(key_char) == 1:
                    if key_char == expected_char:
                        letter_status[input_index] = "correct"
                        input_index += 1
                        if input_index == len(word):
                            feedback = "correct"
                            points = max(1, min(len(word), 7))
                            score += points
                            score_display.add(points)
                            pygame.time.set_timer(pygame.USEREVENT, 300)
                    else:
                        score -= 2
                        score_display.add(-2)
                        wrong = 100
                        cha = config.Wrong_speed
                        for zombie in zombie_sprites:
                            zombie.speed = config.Wrong_speed
                        letter_status[input_index] = "wrong"
                        feedback = "wrong"
                        pygame.time.set_timer(pygame.USEREVENT, 300)
        elif event.type == pygame.USEREVENT:
            reset_word()
            pygame.time.set_timer(pygame.USEREVENT, 0)

    if not game_over:
        now = pygame.time.get_ticks()
        if now - zombie_timer >= zombie_interval:
            zombie_timer = now
            x = random.randint(config.ZOMBIE_SPAWN_X, config.WIDTH)
            y = random.randint(config.GRASS_Y_TOP + 30,
                               config.GRASS_Y_BOTTOM - 20)
            zombie = Zombie(x, y, zombie_img)
            zombie.speed = zombie_speed  # 使用當前關卡速度
            zombie_sprites.add(zombie)

            zombie.bind_context(plants, castle)
            enemies.add(zombie)
            zombie_sprites.add(zombie)

        for plant in plants:
            bullet = plant.shoot(enemies)
            if bullet:
                bullet.score_display = score_display
                bullets.add(bullet)
                all_sprites.add(bullet)

        # 所有物件(血條 -> 植物、城堡... -> 左側邊框 -> 技能按鈕 -> Game over)
        all_sprites.update()
        if stop == 0:
            zombie_sprites.update()
        for enemy in enemies:
            draw_health_bar(screen, enemy.health, 2,
                            enemy.rect.x + 5, enemy.rect.y - 8)
        for plant in plants:
            draw_health_bar(screen, plant.health, 10,
                            plant.rect.x + 0.75, plant.rect.y - 10)
            draw_range(screen, plant.rect.centerx,
                       plant.rect.centery, plant.range)
        draw_health_bar(screen, castle.health, 5,
                        castle.rect.x + 27.5, castle.rect.y + 100)

        for button in buttons:
            button.update(pygame.mouse.get_pos())

        if castle.health <= 0:
            game_over = True

    all_sprites.draw(screen)
    zombie_sprites.draw(screen)
    pygame.draw.rect(screen, config.WHITE, (0, 0, 100, 1200))
    for button in buttons:
        button.draw(screen)
    pygame.draw.rect(screen, config.WHITE, (100, 600, 1200, 600))
    pygame.draw.line(screen, config.RED, (castle.rect.left, 0),
                     (castle.rect.left, 600), 3)
    pygame.draw.line(screen, config.BLACK, (config.ZOMBIE_SPAWN_X, 0),
                     (config.ZOMBIE_SPAWN_X, 600), 3)
    pygame.draw.line(screen, config.BLACK, (100, 600), (1200, 600), 3)
    pygame.draw.line(screen, config.BLACK, (100, 0), (100, 700), 3)

    # 畫倒數計時透明框
    integral_font = pygame.font.SysFont("Segoe UI Symbol", 16)
    for i in range(len(buttons)):
        btn = buttons[i]
        # 顯示技能價格
        color = config.RED if score < button_costs[i] else config.BLACK
        cost_text = integral_font.render(f"{button_costs[i]}∫", True, color)
        cost_rect = cost_text.get_rect(
            center=(btn.rect.centerx, btn.rect.bottom + 20))
        screen.blit(cost_text, cost_rect)

        if button_stop[i] > 0 and not game_over:
            button_stop[i] -= 1
            draw_rect(i)

    level_text = font.render(f"Level: {level} ", True, (0, 0, 0))
    screen.blit(level_text, (config.WIDTH - 300, 0))

    if event.type == pygame.KEYDOWN and game_over and input_active:
        if event.key == pygame.K_RETURN:
            save_score(name_input, score_display.score, "normal")
            input_active = False
        elif event.key == pygame.K_BACKSPACE:
            name_input = name_input[:-1]
        else:
            if len(name_input) < 10 and event.unicode.isprintable():
                name_input += event.unicode

    if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
        with open("scores.json", "w", encoding="utf-8") as f:
            json.dump([], f)

    draw_word()
    draw_feedback()
    draw_score()

    # 結算畫面
    if game_over:

        screen.fill(config.papayawhip)

        score_display.update()
        score_display.draw(screen, config.WIDTH // 2, config.HEIGHT // 2 - 80)
        font_game_over = pygame.font.SysFont("微軟正黑體", 100)
        text = font_game_over.render("Game Over", True, config.RED)
        screen.blit(text, (config.WIDTH // 2 - text.get_width() //
                           2, config.HEIGHT // 2 - text.get_height() * 1.3))

        pygame.draw.rect(screen, (200, 200, 200), (config.WIDTH //
                         2 - 100, config.HEIGHT//2 + 75, 200, 40))
        font_name = pygame.font.SysFont(None, 36)
        name_text = font_name.render(
            name_input or "Enter your name...", True, (0, 0, 0))
        screen.blit(name_text, (config.WIDTH//2 - 90, config.HEIGHT//2 + 80))

        # 1. 建立按鈕 rect，讓它在畫面底部中間
        rank_btn = pygame.Rect(0, 0, 100, 40)
        rank_btn.centerx = config.WIDTH // 2
        rank_btn.centery = config.HEIGHT // 10 * 7

        # 2. 畫按鈕（黑底 + 白邊）
        pygame.draw.rect(screen, (0, 0, 0), rank_btn)
        pygame.draw.rect(screen, (255, 255, 255), rank_btn, 2)

        # 3. 顯示文字並置中對齊在按鈕中
        rank_label = font_name.render("Rank", True, (255, 255, 255))
        label_rect = rank_label.get_rect(center=rank_btn.center)
        screen.blit(rank_label, label_rect)
        if show_scoreboard:
            draw_scoreboard()

    pygame.display.flip()
pygame.quit()
