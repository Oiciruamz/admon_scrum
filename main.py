"""
Main entry point for the Escape Room game.
"""
import os
import sys
import pygame
from settings import *
from assets import assets
from game import Game

def main():
    """
    Main function to initialize and run the game.
    """
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()  # For sound
    pygame.font.init()  # Initialize font module

    # Create game window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # Initialize assets and fonts (después de inicializar pygame.display)
    assets.initialize()
    assets.initialize_fonts()

    # Create clock for controlling frame rate
    clock = pygame.time.Clock()

    # Create game instance
    game = Game(screen)

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        # Update game state
        game.update()

        # Render game
        game.render()

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Create asset directories if they don't exist 
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True)

    # Run the game
    main()
