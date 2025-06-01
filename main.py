import pygame
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 500, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("<看到幫我加分> 選單")
font = pygame.font.SysFont("微軟正黑體", 48)

# 控制遊戲更新速度(幀率)
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 102, 204)


def draw_button(text, rectangle, hover=False):
    color = DARK_GRAY if hover else BLACK
    pygame.draw.rect(screen, color, rectangle)
    label = font.render(text, True, WHITE)  # 將文字轉成圖片
    label_rect = label.get_rect(center=rectangle.center)
    screen.blit(label, label_rect)  # 將圖片或文字貼到畫面上(圖片)


def main_menu():
    normal_button = pygame.Rect(WIDTH // 2 - 150, 200, 300, 80)
    surround_button = pygame.Rect(WIDTH // 2 - 150, 320, 300, 80)
    quit_button = pygame.Rect(WIDTH // 2 - 150, 440, 300, 80)

    while True:
        screen.fill("silver")
        font = pygame.font.SysFont("微軟正黑體", 56)
        title = font.render("Choose the game model", True, (129, 19, 49))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        mouse_pos = pygame.mouse.get_pos()

        draw_button("normal_mode", normal_button,
                    normal_button.collidepoint(mouse_pos))
        draw_button("360_mode", surround_button,
                    surround_button.collidepoint(mouse_pos))
        draw_button("Quit game", quit_button,
                    quit_button.collidepoint(mouse_pos))

        # 監聽事件(滑鼠位置)
        for event in pygame.event.get():
            # 點擊右上叉叉
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 按下滑鼠鍵，判斷執行腳本
            if event.type == pygame.MOUSEBUTTONDOWN:
                if normal_button.collidepoint(mouse_pos):
                    pygame.quit()
                    subprocess.run(["python", "normal_mode.py"])
                    sys.exit()
                elif surround_button.collidepoint(mouse_pos):
                    subprocess.run(["python", "surround_mode.py"])
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
