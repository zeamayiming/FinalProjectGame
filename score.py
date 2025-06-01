# 分數動畫顯示功能


class Score_display:
    def __init__(self, font, color=(0, 0, 0)):
        self.score = 0
        self.displayed_score = 0
        self.font = font
        self.color = color
        self.done = True

    def add(self, amount):
        self.score += amount
        self.done = False

    def update(self):
        if self.displayed_score < self.score:
            self.displayed_score += min(self.score //
                                        120, self.score - self.displayed_score)
        else:
            self.done = True

    def draw(self, screen, x, y):
        text = self.font.render(
            f"Score: {self.displayed_score}", True, self.color)
        rect = text.get_rect(centerx=x, bottom=y+130)
        screen.blit(text, rect)
