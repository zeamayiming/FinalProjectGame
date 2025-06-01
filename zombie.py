import pygame


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.original_image = pygame.transform.scale(img, (50, 50))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 2
        self.speed = 1
        self.attacking = False

    def update(self):
        self.rect.x -= self.speed
        if hasattr(self, 'castle') and self.rect.right <= self.castle.rect.left:
            self.castle.health -= 1
            self.kill()
            return
        for plant in self.plants:
            if self.rect.colliderect(plant.rect):
                plant.health -= 1
                if plant.health <= 0:
                    plant.kill()
                return
        if hasattr(self, 'castle') and self.rect.colliderect(self.castle.rect):
            self.castle.health -= 1
            self.kill()

    def bind_context(self, plants, castle):
        self.plants = plants
        self.castle = castle
