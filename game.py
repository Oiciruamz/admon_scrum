"""
Game state management for the Escape Room game.
"""
import sys
import pygame
import random
import math
from settings import *
from player import Player
from room import RoomManager, ScrumRolesRoom, ScrumArtifactsRoom, ScrumEventsRoom, PMBOKInitiationRoom, PMBOKPlanningRoom, PMBOKExecutionRoom, PMBOKClosingRoom
from ui import UI
from timer import Timer
from assets import assets
from utils import draw_decorative_border, draw_stardew_button, draw_stardew_title, color_lerp

class Game:
    """
    Main game class that manages game states and components.
    """
    def __init__(self, screen):
        """
        Initialize the game.

        Args:
            screen: Pygame surface for rendering
        """
        self.screen = screen
        self.state = STATE_MENU
        self.selected_path = None

        # Initialize components
        self.ui = UI(self)
        self.player = None
        self.room_manager = None
        self.timer = None

        # Game progress
        self.total_score = 0
        self.high_score = 0
        self.completed_rooms = 0
        self.time_bonus = 0

        # Load fonts
        self.font_large = pygame.font.Font("assets/fonts/Stardew_Valley.ttf", 48)
        self.font_medium = pygame.font.Font("assets/fonts/Stardew_Valley.ttf", 36)
        self.font_small = pygame.font.Font("assets/fonts/Stardew_Valley.ttf", 24)

    def handle_event(self, event):
        """
        Handle pygame events based on current game state.

        Args:
            event: Pygame event
        """
        if self.state == STATE_MENU:
            self._handle_menu_event(event)
        elif self.state == STATE_PATH_SELECTION:
            self._handle_path_selection_event(event)
        elif self.state == STATE_INSTRUCTIONS:
            self._handle_instructions_event(event)
        elif self.state == STATE_GAME:
            self._handle_game_event(event)
        elif self.state == STATE_GAME_OVER or self.state == STATE_VICTORY:
            self._handle_end_event(event)

    def update(self):
        """
        Update game state and components.
        """
        # Actualizar la pantalla de selección de camino
        if self.state == STATE_PATH_SELECTION:
            if hasattr(self, 'path_selection_player') and self.path_selection_player is not None:
                self.path_selection_player.update()

        # Actualizar el juego principal
        elif self.state == STATE_GAME:
            self.player.update()
            current_room = self.room_manager.get_current_room()
            self.player.current_room = current_room
            current_room.update()
            self.timer.update()
            self.ui.update()

            # Verificar si se ha presionado la tecla de espacio para interactuar
            if self.player.is_interacting():
                # Verificar si el jugador está en un área de transición
                in_transition_area = False
                if hasattr(current_room, 'check_transition_area'):
                    in_transition_area = current_room.check_transition_area(self.player.rect)

                # Si está en un área de transición y presiona espacio
                if in_transition_area:
                    # Si es la sala 1, 2 o 3 de SCRUM, o la sala 1, 2 o 3 de PMBOK, ir a la siguiente sala
                    if (isinstance(current_room, ScrumRolesRoom) or
                        isinstance(current_room, ScrumArtifactsRoom) or
                        isinstance(current_room, PMBOKInitiationRoom) or
                        isinstance(current_room, PMBOKPlanningRoom) or
                        isinstance(current_room, PMBOKExecutionRoom)) and self.room_manager.has_next_room():
                        # Incrementar contador de salas completadas
                        self.completed_rooms += 1

                        # Cambiar a la siguiente sala
                        self.room_manager.go_to_next_room()
                        current_room = self.room_manager.get_current_room()
                        self.player.current_room = current_room

                        # Posicionar al jugador según la sala de destino
                        if isinstance(current_room, ScrumArtifactsRoom):  # Si va hacia la Sala 2 de SCRUM
                            self.player.rect.x = WINDOW_WIDTH - self.player.width - 20  # 20 píxeles desde el borde derecho
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 20  # 20 píxeles desde el borde inferior
                        elif isinstance(current_room, PMBOKPlanningRoom):  # Si va hacia la Sala 2 de PMBOK
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 50  # 50 píxeles desde el borde inferior
                        elif isinstance(current_room, PMBOKExecutionRoom):  # Si va hacia la Sala 3 de PMBOK
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 50  # 50 píxeles desde el borde inferior
                        elif isinstance(current_room, PMBOKClosingRoom):  # Si va hacia la Sala 4 de PMBOK
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 50  # 50 píxeles desde el borde inferior
                        else:  # Si va hacia la Sala 3 de SCRUM
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - 100

                        # Actualizar también las coordenadas x e y del jugador para mantener consistencia
                        self.player.x = self.player.rect.x
                        self.player.y = self.player.rect.y

                    # Si es la sala 4 de PMBOK o la sala 3 de SCRUM, finalizar el juego
                    elif isinstance(current_room, PMBOKClosingRoom) or isinstance(current_room, ScrumEventsRoom):
                        # Incrementar contador de salas completadas
                        self.completed_rooms += 1

                        # Calculate final score based on time left and rooms completed
                        time_left = self.timer.get_time_left()
                        self.time_bonus = int(time_left * 10)  # 10 points per second remaining
                        self.total_score = (self.completed_rooms * 1000) + self.time_bonus  # 1000 points per room + time bonus
                        self.high_score = max(self.high_score, self.total_score)
                        self.state = STATE_VICTORY
                        print("¡Juego completado! Victoria.")

                        # Posicionar al jugador según la sala de destino
                        if isinstance(current_room, ScrumArtifactsRoom):  # Si va hacia la Sala 2 de SCRUM
                            self.player.rect.x = WINDOW_WIDTH - self.player.width - 20  # 20 píxeles desde el borde derecho
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 20  # 20 píxeles desde el borde inferior
                        elif isinstance(current_room, PMBOKPlanningRoom):  # Si va hacia la Sala 2 de PMBOK
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 50  # 50 píxeles desde el borde inferior
                        elif isinstance(current_room, PMBOKExecutionRoom):  # Si va hacia la Sala 3 de PMBOK
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 50  # 50 píxeles desde el borde inferior
                        elif isinstance(current_room, PMBOKClosingRoom):  # Si va hacia la Sala 4 de PMBOK
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - self.player.height - 50  # 50 píxeles desde el borde inferior
                        else:  # Si va hacia la Sala 3 de SCRUM
                            self.player.rect.x = WINDOW_WIDTH // 2
                            self.player.rect.y = WINDOW_HEIGHT - 100

                        # Actualizar también las coordenadas x e y del jugador para mantener consistencia
                        self.player.x = self.player.rect.x
                        self.player.y = self.player.rect.y

                        # Imprimir mensaje de depuración
                        print(f"Transición a la siguiente sala: {current_room.__class__.__name__}")

                    # Si es la última sala (ScrumEventsRoom), finalizar el juego
                    elif isinstance(current_room, ScrumEventsRoom):
                        # Incrementar contador de salas completadas
                        self.completed_rooms += 1

                        # Calculate final score based on time left and rooms completed
                        time_left = self.timer.get_time_left()
                        self.time_bonus = int(time_left * 10)  # 10 points per second remaining
                        self.total_score = (self.completed_rooms * 1000) + self.time_bonus  # 1000 points per room + time bonus
                        self.high_score = max(self.high_score, self.total_score)
                        self.state = STATE_VICTORY
                        print("¡Juego completado! Victoria.")

                # Reiniciar el estado de interacción para evitar transiciones inmediatas
                self.player.interacting = False

            # Check if time is up
            if self.timer.is_time_up():
                self.state = STATE_GAME_OVER

    def render(self):
        """
        Render the game based on current state.
        """
        # Clear the screen
        self.screen.fill(BLACK)

        if self.state == STATE_MENU:
            self._render_menu()
        elif self.state == STATE_PATH_SELECTION:
            self._render_path_selection()
        elif self.state == STATE_INSTRUCTIONS:
            self._render_instructions()
        elif self.state == STATE_GAME:
            self._render_game()
        elif self.state == STATE_GAME_OVER:
            self._render_game_over()
        elif self.state == STATE_VICTORY:
            self._render_victory()

    def start_game(self, path):
        """
        Start a new game with the selected path.

        Args:
            path: Selected path (PMBOK or Scrum)
        """
        self.selected_path = path
        self.room_manager = RoomManager(path)
        self.player = Player()
        # Set initial room
        self.player.current_room = self.room_manager.get_current_room()
        self.timer = Timer(ROOM_TIME_LIMIT)
        self.state = STATE_GAME

        # Reset game progress
        self.total_score = 0
        self.completed_rooms = 0
        self.time_bonus = 0

    def _handle_menu_event(self, event):
        """
        Handle events in the menu state.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = STATE_PATH_SELECTION
            elif event.key == pygame.K_i:
                self.state = STATE_INSTRUCTIONS
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _handle_path_selection_event(self, event):
        """
        Handle events in the path selection state.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

        # Si no hay un jugador creado para la selección, créalo
        if not hasattr(self, 'path_selection_player') or self.path_selection_player is None:
            self.path_selection_player = Player()
            # Posicionar al jugador en el centro de la pantalla
            self.path_selection_player.x = WINDOW_WIDTH // 2 - self.path_selection_player.width // 2
            self.path_selection_player.y = WINDOW_HEIGHT // 2 + 50  # Un poco más abajo del centro
            self.path_selection_player.rect.x = int(self.path_selection_player.x)
            self.path_selection_player.rect.y = int(self.path_selection_player.y)

        # Manejar eventos del jugador
        self.path_selection_player.handle_event(event)

        # Verificar si el jugador ha elegido un camino
        # Si el jugador se mueve lo suficientemente a la izquierda, elige SCRUM
        if self.path_selection_player.x < WINDOW_WIDTH // 3:
            self.start_game(PATH_SCRUM)
            self.path_selection_player = None  # Limpiar el jugador de selección

        # Si el jugador se mueve lo suficientemente a la derecha, elige PMBOK
        elif self.path_selection_player.x > (WINDOW_WIDTH * 2) // 3:
            self.start_game(PATH_PMBOK)
            self.path_selection_player = None  # Limpiar el jugador de selección

    def _handle_instructions_event(self, event):
        """
        Handle events in the instructions state.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                self.state = STATE_MENU

    def _handle_game_event(self, event):
        """
        Handle events in the game state.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

        # Get current room
        current_room = self.room_manager.get_current_room()

        # Update player's current room reference
        self.player.current_room = current_room

        # Ya no usamos la transición al tocar el borde superior
        # Ahora todas las transiciones se manejan con el área de transición y la tecla ESPACIO

        # Handle player events
        self.player.handle_event(event)

        # Handle room events
        current_room.handle_event(event)

    def _handle_end_event(self, event):
        """
        Handle events in the end states (game over or victory).

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = STATE_MENU
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _render_menu(self):
        """
        Render the menu screen in Stardew Valley style.
        """
        # Load and scale the background image to fit the window size
        background = pygame.image.load("img/remix_2.png")
        background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.blit(background, (0, 0))

        # Draw decorative elements
        # Top and bottom borders
        border_rect = pygame.Rect(20, 20, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 40)
        draw_decorative_border(self.screen, border_rect, SDV_BROWN, width=3, corner_size=30)

        # Draw title with stylized text
        title_font = assets.fonts["stardew_large"]
        draw_stardew_title(
            self.screen,
            "Escape Room",
            title_font,
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 4 - 30,
            main_color=SDV_YELLOW,
            shadow_color=SDV_BROWN
        )

        subtitle_font = assets.fonts["stardew_medium"]
        draw_stardew_title(
            self.screen,
            "PMBOK vs Scrum",
            subtitle_font,
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 4 + 30,
            main_color=WHITE,
            shadow_color=SDV_DARK_GREEN
        )

        # Draw buttons in Stardew Valley style
        button_width = 250
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2

        # Start button
        start_rect = pygame.Rect(button_x, WINDOW_HEIGHT // 2, button_width, button_height)
        draw_stardew_button(
            self.screen,
            start_rect,
            "Start Game",
            self.font_medium,
            text_color=WHITE,
            bg_color=SDV_BROWN,
            border_color=SDV_LIGHT_BROWN
        )

        # Instructions button
        instructions_rect = pygame.Rect(button_x, WINDOW_HEIGHT // 2 + 70, button_width, button_height)
        draw_stardew_button(
            self.screen,
            instructions_rect,
            "Instructions",
            self.font_medium,
            text_color=WHITE,
            bg_color=SDV_BROWN,
            border_color=SDV_LIGHT_BROWN
        )

        # Exit button
        exit_rect = pygame.Rect(button_x, WINDOW_HEIGHT // 2 + 140, button_width, button_height)
        draw_stardew_button(
            self.screen,
            exit_rect,
            "Exit Game",
            self.font_medium,
            text_color=WHITE,
            bg_color=SDV_BROWN,
            border_color=SDV_LIGHT_BROWN
        )

        # Draw decorative elements
        # Draw small stars/sparkles
        for _ in range(20):
            x = random.randint(30, WINDOW_WIDTH - 30)
            y = random.randint(30, WINDOW_HEIGHT - 30)
            size = random.randint(1, 3)
            brightness = random.uniform(0.5, 1.0)
            color = color_lerp(SDV_YELLOW, WHITE, brightness)
            pygame.draw.circle(self.screen, color, (x, y), size)

        # Draw version text
        version_text = self.font_small.render("v1.0", True, WHITE)
        version_rect = version_text.get_rect(bottomright=(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
        self.screen.blit(version_text, version_rect)

    def _render_path_selection(self):
        """
        Render the path selection screen.
        """
        # Dibujar la imagen de fondo
        background = assets.get_image("common_background")
        self.screen.blit(background, (0, 0))

        # Renderizar al jugador si existe
        if hasattr(self, 'path_selection_player') and self.path_selection_player is not None:
            self.path_selection_player.render(self.screen)

    def _render_instructions(self):
        """
        Render the instructions screen.
        """
        title = self.font_large.render("Instructions", True, WHITE)
        instruction1 = self.font_small.render("Use arrow keys to move the player", True, WHITE)
        instruction2 = self.font_small.render("Move between rooms by reaching the top of the screen", True, WHITE)
        instruction3 = self.font_small.render("Explore each room to learn about project management", True, WHITE)
        instruction4 = self.font_small.render("Progress through all rooms to complete your path", True, WHITE)
        back_text = self.font_small.render("Press ESC or ENTER to go back", True, WHITE)

        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        instruction1_rect = instruction1.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        instruction2_rect = instruction2.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        instruction3_rect = instruction3.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        instruction4_rect = instruction4.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))

        self.screen.blit(title, title_rect)
        self.screen.blit(instruction1, instruction1_rect)
        self.screen.blit(instruction2, instruction2_rect)
        self.screen.blit(instruction3, instruction3_rect)
        self.screen.blit(instruction4, instruction4_rect)
        self.screen.blit(back_text, back_rect)

    def _render_game(self):
        """
        Render the game screen.
        """
        # Ya no se dibuja el fondo común aquí
        # background = assets.get_image("common_background")
        # self.screen.blit(background, (0, 0))

        # Renderizar la sala actual (que puede tener su propio fondo)
        current_room = self.room_manager.get_current_room()
        if current_room:
            current_room.render(self.screen)

        # Renderizar al jugador directamente sobre la sala
        if self.player:
            self.player.render(self.screen)

        # Render UI elements
        self.ui.render_game_ui(self.screen, self.timer)

    def _render_game_over(self):
        """
        Render the game over screen.
        """
        # Draw background panel
        panel_width = 600
        panel_height = 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2

        pygame.draw.rect(self.screen, CHARCOAL,
                        (panel_x, panel_y, panel_width, panel_height),
                        border_radius=15)
        pygame.draw.rect(self.screen, RED,
                        (panel_x, panel_y, panel_width, panel_height),
                        3, border_radius=15)

        # Draw header
        game_over_text = self.font_large.render("Game Over", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 50))
        self.screen.blit(game_over_text, game_over_rect)

        # Draw reason
        reason_text = self.font_medium.render("Time's up! You couldn't escape in time.", True, WHITE)
        reason_rect = reason_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 120))
        self.screen.blit(reason_text, reason_rect)

        # Draw score information
        score_text = self.font_medium.render(f"Your Score: {self.total_score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 180))
        self.screen.blit(score_text, score_rect)

        high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, ORANGE)
        high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 220))
        self.screen.blit(high_score_text, high_score_rect)

        rooms_text = self.font_small.render(f"Rooms Completed: {self.completed_rooms}", True, WHITE)
        rooms_rect = rooms_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 250))
        self.screen.blit(rooms_text, rooms_rect)

        # Draw buttons
        restart_text = self.font_medium.render("Press ENTER to return to menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 320))
        self.screen.blit(restart_text, restart_rect)

        exit_text = self.font_small.render("Press ESC to exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 360))
        self.screen.blit(exit_text, exit_rect)

    def _render_victory(self):
        """
        Render the victory screen.
        """
        # Draw background panel
        panel_width = 700
        panel_height = 500
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2

        pygame.draw.rect(self.screen, CHARCOAL,
                        (panel_x, panel_y, panel_width, panel_height),
                        border_radius=15)
        pygame.draw.rect(self.screen, GREEN,
                        (panel_x, panel_y, panel_width, panel_height),
                        3, border_radius=15)

        # Draw header
        victory_text = self.font_large.render("Victory!", True, GREEN)
        victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 50))
        self.screen.blit(victory_text, victory_rect)

        # Draw congratulations
        congrats_text = self.font_medium.render(f"Congratulations! You've mastered the {self.selected_path.upper()} path.", True, WHITE)
        congrats_rect = congrats_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 120))
        self.screen.blit(congrats_text, congrats_rect)

        # Draw score breakdown
        score_text = self.font_medium.render(f"Final Score: {self.total_score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 180))
        self.screen.blit(score_text, score_rect)

        # Draw score components
        puzzle_score = self.total_score - self.time_bonus
        puzzle_text = self.font_small.render(f"Puzzle Points: {puzzle_score}", True, WHITE)
        puzzle_rect = puzzle_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 230))
        self.screen.blit(puzzle_text, puzzle_rect)

        time_text = self.font_small.render(f"Time Bonus: {self.time_bonus}", True, CYAN)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 260))
        self.screen.blit(time_text, time_rect)

        rooms_text = self.font_small.render(f"Rooms Completed: {self.completed_rooms}", True, WHITE)
        rooms_rect = rooms_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 290))
        self.screen.blit(rooms_text, rooms_rect)

        # Draw high score
        if self.total_score >= self.high_score:
            high_score_text = self.font_medium.render("New High Score!", True, ORANGE)
        else:
            high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, ORANGE)
        high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 340))
        self.screen.blit(high_score_text, high_score_rect)

        # Draw buttons
        restart_text = self.font_medium.render("Press ENTER to return to menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 400))
        self.screen.blit(restart_text, restart_rect)

        exit_text = self.font_small.render("Press ESC to exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 440))
        self.screen.blit(exit_text, exit_rect)
