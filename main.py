"""
Flappy Bird Clone - A Python implementation using Pygame
Features:
- Classic gameplay mechanics
- Sound effects and background music
- Persistent high score system
- Volume control interface
"""

import pygame
import random
import requests
import io
import os
import tempfile
from typing import List, Tuple, Dict, Optional, Union, Final

# Initialize Pygame and core components
pygame.init()
clock: pygame.time.Clock = pygame.time.Clock()
font: pygame.font.Font = pygame.font.SysFont("Arial", 24)

# Game Constants (using Final for compile-time constants)
SCREEN_WIDTH: Final[int] = 288
SCREEN_HEIGHT: Final[int] = 512
GRAVITY: Final[float] = 0.2425
FLAP_STRENGTH: Final[int] = -6
PIPE_GAP: Final[int] = 100
PIPE_FREQ: Final[int] = 1500
HIGHSCORE_FILE: Final[str] = "highscore.txt"

screen: pygame.surface.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Strict type definitions for all game state
sprite_urls: Dict[str, str] = {
    "background": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/sprites/background-day.png",
    "bird": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/sprites/redbird-midflap.png",
    "base": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/sprites/base.png",
    "pipe": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/sprites/pipe-green.png",
}

sound_urls: Dict[str, str] = {
    "flap": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/audio/wing.wav",
    "hit": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/audio/hit.wav",
    "score": "https://raw.githubusercontent.com/sourabhv/FlapPyBird/master/assets/audio/point.wav",
}

# Asset types
background: pygame.surface.Surface
bird_img: pygame.surface.Surface
base_img: pygame.surface.Surface
pipe_img: pygame.surface.Surface
pipe_flipped: pygame.surface.Surface

sound_flap: pygame.mixer.Sound
sound_hit: pygame.mixer.Sound
sound_score: pygame.mixer.Sound

# Game state variables with strict typing
bird: pygame.Rect
bird_movement: float
pipes: List[Tuple[pygame.Rect, pygame.Rect]]
base_x: int
score: int
game_active: bool
high_score: int
music_volume: float
sfx_volume: float
show_volume_ui: bool


def load_image_from_url(url: str) -> pygame.surface.Surface:
    """Download an image and return a converted pygame.Surface."""
    # small timeout so a network hiccup doesn't hang the game
    response = requests.get(url, timeout=5)
    image_file = io.BytesIO(response.content)
    return pygame.image.load(image_file).convert_alpha()


def load_sound_from_url(url: str) -> pygame.mixer.Sound:
    """Download a wav and return a pygame Sound object (temporary file used)."""
    response = requests.get(url, timeout=5)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(response.content)
        tmpfile.flush()
        temp_name = tmpfile.name

    sound = pygame.mixer.Sound(temp_name)
    os.unlink(temp_name)
    return sound


def load_highscore() -> int:
    """Load high score from disk, return 0 if not present or on error."""
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except ValueError:
                # corrupted file, reset to 0
                return 0
    return 0


def save_highscore(score: int) -> None:
    """Persist high score to disk."""
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


def reset_game() -> None:
    """Reset or initialize all runtime game state variables."""
    global bird, bird_movement, pipes, base_x, score, game_active
    bird = bird_img.get_rect(center=(50, SCREEN_HEIGHT // 2))
    bird_movement = 0.0
    pipes = []
    base_x = 0
    score = 0
    game_active = True


def create_pipe() -> Tuple[pygame.Rect, pygame.Rect]:
    """Create a new top/bottom pipe pair and return their rects."""
    height = random.randint(150, 300)
    bottom = pipe_img.get_rect(midtop=(SCREEN_WIDTH + 50, height))
    top = pipe_flipped.get_rect(midbottom=(SCREEN_WIDTH + 50, height - PIPE_GAP))
    return top, bottom


def move_pipes(
    pipes_list: List[Tuple[pygame.Rect, pygame.Rect]],
) -> List[Tuple[pygame.Rect, pygame.Rect]]:
    """Shift pipes left and prune those off-screen."""
    return [
        (top.move(-3, 0), bottom.move(-3, 0))
        for top, bottom in pipes_list
        if top.right > -50
    ]


def draw_pipes(pipes_list: List[Tuple[pygame.Rect, pygame.Rect]]) -> None:
    """Render pipes to the main screen surface."""
    for top, bottom in pipes_list:
        screen.blit(pipe_flipped, top)
        screen.blit(pipe_img, bottom)


def check_collision(pipes_list: List[Tuple[pygame.Rect, pygame.Rect]]) -> bool:
    """Return True when the bird has collided with pipes or ground/ceiling."""
    for top, bottom in pipes_list:
        if bird.colliderect(top) or bird.colliderect(bottom):
            sound_hit.play()
            return True
    if bird.top <= -50 or bird.bottom >= SCREEN_HEIGHT - base_img.get_height():
        sound_hit.play()
        return True
    return False


def draw_text(
    text: str, x: int, y: int, color: Tuple[int, int, int] = (255, 255, 255)
) -> None:
    """Utility to blit text on screen."""
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


def draw_volume_ui() -> None:
    """Draw the small volume settings overlay."""
    pygame.draw.rect(screen, (0, 0, 0), (20, 150, SCREEN_WIDTH - 40, 100))
    draw_text("Volume Settings", 90, 160)
    draw_text(f"Music Volume: {int(music_volume*100)}%", 50, 190)
    draw_text(f"SFX Volume: {int(sfx_volume*100)}%", 50, 220)
    draw_text("Use M/N to adjust Music", 50, 250)
    draw_text("Use K/L to adjust SFX", 50, 280)
    draw_text("Press V to close", 50, 310)


# Event handling type
SPAWNPIPE: Final[int] = pygame.USEREVENT

# Initialize music with better error handling
SCRIPT_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))
music_file: str = os.path.join(SCRIPT_DIR, "bg.ogg")

try:
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(
        "Info: Background music not loaded (optional) - game will continue without music"
    )
    music_volume = 0.0  # Disable music volume control since no music is playing

# Start the pipe spawning timer (this was missing)
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQ)

# Initialize default values for game state variables
bird_movement: float = 0.0
pipes: List[Tuple[pygame.Rect, pygame.Rect]] = []
base_x: int = 0
score: int = 0
game_active: bool = True
high_score: int = load_highscore()
music_volume: float = 0.4
sfx_volume: float = 0.5
show_volume_ui: bool = False

# Load all assets
background = load_image_from_url(sprite_urls["background"])
bird_img = load_image_from_url(sprite_urls["bird"])
base_img = load_image_from_url(sprite_urls["base"])
pipe_img = load_image_from_url(sprite_urls["pipe"])
pipe_flipped = pygame.transform.flip(pipe_img, False, True)

sound_flap = load_sound_from_url(sound_urls["flap"])
sound_hit = load_sound_from_url(sound_urls["hit"])
sound_score = load_sound_from_url(sound_urls["score"])

# Initialize bird after loading bird_img
bird: pygame.Rect = bird_img.get_rect(center=(50, SCREEN_HEIGHT // 2))

# Main game loop with type hints
running: bool = True
while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_active and not show_volume_ui:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_movement = FLAP_STRENGTH
                sound_flap.play()
            if event.type == SPAWNPIPE:
                pipes.append(create_pipe())
        elif not game_active and not show_volume_ui:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

        # Toggle volume UI with V key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                show_volume_ui = not show_volume_ui

            if show_volume_ui:
                pressed_key: int = event.key  # Type hint for key events
                volume_change: Final[float] = 0.05
                if pressed_key == pygame.K_m:
                    music_volume = min(1.0, music_volume + volume_change)
                    pygame.mixer.music.set_volume(music_volume)
                elif pressed_key == pygame.K_n:
                    music_volume = max(0.0, music_volume - volume_change)
                    pygame.mixer.music.set_volume(music_volume)
                elif pressed_key == pygame.K_k:
                    sfx_volume = min(1.0, sfx_volume + volume_change)
                    sound_flap.set_volume(sfx_volume)
                    sound_hit.set_volume(sfx_volume)
                    sound_score.set_volume(sfx_volume)
                elif pressed_key == pygame.K_l:
                    sfx_volume = max(0.0, sfx_volume - volume_change)
                    sound_flap.set_volume(sfx_volume)
                    sound_hit.set_volume(sfx_volume)
                    sound_score.set_volume(sfx_volume)

    if game_active and not show_volume_ui:
        bird_movement += GRAVITY
        bird.centery += int(bird_movement)  # Explicit int conversion
        screen.blit(bird_img, bird)

        pipes = move_pipes(pipes)
        draw_pipes(pipes)

        base_x -= 1
        if base_x <= -SCREEN_WIDTH:
            base_x = 0

        # Collision checking with type hints
        collision_detected: bool = check_collision(pipes)
        if collision_detected:
            game_active = False
            if score > high_score:
                high_score = score
                save_highscore(high_score)

        for pipe in pipes:
            # Score when passing pipe
            if pipe[0].centerx == bird.centerx:
                score += 1
                sound_score.play()

        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"High Score: {high_score}", 10, 40)

    elif show_volume_ui:
        draw_volume_ui()
    else:
        draw_text("Game Over! Press R to Restart", 30, SCREEN_HEIGHT // 2)
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"High Score: {high_score}", 10, 40)

    screen.blit(base_img, (base_x, SCREEN_HEIGHT - base_img.get_height()))
    screen.blit(
        base_img, (base_x + SCREEN_WIDTH, SCREEN_HEIGHT - base_img.get_height())
    )

    pygame.display.update()
    clock.tick(60)

pygame.quit()
