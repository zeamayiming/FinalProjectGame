import pygame
import os


class Button:
    def __init__(self, image_path, center_pos, hover_scale=1.1, padding=10):
        self.original_image = pygame.image.load(
            os.path.join("pic", image_path)).convert_alpha()
        self.original_image = pygame.transform.smoothscale(
            self.original_image, (50, 50))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=center_pos)

        # 底下方塊尺寸稍微比圖片大一點
        self.bg_rect = pygame.Rect(
            0, 0, self.rect.width + padding * 2, self.rect.height + padding * 2)
        self.bg_rect.center = self.rect.center

        self.base_color = (0, 0, 0)
        self.hover_color = (180, 180, 180)
        self.current_color = self.base_color

        self.hover_scale = hover_scale
        self.is_hovered = False

    def update(self, mouse_pos):
        if self.bg_rect.collidepoint(mouse_pos):
            if not self.is_hovered:
                self._apply_scale(self.hover_scale)
                self.is_hovered = True
            self.current_color = self.hover_color
        else:
            if self.is_hovered:
                self._apply_scale(1 / self.hover_scale)
                self.is_hovered = False
            self.current_color = self.base_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.bg_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.bg_rect, 2)  # 外框
        surface.blit(self.image, self.rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.bg_rect.collidepoint(event.pos)

    def _apply_scale(self, factor):
        center = self.rect.center
        w, h = self.original_image.get_size()
        scaled_size = (int(w * factor), int(h * factor))
        self.image = pygame.transform.smoothscale(
            self.original_image, scaled_size)
        self.rect = self.image.get_rect(center=center)
        self.bg_rect = self.rect.inflate(20, 20)
