"""
Puzzle system for the Escape Room game.
"""
import math
import random
import pygame
from settings import *
from utils import draw_text, draw_panel, draw_tooltip, color_lerp

class Puzzle:
    """
    Base class for all puzzles in the game.
    """
    def __init__(self, title, description, difficulty=1):
        """
        Initialize a puzzle.

        Args:
            title: Puzzle title
            description: Puzzle description
            difficulty: Puzzle difficulty (1-5)
        """
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.completed = False
        self.active = False
        self.score = 0
        self.max_score = 100 * difficulty
        self.time_bonus = 0
        self.attempts = 0
        self.max_attempts = 3
        self.feedback = ""
        self.success_callback = None

        # UI elements
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.close_button_rect = pygame.Rect(0, 0, 0, 0)
        self.submit_button_rect = pygame.Rect(0, 0, 0, 0)

        # Animation
        self.animation_time = 0
        self.animation_speed = 0.05

    def set_success_callback(self, callback):
        """
        Set a callback function to be called when the puzzle is completed.

        Args:
            callback: Function to call
        """
        self.success_callback = callback

    def activate(self, screen_rect):
        """
        Activate the puzzle.

        Args:
            screen_rect: Screen rectangle for positioning
        """
        self.active = True
        self.attempts = 0
        self.feedback = ""

        # Position puzzle in center of screen
        width = min(700, screen_rect.width - 100)
        height = min(500, screen_rect.height - 100)
        x = (screen_rect.width - width) // 2
        y = (screen_rect.height - height) // 2
        self.rect = pygame.Rect(x, y, width, height)

        # Position buttons
        self.close_button_rect = pygame.Rect(
            x + width - 40, y + 10, 30, 30
        )
        self.submit_button_rect = pygame.Rect(
            x + width // 2 - 50, y + height - 50, 100, 40
        )

        # Initialize puzzle-specific elements
        self._initialize()

    def deactivate(self):
        """
        Deactivate the puzzle.
        """
        self.active = False

    def update(self):
        """
        Update puzzle state.
        """
        if not self.active:
            return

        # Update animation
        self.animation_time += self.animation_speed

        # Update puzzle-specific elements
        self._update()

    def handle_event(self, event):
        """
        Handle events for the puzzle.

        Args:
            event: Pygame event
        """
        if not self.active:
            return

        # Manejar el evento de temporizador para desactivar el puzzle
        if event.type == pygame.USEREVENT and self.completed:
            self.deactivate()
            # Detener el temporizador
            pygame.time.set_timer(pygame.USEREVENT, 0)
            return

        # Check for close button click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_button_rect.collidepoint(event.pos):
                self.deactivate()
                return

            # Check for submit button click
            if self.submit_button_rect.collidepoint(event.pos):
                self._submit()
                return

        # Handle puzzle-specific events
        self._handle_event(event)

    def render(self, screen):
        """
        Render the puzzle.

        Args:
            screen: Pygame surface to render on
        """
        if not self.active:
            return

        # Draw darkened overlay for the entire screen with higher opacity
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))  # Black with 85% opacity
        screen.blit(overlay, (0, 0))

        # Draw a second overlay to ensure complete coverage
        screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Draw background panel
        draw_panel(
            screen,
            self.rect.x, self.rect.y,
            self.rect.width, self.rect.height,
            CHARCOAL,
            WHITE,
            2,
            10,
            240  # Increased opacity
        )

        # Draw title with improved visibility
        title_bg = pygame.Rect(
            self.rect.x + 20,
            self.rect.y + 10,
            self.rect.width - 80,  # Leave space for close button
            50
        )
        pygame.draw.rect(screen, BLACK, title_bg, border_radius=5)

        draw_text(
            screen,
            self.title,
            pygame.font.SysFont("Arial", UI_FONT_SIZE_MEDIUM, bold=True),
            WHITE,
            self.rect.x + self.rect.width // 2,
            self.rect.y + 30,
            "center"
        )

        # Draw close button with improved visibility
        # Draw glow effect for close button
        close_glow_rect = self.close_button_rect.inflate(6, 6)
        pygame.draw.rect(screen, (*RED, 150), close_glow_rect, border_radius=8)

        # Draw button background
        pygame.draw.rect(screen, RED, self.close_button_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.close_button_rect, 2, border_radius=5)

        # Draw X
        pygame.draw.line(
            screen, WHITE,
            (self.close_button_rect.x + 10, self.close_button_rect.y + 10),
            (self.close_button_rect.x + 20, self.close_button_rect.y + 20),
            2
        )
        pygame.draw.line(
            screen, WHITE,
            (self.close_button_rect.x + 20, self.close_button_rect.y + 10),
            (self.close_button_rect.x + 10, self.close_button_rect.y + 20),
            2
        )

        # Draw submit button with improved visibility
        if not self.completed:
            # Create pulsing effect for submit button
            pulse = 0.8 + 0.2 * math.sin(self.animation_time * 3)
            button_color = GREEN if self._can_submit() else GRAY

            # Draw glow for submit button
            submit_glow_rect = self.submit_button_rect.inflate(int(8 * pulse), int(4 * pulse))
            pygame.draw.rect(screen, (*button_color, 150), submit_glow_rect, border_radius=8)

            # Draw button background
            pygame.draw.rect(screen, button_color, self.submit_button_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, self.submit_button_rect, 2, border_radius=5)

            # Draw text
            draw_text(
                screen,
                "Submit",
                pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL, bold=True),
                WHITE,
                self.submit_button_rect.centerx,
                self.submit_button_rect.centery,
                "center"
            )

        # Draw feedback if any
        if self.feedback:
            feedback_color = GREEN if self.completed else RED
            draw_text(
                screen,
                self.feedback,
                pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL),
                feedback_color,
                self.rect.x + self.rect.width // 2,
                self.submit_button_rect.y - 30,
                "center"
            )

        # Draw attempts remaining
        if not self.completed:
            attempts_text = f"Attempts: {self.attempts}/{self.max_attempts}"
            draw_text(
                screen,
                attempts_text,
                pygame.font.SysFont("Arial", UI_FONT_SIZE_TINY),
                WHITE,
                self.rect.x + 20,
                self.submit_button_rect.y,
                "left"
            )

        # Draw puzzle-specific elements
        self._render_content(screen)

    def _initialize(self):
        """
        Initialize puzzle-specific elements.
        To be overridden by subclasses.
        """
        pass

    def _update(self):
        """
        Update puzzle-specific elements.
        To be overridden by subclasses.
        """
        pass

    def _handle_event(self, event):
        """
        Handle puzzle-specific events.
        To be overridden by subclasses.

        Args:
            event: Pygame event
        """
        pass

    def _render_content(self, screen):
        """
        Render puzzle-specific content.
        To be overridden by subclasses.

        Args:
            screen: Pygame surface to render on
        """
        pass

    def _can_submit(self):
        """
        Check if the puzzle can be submitted.
        To be overridden by subclasses.

        Returns:
            Boolean indicating if the puzzle can be submitted
        """
        return self.attempts < self.max_attempts

    def _submit(self):
        """
        Submit the puzzle for validation.
        """
        if not self._can_submit():
            return

        self.attempts += 1

        # Check if the solution is correct
        if self._check_solution():
            self.completed = True
            self.score = self._calculate_score()
            self.feedback = f"Correct! Score: {self.score}"

            # Call success callback if set
            if self.success_callback:
                self.success_callback(self.score)

            # Desactivar el puzzle después de completarlo exitosamente
            # Dar un breve tiempo para mostrar el feedback antes de desactivar
            pygame.time.set_timer(pygame.USEREVENT, 1500)  # 1.5 segundos
        else:
            # Check if out of attempts
            if self.attempts >= self.max_attempts:
                self.feedback = "Out of attempts. Try again later."
            else:
                self.feedback = f"Incorrect. {self.max_attempts - self.attempts} attempts remaining."

    def _check_solution(self):
        """
        Check if the puzzle solution is correct.
        To be overridden by subclasses.

        Returns:
            Boolean indicating if the solution is correct
        """
        return False

    def _calculate_score(self):
        """
        Calculate the score based on attempts and time.

        Returns:
            Score value
        """
        # Base score
        base_score = self.max_score

        # Deduct points for attempts
        attempt_penalty = (self.attempts - 1) * (self.max_score / (self.max_attempts * 2))

        # Add time bonus
        time_bonus = self.time_bonus

        return int(base_score - attempt_penalty + time_bonus)


class MultipleChoiceQuiz(Puzzle):
    """
    Multiple choice quiz puzzle.
    """
    def __init__(self, title, description, question, options, correct_answer, difficulty=1):
        """
        Initialize a multiple choice quiz.

        Args:
            title: Quiz title
            description: Quiz description
            question: Quiz question
            options: List of answer options
            correct_answer: Correct answer
            difficulty: Quiz difficulty (1-5)
        """
        super().__init__(title, description, difficulty)
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.selected_option = None
        self.option_rects = []

    def _initialize(self):
        """
        Initialize quiz-specific elements.
        """
        self.selected_option = None
        self.option_rects = []

        # Create option rectangles
        option_height = 40
        option_width = self.rect.width - 100
        option_x = self.rect.x + 50
        option_y = self.rect.y + 150

        for i in range(len(self.options)):
            option_rect = pygame.Rect(
                option_x,
                option_y + i * (option_height + 10),
                option_width,
                option_height
            )
            self.option_rects.append(option_rect)

    def _handle_event(self, event):
        """
        Handle quiz-specific events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_option = i
                    break

    def _render_content(self, screen):
        """
        Render quiz-specific content.

        Args:
            screen: Pygame surface to render on
        """
        # Draw question
        draw_text(
            screen,
            self.question,
            pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL),
            WHITE,
            self.rect.x + self.rect.width // 2,
            self.rect.y + 100,
            "center"
        )

        # Draw options
        for i, (rect, option) in enumerate(zip(self.option_rects, self.options)):
            # Determine colors based on selection and completion
            if self.completed:
                if i == self.options.index(self.correct_answer):
                    bg_color = GREEN
                elif i == self.selected_option:
                    bg_color = RED
                else:
                    bg_color = CHARCOAL
            else:
                bg_color = BLUE if i == self.selected_option else CHARCOAL

            # Draw option background
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)

            # Draw option text
            draw_text(
                screen,
                option,
                pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL),
                WHITE,
                rect.centerx,
                rect.centery,
                "center"
            )

    def _can_submit(self):
        """
        Check if the quiz can be submitted.

        Returns:
            Boolean indicating if the quiz can be submitted
        """
        return super()._can_submit() and self.selected_option is not None

    def _check_solution(self):
        """
        Check if the selected option is correct.

        Returns:
            Boolean indicating if the solution is correct
        """
        return self.options[self.selected_option] == self.correct_answer


class OrderingPuzzle(Puzzle):
    """
    Ordering puzzle where items must be arranged in the correct order.
    """
    def __init__(self, title, description, items, correct_order, difficulty=2):
        """
        Initialize an ordering puzzle.

        Args:
            title: Puzzle title
            description: Puzzle description
            items: List of items to order
            correct_order: Correct order of items
            difficulty: Puzzle difficulty (1-5)
        """
        super().__init__(title, description, difficulty)
        self.items = items
        self.correct_order = correct_order
        self.current_order = []
        self.item_rects = []
        self.dragging_item = None
        self.dragging_offset = (0, 0)

    def _initialize(self):
        """
        Initialize puzzle-specific elements.
        """
        self.current_order = self.items.copy()
        random.shuffle(self.current_order)
        self.item_rects = []
        self.dragging_item = None

        # Create item rectangles
        item_height = 40
        item_width = self.rect.width - 100
        item_x = self.rect.x + 50
        item_y = self.rect.y + 150

        for i in range(len(self.current_order)):
            item_rect = pygame.Rect(
                item_x,
                item_y + i * (item_height + 10),
                item_width,
                item_height
            )
            self.item_rects.append(item_rect)

    def _handle_event(self, event):
        """
        Handle puzzle-specific events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(event.pos):
                    self.dragging_item = i
                    self.dragging_offset = (
                        rect.x - event.pos[0],
                        rect.y - event.pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_item is not None:
                # Find the closest position to drop the item
                drop_pos = event.pos[1]
                closest_idx = min(
                    range(len(self.item_rects)),
                    key=lambda i: abs(self.item_rects[i].centery - drop_pos)
                )

                # Swap items
                if closest_idx != self.dragging_item:
                    self.current_order[self.dragging_item], self.current_order[closest_idx] = \
                        self.current_order[closest_idx], self.current_order[self.dragging_item]

                self.dragging_item = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item is not None:
                # Update dragged item position
                self.item_rects[self.dragging_item].x = event.pos[0] + self.dragging_offset[0]
                self.item_rects[self.dragging_item].y = event.pos[1] + self.dragging_offset[1]

    def _update(self):
        """
        Update puzzle-specific elements.
        """
        super()._update()

        # Update item positions (except for dragged item)
        item_height = 40
        item_width = self.rect.width - 100
        item_x = self.rect.x + 50
        item_y = self.rect.y + 150

        for i in range(len(self.item_rects)):
            if i != self.dragging_item:
                self.item_rects[i].x = item_x
                self.item_rects[i].y = item_y + i * (item_height + 10)

    def _render_content(self, screen):
        """
        Render puzzle-specific content.

        Args:
            screen: Pygame surface to render on
        """
        # Draw instructions
        draw_text(
            screen,
            "Drag and drop items to arrange them in the correct order:",
            pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL),
            WHITE,
            self.rect.x + self.rect.width // 2,
            self.rect.y + 100,
            "center"
        )

        # Draw items in current order
        for i, (rect, item) in enumerate(zip(self.item_rects, self.current_order)):
            # Determine colors
            if self.completed:
                if self.current_order.index(item) == self.correct_order.index(item):
                    bg_color = GREEN
                else:
                    bg_color = RED
            else:
                bg_color = BLUE if i == self.dragging_item else CHARCOAL

            # Draw item background
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)

            # Draw item text
            draw_text(
                screen,
                item,
                pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL),
                WHITE,
                rect.centerx,
                rect.centery,
                "center"
            )

            # Draw drag handle
            pygame.draw.line(
                screen, WHITE,
                (rect.x + 20, rect.centery - 5),
                (rect.x + 20, rect.centery + 5),
                2
            )
            pygame.draw.line(
                screen, WHITE,
                (rect.x + 15, rect.centery - 5),
                (rect.x + 15, rect.centery + 5),
                2
            )

    def _check_solution(self):
        """
        Check if the current order matches the correct order.

        Returns:
            Boolean indicating if the solution is correct
        """
        return self.current_order == self.correct_order


class MatchingPuzzle(Puzzle):
    """
    Matching puzzle where items must be matched with their corresponding pairs.
    """
    def __init__(self, title, description, left_items, right_items, correct_matches, difficulty=3):
        """
        Initialize a matching puzzle.

        Args:
            title: Puzzle title
            description: Puzzle description
            left_items: List of items on the left
            right_items: List of items on the right
            correct_matches: Dictionary mapping left items to right items
            difficulty: Puzzle difficulty (1-5)
        """
        super().__init__(title, description, difficulty)
        self.left_items = left_items
        self.right_items = right_items
        self.correct_matches = correct_matches
        self.current_matches = {}
        self.left_rects = []
        self.right_rects = []
        self.selected_left = None
        self.lines = []

    def _initialize(self):
        """
        Initialize puzzle-specific elements.
        """
        self.current_matches = {}
        self.selected_left = None
        self.lines = []

        # Create item rectangles
        item_height = 40
        item_width = (self.rect.width - 150) // 2
        left_x = self.rect.x + 30
        right_x = self.rect.x + self.rect.width - 30 - item_width
        item_y = self.rect.y + 150

        # Left items
        self.left_rects = []
        for i in range(len(self.left_items)):
            item_rect = pygame.Rect(
                left_x,
                item_y + i * (item_height + 10),
                item_width,
                item_height
            )
            self.left_rects.append(item_rect)

        # Right items
        self.right_rects = []
        for i in range(len(self.right_items)):
            item_rect = pygame.Rect(
                right_x,
                item_y + i * (item_height + 10),
                item_width,
                item_height
            )
            self.right_rects.append(item_rect)

    def _handle_event(self, event):
        """
        Handle puzzle-specific events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check left items
            for i, rect in enumerate(self.left_rects):
                if rect.collidepoint(event.pos):
                    left_item = self.left_items[i]

                    # If already matched, remove the match
                    if left_item in self.current_matches:
                        del self.current_matches[left_item]

                    # Select this item
                    self.selected_left = i
                    break

            # Check right items
            for i, rect in enumerate(self.right_rects):
                if rect.collidepoint(event.pos) and self.selected_left is not None:
                    left_item = self.left_items[self.selected_left]
                    right_item = self.right_items[i]

                    # Create match
                    self.current_matches[left_item] = right_item
                    self.selected_left = None
                    break

    def _render_content(self, screen):
        """
        Render puzzle-specific content.

        Args:
            screen: Pygame surface to render on
        """
        # Draw instructions with improved visibility
        instruction_bg = pygame.Rect(
            self.rect.x + 20,
            self.rect.y + 70,
            self.rect.width - 40,
            50
        )
        pygame.draw.rect(screen, BLACK, instruction_bg, border_radius=5)
        pygame.draw.rect(screen, WHITE, instruction_bg, 1, border_radius=5)

        draw_text(
            screen,
            "Match items on the left with their corresponding items on the right:",
            pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL, bold=True),
            WHITE,
            self.rect.x + self.rect.width // 2,
            self.rect.y + 95,
            "center"
        )

        # Draw left items with improved visibility
        for i, (rect, item) in enumerate(zip(self.left_rects, self.left_items)):
            # Determine colors
            if self.completed:
                if item in self.current_matches and self.current_matches[item] == self.correct_matches[item]:
                    bg_color = GREEN
                    border_color = WHITE
                    glow = True
                else:
                    bg_color = RED
                    border_color = WHITE
                    glow = False
            else:
                if i == self.selected_left:
                    bg_color = BLUE
                    border_color = YELLOW
                    glow = True
                elif item in self.current_matches:
                    bg_color = PURPLE
                    border_color = CYAN
                    glow = True
                else:
                    bg_color = CHARCOAL
                    border_color = WHITE
                    glow = False

            # Draw glow effect if needed
            if glow:
                glow_rect = rect.inflate(10, 10)
                pygame.draw.rect(screen, border_color, glow_rect, border_radius=8)

            # Draw item background with gradient effect
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)

            # Draw border
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

            # Draw item text with improved readability
            draw_text(
                screen,
                item,
                pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL, bold=True),
                WHITE,
                rect.centerx,
                rect.centery,
                "center"
            )

        # Draw right items with improved visibility
        for i, (rect, item) in enumerate(zip(self.right_rects, self.right_items)):
            # Determine colors and states
            is_matched = False
            is_correct = False
            matching_left_item = None

            # Check if this item is matched and if it's correct
            for left_item, right_item in self.current_matches.items():
                if right_item == item:
                    is_matched = True
                    matching_left_item = left_item
                    if self.correct_matches[left_item] == right_item:
                        is_correct = True
                    break

            # Set colors based on state
            if self.completed:
                if is_matched and is_correct:
                    bg_color = GREEN
                    border_color = WHITE
                    glow = True
                elif is_matched:
                    bg_color = RED
                    border_color = WHITE
                    glow = False
                else:
                    bg_color = CHARCOAL
                    border_color = WHITE
                    glow = False
            else:
                if is_matched:
                    bg_color = PURPLE
                    border_color = CYAN
                    glow = True
                else:
                    bg_color = CHARCOAL
                    border_color = WHITE
                    glow = False

            # Draw glow effect if needed
            if glow:
                glow_rect = rect.inflate(10, 10)
                pygame.draw.rect(screen, border_color, glow_rect, border_radius=8)

            # Draw item background
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)

            # Draw border
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

            # Create a text surface with word wrapping for better readability
            font = pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL, bold=True)

            # Limit text length and add ellipsis if too long
            max_chars = 30
            display_text = item if len(item) <= max_chars else item[:max_chars-3] + "..."

            # Draw text
            draw_text(
                screen,
                display_text,
                font,
                WHITE,
                rect.centerx,
                rect.centery,
                "center"
            )

        # Draw connection lines with improved visibility
        for left_item, right_item in self.current_matches.items():
            left_idx = self.left_items.index(left_item)
            right_idx = self.right_items.index(right_item)

            left_rect = self.left_rects[left_idx]
            right_rect = self.right_rects[right_idx]

            # Determine line color and style
            if self.completed:
                if self.correct_matches[left_item] == right_item:
                    line_color = GREEN
                    line_width = 3
                    animate = True
                else:
                    line_color = RED
                    line_width = 2
                    animate = False
            else:
                line_color = CYAN
                line_width = 2
                animate = True

            # Draw animated line with glow effect
            start_pos = (left_rect.right, left_rect.centery)
            end_pos = (right_rect.left, right_rect.centery)

            # Draw glow/shadow for the line
            if animate:
                # Draw pulsing glow effect
                glow_alpha = int(128 + 64 * math.sin(self.animation_time * 3))
                glow_color = (*line_color[:3], glow_alpha)

                # Draw wider glow line
                pygame.draw.line(
                    screen,
                    glow_color,
                    start_pos,
                    end_pos,
                    line_width + 2
                )

            # Draw main line
            pygame.draw.line(
                screen,
                line_color,
                start_pos,
                end_pos,
                line_width
            )

        # Draw line from selected left item to mouse position with improved visibility
        if self.selected_left is not None:
            left_rect = self.left_rects[self.selected_left]
            mouse_pos = pygame.mouse.get_pos()
            start_pos = (left_rect.right, left_rect.centery)

            # Draw animated selection line
            # Create a pulsing effect
            pulse = 0.7 + 0.3 * math.sin(self.animation_time * 5)

            # Draw glow effect
            glow_width = int(4 * pulse)
            pygame.draw.line(
                screen,
                (*YELLOW, 128),  # Semi-transparent yellow
                start_pos,
                mouse_pos,
                glow_width
            )

            # Draw main line
            pygame.draw.line(
                screen,
                WHITE,
                start_pos,
                mouse_pos,
                2
            )

    def _can_submit(self):
        """
        Check if the puzzle can be submitted.

        Returns:
            Boolean indicating if the puzzle can be submitted
        """
        return super()._can_submit() and len(self.current_matches) == len(self.left_items)

    def _check_solution(self):
        """
        Check if all matches are correct.

        Returns:
            Boolean indicating if the solution is correct
        """
        if len(self.current_matches) != len(self.correct_matches):
            return False

        for left_item, right_item in self.current_matches.items():
            if self.correct_matches.get(left_item) != right_item:
                return False

        return True


def create_puzzle_from_content(content_item, difficulty=1):
    """
    Create a puzzle based on educational content.

    Args:
        content_item: Dictionary containing educational content
        difficulty: Puzzle difficulty (1-5)

    Returns:
        Puzzle object
    """
    title = content_item["title"]
    description = content_item["description"]

    # Randomly select a puzzle type based on available content
    puzzle_type = random.choice(["quiz", "ordering", "matching"])

    if puzzle_type == "quiz" and "quiz_questions" in content_item:
        # Create a multiple choice quiz
        question_data = random.choice(content_item["quiz_questions"])
        return MultipleChoiceQuiz(
            title,
            description,
            question_data["question"],
            question_data["options"],
            question_data["correct_answer"],
            difficulty
        )

    elif puzzle_type == "ordering" and "key_concepts" in content_item:
        # Create an ordering puzzle
        concepts = [concept["name"] for concept in content_item["key_concepts"]]
        correct_order = concepts.copy()
        return OrderingPuzzle(
            title,
            description,
            concepts,
            correct_order,
            difficulty
        )

    elif puzzle_type == "matching" and "key_concepts" in content_item:
        # Create a matching puzzle
        concepts = content_item["key_concepts"]
        left_items = [concept["name"] for concept in concepts]
        right_items = [concept["description"] for concept in concepts]

        # Create correct matches dictionary
        correct_matches = {}
        for concept in concepts:
            correct_matches[concept["name"]] = concept["description"]

        return MatchingPuzzle(
            title,
            description,
            left_items,
            right_items,
            correct_matches,
            difficulty
        )

    # Fallback to a simple quiz
    return MultipleChoiceQuiz(
        title,
        description,
        "What is the main focus of " + title + "?",
        ["Planning", "Execution", "Monitoring", "Closing"],
        "Execution",
        difficulty
    )
