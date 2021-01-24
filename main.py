"""
Space Invaders Game
"""
import os
import pathlib
import random
import pygame
import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Space Invaders"
SPRITE_SCALE_ALIENS = 1.5
SPRITE_SCALE_SHIP = 1.5
SPRITE_SCALE_BULLET = 0.5
SPRITE_SCALE_SHIELD = 1
RIGHT = 0
LEFT = 1
ALIEN_STEP = 5
HEIGHT_GAP = 0
PLAYER_BULLET_SPEED = 500
ALIEN_BULLET_SPEED = -350
SHIELD_WIDTH = 100


class Bullet(arcade.Sprite):
    def __init__(self, filename, scale, pos_x, pos_y, change_y):
        super().__init__(filename, scale)
        self.change_y = change_y
        self.center_x = pos_x
        self.center_y = pos_y
        self.past_y = pos_y

    def on_update(self, delta_time: float = 1/60):
        self.past_y = self.center_y
        self.center_y += delta_time * self.change_y
        if self.change_y > 0 and self.center_y - self.height / 2 >= SCREEN_HEIGHT - 100:
            self.remove_from_sprite_lists()
        if self.change_y < 0 and self.center_y < -self.height / 2:
            self.remove_from_sprite_lists()

    def testDraw(self):
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, arcade.color.RED)
        arcade.draw_point(self.center_x - self.width/2, self.center_y - self.height/2, arcade.color.BLUE, 2)


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

    def testDraw(self):
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, arcade.color.RED)
        arcade.draw_point(self.center_x - self.width / 2, self.center_y - self.height / 2, arcade.color.BLUE, 2)


class MyGame(arcade.View):

    def __init__(self):
        super().__init__()
        self.player = None
        self.alien_sprite_list = None
        self.shield_sprite_list = None
        self.player_bullet_list = None
        self.alien_bullet_list = None
        self.gap = None
        self.mixer = None
        self.swoosh_sound = None
        self.alien_bullet_sound = None
        self.ship_bullet_sound = None

        self.alien_height = 0
        self.odds = 0
        self.frame = 0
        self.score = 0
        self.lives = 0

    def alien_setup(self):
        # aliens setup
        self.odds -= 20
        alien_template = arcade.Sprite("Resources/InvaderA_00.png", SPRITE_SCALE_ALIENS)
        width = SCREEN_WIDTH - alien_template.width * 4
        self.gap = (width - alien_template.width * 11) / 10
        global HEIGHT_GAP
        HEIGHT_GAP = (SCREEN_HEIGHT - 200 - 10 * alien_template.height) / 9
        self.alien_height = alien_template.height

        for row in range(5):
            for i in range(11):
                if row == 0:
                    alien = Alien("Resources/InvaderC_00.png", SPRITE_SCALE_ALIENS * 2 / 3,
                                  arcade.load_texture("Resources/InvaderC_01.png"), self.alien_bullet_list, 40,
                                  alien_template.height)
                elif row < 3:
                    alien = Alien("Resources/InvaderB_00.png", SPRITE_SCALE_ALIENS,
                                  arcade.load_texture("Resources/InvaderB_01.png"), self.alien_bullet_list, 20,
                                  alien_template.height)
                else:
                    alien = Alien("Resources/InvaderA_00.png", SPRITE_SCALE_ALIENS,
                                  arcade.load_texture("Resources/InvaderA_01.png"), self.alien_bullet_list, 10,
                                  alien_template.height)
                alien.center_x = alien_template.width + i * (
                            alien_template.width + self.gap) + alien_template.width / 2  # center with border to move
                alien.center_y = SCREEN_HEIGHT - 120 - row * (alien_template.height + HEIGHT_GAP)
                self.alien_sprite_list.append(alien)

    def on_show(self):
        """ Set up the game here. Call this function to restart the game. """
        self.lives = 3
        self.frame = 0
        self.odds = 120
        self.alien_sprite_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.alien_bullet_list = arcade.SpriteList()
        self.shield_sprite_list = arcade.SpriteList()

        self.mixer = pygame.mixer
        self.mixer.init(channels=4)  # 0 - playershoot, 1 - alien swoosh, 2 - alien shoot
        self.swoosh_sound = self.mixer.Sound('Resources/swoosh.wav')
        self.alien_bullet_sound = self.mixer.Sound('Resources/InvaderBullet.wav')
        self.ship_bullet_sound = self.mixer.Sound('Resources/ShipBullet.wav')
        self.mixer.Channel(0).set_volume(0.1)
        self.mixer.Channel(1).set_volume(0.1)
        self.mixer.Channel(2).set_volume(0.1)

        self.player = Player("Resources/Ship.png", SPRITE_SCALE_SHIP, self.player_bullet_list,
                             self.mixer, self.ship_bullet_sound)
        self.player.center_x = SCREEN_WIDTH / 2 + self.player.width/2
        self.player.center_y = 50

        self.alien_setup()

        gap_width = (SCREEN_WIDTH - 4 * SHIELD_WIDTH) / 5
        for i in range(4):
            self.make_shield(gap_width + i * (gap_width + SHIELD_WIDTH),
                             gap_width + SHIELD_WIDTH + i * (gap_width + SHIELD_WIDTH))

    def make_shield(self, x, max_x):
        i = x
        j = 160
        min_j = j - self.alien_height * 1.5

        shield = arcade.Sprite("Resources/Shield.png", SPRITE_SCALE_SHIELD)
        while i < max_x:
            while j > min_j:
                shield = arcade.Sprite("Resources/Shield.png", SPRITE_SCALE_SHIELD)
                shield.center_x = i
                shield.center_y = j
                self.shield_sprite_list.append(shield)
                j -= shield.height
            i += shield.width
            j = 160

    def game_over(self):
        game_over = GameOver()
        self.window.show_view(game_over)

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        arcade.draw_line(0, 100, SCREEN_WIDTH, 100, arcade.color.GREEN)
        arcade.draw_line(0, 1, SCREEN_WIDTH, 1, arcade.color.GREEN)
        arcade.draw_text("LIVES: " + str(self.lives), 50, 5, arcade.color.WHITE, 25)
        self.player.draw()
        self.alien_sprite_list.draw()
        self.player_bullet_list.draw()
        self.alien_bullet_list.draw()
        self.shield_sprite_list.draw()
        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 100, arcade.color.BLACK)
        arcade.draw_line(0, SCREEN_HEIGHT-100, SCREEN_WIDTH, SCREEN_HEIGHT-100, arcade.color.GREEN)
        arcade.draw_text("SCORE: " + str(self.window.score), 50, SCREEN_HEIGHT - 50, arcade.color.WHITE, 25)
        # for bullet in self.player_bullet_list:
        #     bullet.testDraw()
        # for alien in self.alien_sprite_list:
        #     alien.testDraw()

    def on_update(self, dt):
        """ Update everything """
        self.player.on_update(dt)
        self.player_bullet_list.on_update(dt)
        self.alien_bullet_list.on_update(dt)

        if self.frame > 50/(200 - 2 * len(self.alien_sprite_list)):  # random values
            self.alien_sprite_list.update()
            if len(self.alien_sprite_list) > 0:
                self.mixer.Channel(1).play(self.swoosh_sound)
            self.frame = 0
            collision = False
            for alien in self.alien_sprite_list:
                if alien.direction == RIGHT and alien.center_x + alien.width / 2 + 5 >= SCREEN_WIDTH:
                    collision = True
                if alien.direction == LEFT and alien.center_x - alien.width / 2 - 5 <= 0:
                    collision = True
            if collision:
                for alien in self.alien_sprite_list:
                    alien.change_direction()

        # Have a random 1 in x change of shooting each 1/60th of a second (each frame in 60 fps)
        adj_odds = int(self.odds * (1 / 60) / dt)
        if random.randrange(adj_odds) == 0:
            if len(self.alien_sprite_list) > 1:
                self.mixer.Channel(2).play(self.alien_bullet_sound)
                alien = random.randrange(0, len(self.alien_sprite_list) - 1, 1)
                alien = self.alien_sprite_list[alien]
                alien.shoot_bullet()
            elif len(self.alien_sprite_list) > 0:
                self.mixer.Channel(2).play(self.alien_bullet_sound)
                alien = self.alien_sprite_list[0]
                alien.shoot_bullet()

        for bullet in self.player_bullet_list:
            hit_list_alien = arcade.check_for_collision_with_list(bullet, self.alien_sprite_list)
            hit_list_alien_bullets = arcade.check_for_collision_with_list(bullet, self.alien_bullet_list)
            hit_list_shield = arcade.check_for_collision_with_list(bullet, self.shield_sprite_list)
            if len(hit_list_shield) > 0:
                for s in hit_list_shield:
                    s.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
            if len(hit_list_alien_bullets) > 0:
                for b in hit_list_alien_bullets:
                    b.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
            for alien in hit_list_alien:
                self.window.score += alien.score
                alien.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()

        hit_list = arcade.check_for_collision_with_list(self.player, self.alien_bullet_list)
        if len(hit_list) > 0:
            self.lives -= 1
            while len(self.alien_bullet_list) > 0:
                for bullet in self.alien_bullet_list:
                    bullet.remove_from_sprite_lists()

        for bullet in self.alien_bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_sprite_list)
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
            for s in hit_list:
                s.remove_from_sprite_lists()

        if len(self.alien_sprite_list) == 0:
            self.alien_setup()

        for alien in self.alien_sprite_list:
            if alien.too_low():
                self.game_over()

        if self.lives <= 0:
            self.game_over()
        if len(self.shield_sprite_list) == 0:
            self.game_over()

        self.frame += dt

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.player.right_pressed = True
        elif key == arcade.key.SPACE:
            self.player.space_pressed = True
        elif key == arcade.key.ESCAPE:
            self.game_over()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.player.right_pressed = False
        elif key == arcade.key.SPACE:
            self.player.space_pressed = False


class GameOver(arcade.View):

    def __init__(self):
        super().__init__()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Game Over", 240, 400, arcade.color.WHITE, 54)
        arcade.draw_text("Press Spacebar to restart", 240, 300, arcade.color.WHITE, 24)

        output_total = f"Total Score: {self.window.score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.window.score = 0
            game = MyGame()
            self.window.show_view(game)
        elif key == arcade.key.ESCAPE:
            self.window.close()


class StartGame(arcade.View):

    def __init__(self):
        super().__init__()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Press Spacebar to start", 220, 300, arcade.color.WHITE, 30)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game = MyGame()
            self.window.show_view(game)
        elif key == arcade.key.ESCAPE:
            self.window.close()


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_vsync(True)
    window.score = 0
    view = StartGame()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
