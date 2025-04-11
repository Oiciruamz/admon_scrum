"""
User interface elements for the Escape Room game.
"""
import math
import pygame
from settings import *
from assets import assets
from utils import draw_text, draw_panel, draw_progress_bar, draw_tooltip, color_lerp

class UI:
    """
    User interface elements for the game.
    """
    def __init__(self, game):
        """
        Initialize the UI.

        Args:
            game: Game instance
        """
        self.game = game

        # Fonts
        self.font_large = assets.get_font("large")
        self.font_medium = assets.get_font("medium")
        self.font_small = assets.get_font("small")
        self.font_tiny = assets.get_font("tiny")

        # UI animations
        self.animation_time = 0
        self.pulse_speed = 0.05

        # UI elements
        self.tooltip_active = False
        self.tooltip_text = ""
        self.tooltip_x = 0
        self.tooltip_y = 0

        # Button states
        self.buttons = {}

        # Icons
        self.icons = {
            "clock": assets.get_image("icon_clock"),
            "info": assets.get_image("icon_info"),
            "check": assets.get_image("icon_check"),
            "cross": assets.get_image("icon_cross"),
            "lock": assets.get_image("icon_lock"),
            "key": assets.get_image("icon_key")
        }

    def update(self):
        """
        Update UI animations and states.
        """
        # Update animation time
        self.animation_time += self.pulse_speed

        # Reset tooltip if needed
        self.tooltip_active = False

    def render_game_ui(self, screen, timer):
        """
        Render UI elements during gameplay.

        Args:
            screen: Pygame surface to render on
            timer: Timer instance
        """
        # Update UI animations
        self.update()

        # Render top panel
        self._render_top_panel(screen, timer)

        # Render bottom panel
        self._render_bottom_panel(screen)

        # Render tooltip if active
        if self.tooltip_active:
            self._render_tooltip(screen)

    def _render_top_panel(self, screen, timer):
        """
        Render the top UI panel with timer and other info.

        Args:
            screen: Pygame surface to render on
            timer: Timer instance
        """
        # Create panel background
        panel_height = 60
        panel_width = WINDOW_WIDTH

        draw_panel(
            screen,
            0, 0,
            panel_width, panel_height,
            CHARCOAL,
            border_color=None,
            border_width=0,
            radius=0,
            alpha=200
        )

        # Draw separator line
        pygame.draw.line(screen, GRAY, (0, panel_height), (panel_width, panel_height), 2)

        # Render timer
        self._render_timer(screen, timer, 20, panel_height // 2)

        # Render room name if in game state
        if self.game.state == STATE_GAME and self.game.room_manager:
            current_room = self.game.room_manager.get_current_room()
            draw_text(
                screen,
                current_room.name,
                self.font_medium,
                WHITE,
                panel_width // 2,
                panel_height // 2,
                "center"
            )

    def _render_bottom_panel(self, screen):
        """
        Render the bottom UI panel with path and progress info.

        Args:
            screen: Pygame surface to render on
        """
        # Create panel background
        panel_height = 50
        panel_width = WINDOW_WIDTH
        panel_y = WINDOW_HEIGHT - panel_height

        draw_panel(
            screen,
            0, panel_y,
            panel_width, panel_height,
            CHARCOAL,
            border_color=None,
            border_width=0,
            radius=0,
            alpha=200
        )

        # Draw separator line
        pygame.draw.line(screen, GRAY, (0, panel_y), (panel_width, panel_y), 2)

        # Render path info
        if self.game.selected_path:
            self._render_path(screen, 20, panel_y + panel_height // 2)

        # Render progress if in game state
        if self.game.state == STATE_GAME and self.game.room_manager:
            self._render_progress(screen, panel_width - 200, panel_y + panel_height // 2)

    def _render_timer(self, screen, timer, x, y):
        """
        Render the timer with icon and visual effects.

        Args:
            screen: Pygame surface to render on
            timer: Timer instance
            x, y: Position coordinates
        """
        # Format time as MM:SS
        minutes = int(timer.get_time_left() // 60)
        seconds = int(timer.get_time_left() % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Determine color and pulse effect based on time left
        if timer.get_time_left() < 60:  # Less than 1 minute
            color = RED
            pulse = abs(math.sin(self.animation_time * 4)) * 0.3 + 0.7  # Faster pulse when low on time
        elif timer.get_time_left() < 120:  # Less than 2 minutes
            color = YELLOW
            pulse = abs(math.sin(self.animation_time * 2)) * 0.2 + 0.8
        else:
            color = WHITE
            pulse = 1.0

        # Draw clock icon
        icon_size = int(24 * pulse)
        icon_x = x
        icon_y = y - icon_size // 2

        # Scale icon with pulse effect
        if pulse != 1.0:
            scaled_icon = pygame.transform.scale(self.icons["clock"], (icon_size, icon_size))
            screen.blit(scaled_icon, (icon_x, icon_y))
        else:
            screen.blit(self.icons["clock"], (icon_x, icon_y))

        # Draw time text
        draw_text(
            screen,
            time_str,
            self.font_medium,
            color,
            icon_x + 40,
            y,
            "left"
        )

    def _render_path(self, screen, x, y):
        """
        Render the current path with icon.

        Args:
            screen: Pygame surface to render on
            x, y: Position coordinates
        """
        # Draw path icon
        screen.blit(self.icons["info"], (x, y - 16))

        # Draw path text
        path_name = self.game.selected_path.upper()
        draw_text(
            screen,
            f"Path: {path_name}",
            self.font_small,
            WHITE,
            x + 40,
            y,
            "left"
        )

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
            x,
            y - 15,
            "center"
        )

        # Draw progress bar
        progress = current_room / total_rooms
        draw_progress_bar(
            screen,
            x - 75, y + 5,
            150, 10,
            progress,
            CHARCOAL,
            GREEN,
            WHITE,
            1,
            5
        )

    def _render_tooltip(self, screen):
        """
        Render a tooltip with text.

        Args:
            screen: Pygame surface to render on
        """
        draw_tooltip(
            screen,
            self.tooltip_text,
            self.font_tiny,
            self.tooltip_x,
            self.tooltip_y,
            padding=10,
            bg_color=CHARCOAL,
            text_color=WHITE,
            border_color=WHITE,
            border_width=1,
            radius=5,
            max_width=300
        )

    def show_tooltip(self, text, x, y):
        """
        Show a tooltip at the specified position.

        Args:
            text: Tooltip text
            x, y: Position coordinates
        """
        self.tooltip_active = True
        self.tooltip_text = text
        self.tooltip_x = x
        self.tooltip_y = y

    def create_button(self, id, text, x, y, width=None, height=None, color=CHARCOAL, hover_color=None, text_color=WHITE, border_color=WHITE):
        """
        Create a button and store its state.

        Args:
            id: Button identifier
            text: Button text
            x, y: Position coordinates
            width, height: Button dimensions (optional)
            color: Button color
            hover_color: Button hover color (optional)
            text_color: Text color
            border_color: Border color

        Returns:
            Button rectangle
        """
        if width is None:
            width = UI_BUTTON_WIDTH
        if height is None:
            height = UI_BUTTON_HEIGHT
        if hover_color is None:
            hover_color = color_lerp(color, WHITE, 0.3)

        # Store button state
        self.buttons[id] = {
            'text': text,
            'rect': pygame.Rect(x - width // 2, y - height // 2, width, height),
            'color': color,
            'hover_color': hover_color,
            'text_color': text_color,
            'border_color': border_color,
            'hover': False,
            'clicked': False
        }

        return self.buttons[id]['rect']

    def update_button(self, id, mouse_pos, mouse_clicked):
        """
        Update button state based on mouse position and clicks.

        Args:
            id: Button identifier
            mouse_pos: Mouse position (x, y)
            mouse_clicked: Whether mouse was clicked

        Returns:
            True if button was clicked, False otherwise
        """
        if id not in self.buttons:
            return False

        button = self.buttons[id]
        button['hover'] = button['rect'].collidepoint(mouse_pos)

        if button['hover'] and mouse_clicked:
            button['clicked'] = True
            return True

        button['clicked'] = False
        return False

    def render_button(self, screen, id):
        """
        Render a button.

        Args:
            screen: Pygame surface to render on
            id: Button identifier
        """
        if id not in self.buttons:
            return

        button = self.buttons[id]
        color = button['hover_color'] if button['hover'] else button['color']

        # Draw button background
        pygame.draw.rect(screen, color, button['rect'], border_radius=UI_BUTTON_RADIUS)

        # Draw border
        pygame.draw.rect(screen, button['border_color'], button['rect'], UI_BORDER_WIDTH, border_radius=UI_BUTTON_RADIUS)

        # Draw text
        draw_text(
            screen,
            button['text'],
            self.font_medium,
            button['text_color'],
            button['rect'].centerx,
            button['rect'].centery,
            "center"
        )
