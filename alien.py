import arcade
from bullet import Bullet
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, RIGHT, LEFT, ALIEN_STEP, SPRITE_SCALE_BULLET, ALIEN_BULLET_SPEED


class BonusAlien(arcade.Sprite):
    def __init__(self, filename, scale, direction):
        super().__init__(filename, scale)
        self.vel = 200
        self.direction = direction
        self.center_y = SCREEN_HEIGHT - 120
        if dir == LEFT:
            self.center_x = SCREEN_WIDTH + self.width/2
        else:
            self.center_x = -self.width / 2

    def on_update(self, dt):
        if self.direction == LEFT:
            self.center_x -= self.vel * dt
        else:
            self.center_x += self.vel * dt
        if self.center_x + self.width/2 < 0:
            self.remove_from_sprite_lists()
        elif self.center_x - self.width/2 > SCREEN_WIDTH:
            self.remove_from_sprite_lists()


class Alien(arcade.Sprite):
    def __init__(self, filename, scale, texture, bullets, score, height):
        super().__init__(filename, scale)
        self.bullet_list = bullets
        self.append_texture(texture)
        self.direction = RIGHT
        self.change_row_now = False
        self.texture_frame = 0
        self.score = score
        self.alien_height = height

    def update(self):
        if self.change_row_now:
            self.change_row_now = False
            self.change_row()
        else:
            if self.direction == RIGHT:
                self.center_x += ALIEN_STEP
            else:
                self.center_x -= ALIEN_STEP
            self.texture_frame = 1 - self.texture_frame
            self.set_texture(self.texture_frame)

    def change_direction(self):
        self.direction = 1 - self.direction  # 0->1 1->0
        self.change_row_now = True

    def change_row(self):
        self.center_y -= self.alien_height

    def shoot_bullet(self):
        bullet = Bullet("Resources/blueLaser.png", SPRITE_SCALE_BULLET, self.center_x, self.center_y + self.height / 2, ALIEN_BULLET_SPEED)
        bullet.angle = 180
        self.bullet_list.append(bullet)

    def too_low(self):
        return self.center_y - self.alien_height <= 100
