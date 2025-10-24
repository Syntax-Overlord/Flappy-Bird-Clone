# Flappy Bird Clone

A Python implementation of the classic Flappy Bird game using Pygame, featuring background music, sound effects, and a high score system.

## Features

- Classic Flappy Bird gameplay mechanics
- Background music with volume control
- Sound effects for actions (flap, hit, scoring)
- High score system that persists between sessions
- Volume control interface for both music and sound effects
- Smooth animations and physics

## Requirements

- Python 3.x
- Pygame
- Requests (for downloading assets)
- Internet connection (first run only, to download assets)

## Installation

1. Install the required Python packages:

```bash
pip install pygame requests
```

2. Make sure you have the background music file (`sweden.ogg`) in your game directory

## How to Play

- Press **SPACE** to make the bird flap
- Press **R** to restart after game over
- Press **V** to toggle the volume control interface
- In volume control mode:
  - **M/N**: Adjust music volume up/down
  - **K/L**: Adjust sound effects volume up/down
  - **V**: Close volume control

## Game Controls

- **Space**: Flap/Jump
- **R**: Restart game
- **V**: Toggle volume settings
- **M/N**: Adjust music volume (when volume UI is visible)
- **K/L**: Adjust sound effects volume (when volume UI is visible)

## Credits

- Original Flappy Bird assets from [sourabhv/FlapPyBird](https://github.com/sourabhv/FlapPyBird)
