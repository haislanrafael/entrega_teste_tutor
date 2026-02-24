import pgzrun
from pygame import Rect
import pygame

# ==============================
# Audio initialization
# ==============================

pygame.mixer.init()

try:
    background_music = pygame.mixer.Sound("music/background.wav")
    background_music.set_volume(0.5)
    music_loaded = True
except:
    music_loaded = False
    print("Failed to load background music.")

# ==============================
# Window settings
# ==============================

WIDTH = 500
HEIGHT = 300
TITLE = "Roguelike Adventure"

TILE_SIZE = 50
ROWS = HEIGHT // TILE_SIZE
COLS = WIDTH // TILE_SIZE

# ==============================
# Game state control
# ==============================

game_state = "menu"
sound_enabled = True

# ==============================
# Button class
# ==============================

class Button:
    def __init__(self, text, center):
        self.text = text
        self.rect = Rect((0, 0), (200, 50))
        self.rect.center = center

    def draw(self):
        screen.draw.filled_rect(self.rect, (40, 40, 40))
        screen.draw.rect(self.rect, (255, 255, 255))
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color="white")

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ==============================
# Hero class
# ==============================

class Hero:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y

        # Convert grid position to screen position
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2

        # Target position for smooth movement
        self.target_x = self.x
        self.target_y = self.y

        self.speed = 0.2
        self.moving = False

        self.actor = Actor("hero_idle_1")
        self.actor.pos = (self.x, self.y)

    def move(self, key):
        # Prevent movement while already moving
        if self.moving:
            return

        if key == keys.LEFT and self.grid_x > 0:
            self.grid_x -= 1
        elif key == keys.RIGHT and self.grid_x < COLS - 1:
            self.grid_x += 1
        elif key == keys.UP and self.grid_y > 0:
            self.grid_y -= 1
        elif key == keys.DOWN and self.grid_y < ROWS - 1:
            self.grid_y += 1
        else:
            return

        # Update target position
        self.target_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.target_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.moving = True

    def update(self):
        # Smooth movement towards target position
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        if abs(dx) > 1 or abs(dy) > 1:
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            # Snap to final position
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False

        self.actor.pos = (self.x, self.y)

# ==============================
# Enemy class
# ==============================

class Enemy:
    def __init__(self, grid_x, grid_y, min_x, max_x):
        self.grid_x = grid_x
        self.grid_y = grid_y

        # Movement boundaries
        self.min_x = min_x
        self.max_x = max_x

        self.direction = 1  # 1 = right, -1 = left

        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2

        self.target_x = self.x
        self.speed = 0.05

        self.actor = Actor("enemy")
        self.actor.pos = (self.x, self.y)

    def update(self):
        # Automatic horizontal movement
        self.target_x = (self.grid_x + self.direction) * TILE_SIZE + TILE_SIZE // 2
        dx = self.target_x - self.x

        if abs(dx) > 1:
            self.x += dx * self.speed
        else:
            # Move to next grid cell
            self.grid_x += self.direction

            # Reverse direction at boundaries
            if self.grid_x <= self.min_x or self.grid_x >= self.max_x:
                self.direction *= -1

        self.actor.pos = (self.x, self.y)

# ==============================
# Instances
# ==============================

start_button = Button("Start Game", (WIDTH // 2, 100))
sound_button = Button("Music: ON", (WIDTH // 2, 170))
exit_button = Button("Exit", (WIDTH // 2, 240))

hero = Hero(2, 2)
enemy = Enemy(1, 4, 1, 7)

# ==============================
# Draw functions
# ==============================

def draw():
    screen.clear()

    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()

def draw_menu():
    screen.fill((30, 0, 0))
    screen.draw.text("MAIN MENU", center=(WIDTH // 2, 40), fontsize=40, color="white")
    start_button.draw()
    sound_button.draw()
    exit_button.draw()

def draw_game():
    screen.fill((0, 40, 0))
    hero.actor.draw()
    enemy.actor.draw()

def draw_game_over():
    screen.fill("black")
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 20), fontsize=50, color="red")
    screen.draw.text("Press R to Restart", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=30, color="white")

# ==============================
# Update loop
# ==============================

def update():
    global game_state

    if game_state == "playing":
        hero.update()
        enemy.update()

        # Collision check
        if hero.grid_x == enemy.grid_x and hero.grid_y == enemy.grid_y:
            game_state = "game_over"
            if music_loaded:
                background_music.stop()

# ==============================
# Input handling
# ==============================

def on_mouse_down(pos):
    global game_state, sound_enabled

    if game_state == "menu":

        if start_button.is_clicked(pos):
            game_state = "playing"
            if sound_enabled and music_loaded:
                background_music.play(-1)

        elif sound_button.is_clicked(pos):
            sound_enabled = not sound_enabled

            if sound_enabled:
                sound_button.text = "Music: ON"
            else:
                sound_button.text = "Music: OFF"
                if music_loaded:
                    background_music.stop()

        elif exit_button.is_clicked(pos):
            exit()

def on_key_down(key):
    global game_state

    if game_state == "playing":
        hero.move(key)

    if game_state == "game_over" and key == keys.R:
        reset_game()

# ==============================
# Reset game state
# ==============================

def reset_game():
    global hero, enemy, game_state

    hero = Hero(2, 2)
    enemy = Enemy(1, 4, 1, 7)

    game_state = "menu"

pgzrun.go()