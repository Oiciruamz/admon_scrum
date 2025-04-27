"""
User interface elements for the Escape Room game.
"""
import pygame
from settings import *
from assets import assets
from utils import draw_text, draw_progress_bar

class UI:
    """
    User interface elements for the game.
    """
    def __init__(self, game):
        self.game = game
        self.font_large = assets.get_font("large")
        self.font_medium = assets.get_font("medium")
        self.font_small = assets.get_font("small")
        self.font_tiny = assets.get_font("tiny")

    def update(self):
        """
        Update UI state.
        """
        pass

    def render_game_ui(self, screen, timer):
        """
        Render in-game UI elements.

        Args:
            screen: Pygame surface to render on
            timer: Timer object
        """
        # Draw room progress
        self._render_progress(screen, UI_PADDING, UI_PADDING)

        # Draw timer
        self._render_timer(screen, timer, WINDOW_WIDTH - UI_PADDING, UI_PADDING)



    def _render_progress(self, screen, x, y):
        """
        Render the room progress with visual bar.

        Args:
            screen: Pygame surface to render on
            x, y: Position coordinates
        """
        current_room = self.game.room_manager.current_room_index + 1
        total_rooms = len(self.game.room_manager.rooms)

        # Draw progress text
        draw_text(
            screen,
            f"Room {current_room}/{total_rooms}",
            self.font_small,
            WHITE,
            x + 75,
            y,
            "left"
        )

        # Draw progress bar
        draw_progress_bar(
            screen,
            x, y + 30,
            150, 10,
            current_room / total_rooms,
            CHARCOAL,
            GREEN,
            WHITE,
            1,
            5
        )

    def _render_timer(self, screen, timer, x, y):
        """
        Render the timer.

        Args:
            screen: Pygame surface to render on
            timer: Timer object
            x, y: Position coordinates
        """
        minutes = int(timer.get_time_left() // 60)
        seconds = int(timer.get_time_left() % 60)
        timer_text = f"{minutes:02d}:{seconds:02d}"

        draw_text(
            screen,
            timer_text,
            self.font_medium,
            WHITE,
            x,
            y,
            "right"
        )

