import arcade
from settings import SCREEN_HEIGHT


class Bullet(arcade.Sprite):
    def __init__(self, filename, scale, pos_x, pos_y, change_y):
        super().__init__(filename, scale)
        self.change_y = change_y
        self.center_x = pos_x
        self.center_y = pos_y
        self.past_y = pos_y

    def on_update(self, delta_time: float = 1 / 60):
        self.past_y = self.center_y
        self.center_y += delta_time * self.change_y
        if self.change_y > 0 and self.center_y - self.height / 2 >= SCREEN_HEIGHT - 100:
            self.remove_from_sprite_lists()
        if self.change_y < 0 and self.center_y < -self.height / 2:
            self.remove_from_sprite_lists()
