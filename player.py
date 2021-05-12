import arcade
from bullet import Bullet
from settings import SCREEN_WIDTH, SPRITE_SCALE_BULLET, PLAYER_BULLET_SPEED


class Player(arcade.Sprite):
    def __init__(self, filename, scale, bullet_list, mixer, shoot_sound):
        super().__init__(filename, scale)
        self.bullet_list = bullet_list
        self.change_x = 180  # random
        self.right_pressed = False
        self.left_pressed = False
        self.space_pressed = False
        self.mixer = mixer
        self.shoot_sound = shoot_sound

    def shoot_bullet(self):
        bullet = Bullet("Resources/laserRed01.png", SPRITE_SCALE_BULLET, self.center_x, self.center_y + self.height / 2, PLAYER_BULLET_SPEED)
        if len(self.bullet_list) < 1:
            self.mixer.Channel(0).play(self.shoot_sound)
            self.bullet_list.append(bullet)

    def on_update(self, delta_time: float = 1/60):
        if self.right_pressed and not self.left_pressed:
            self.center_x += self.change_x * delta_time
        elif self.left_pressed and not self.right_pressed:
            self.center_x -= self.change_x * delta_time
        if self.center_x - self.width/2 <= 0:
            self.center_x = self.width/2
        elif self.center_x + self.width/2 >= SCREEN_WIDTH:
            self.center_x = SCREEN_WIDTH - self.width/2
        if self.space_pressed:
            self.shoot_bullet()
