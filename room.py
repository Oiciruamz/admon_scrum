"""
Room management for the Escape Room game.
"""
import math
import random
import os
import pygame
from settings import *
from educational_content import get_pmbok_content, get_scrum_content
from assets import assets
from utils import draw_text, draw_panel, draw_progress_bar, draw_tooltip, create_particle_effect, update_particles, render_particles
from settings import DEBUG_MODE

class Room:
    """
    Base class for all rooms in the game.
    """
    def __init__(self, name, description, background_color=BLACK, theme="gray"):
        """
        Initialize a room.

        Args:
            name: Room name
            description: Room description
            background_color: Room background color
            theme: Room theme for visuals ("gray", "blue", "green", etc.)
        """
        self.name = name
        self.description = description
        self.background_color = background_color
        self.theme = theme
        self.decorations = []
        self.completed = False
        self.completion_time = 0

        # Room dimensions and position
        self.width = ROOM_WIDTH
        self.height = ROOM_HEIGHT
        self.x = (WINDOW_WIDTH - self.width) // 2
        self.y = (WINDOW_HEIGHT - self.height) // 2

        # Room border
        self.border_width = ROOM_BORDER_WIDTH
        self.border_color = WHITE

        # Fonts
        self.font_large = assets.get_font("large")
        self.font_medium = assets.get_font("medium")
        self.font_small = assets.get_font("small")

        # Create decorative elements
        self._create_decorations()

    def _create_decorations(self):
        """
        Create decorative elements for the room.
        """
        # Add random decorative elements based on theme
        for _ in range(10):
            decoration = {
                'type': random.choice(['dot', 'square', 'line']),
                'x': random.randint(self.x + 20, self.x + self.width - 20),
                'y': random.randint(self.y + 20, self.y + self.height - 20),
                'size': random.randint(2, 8),
                'color': self._get_theme_color(random.uniform(0.7, 1.0)),
                'alpha': random.randint(40, 120),
                'speed': random.uniform(0.01, 0.05),
                'time': random.uniform(0, 2 * math.pi)
            }
            self.decorations.append(decoration)

    def _get_theme_color(self, brightness=1.0):
        """
        Get a color based on the room theme and brightness.

        Args:
            brightness: Color brightness factor (0.0 to 1.0)

        Returns:
            RGB color tuple
        """
        base_colors = {
            'gray': GRAY,
            'blue': LIGHT_BLUE,
            'green': GREEN,
            'red': RED,
            'yellow': YELLOW,
            'purple': PURPLE,
            'cyan': CYAN,
            'orange': ORANGE
        }

        base_color = base_colors.get(self.theme, GRAY)

        # Adjust brightness
        r = min(255, int(base_color[0] * brightness))
        g = min(255, int(base_color[1] * brightness))
        b = min(255, int(base_color[2] * brightness))

        return (r, g, b)

    def update(self):
        """
        Update room state.
        """
        # Update decorations
        self._update_decorations()

        # Check if all required objects are in correct state
        if not self.completed:
            self._check_completion()
        else:
            self.completion_time += 1

    def _update_decorations(self):
        """
        Update decorative elements animation.
        """
        for decoration in self.decorations:
            decoration['time'] += decoration['speed']

            # Make decorations pulse or move slightly
            if decoration['type'] == 'dot':
                decoration['size'] = 2 + math.sin(decoration['time']) * 2
            elif decoration['type'] == 'square':
                decoration['size'] = 3 + math.cos(decoration['time']) * 2
            elif decoration['type'] == 'line':
                decoration['size'] = 4 + math.sin(decoration['time'] * 2) * 2

    def handle_event(self, event):
        """
        Handle events for the room.

        Args:
            event: Pygame event
        """
        pass

    def render(self, screen):
        """
        Render the room.

        Args:
            screen: Pygame surface to render on
        """
        # Render the room background
        self._render_room_background(screen)
        # Render decorations
        self._render_decorations(screen)

    def _render_room_background(self, screen):
        """
        Render the room background.

        Args:
            screen: Pygame surface to render on
        """
        # Get room background image based on theme
        room_bg = assets.get_image(f"room_{self.theme}")
        screen.blit(room_bg, (self.x, self.y))

        # Draw room border
        pygame.draw.rect(screen, self.border_color,
                        (self.x, self.y, self.width, self.height),
                        self.border_width)

    def _render_decorations(self, screen):
        """
        Render decorative elements.

        Args:
            screen: Pygame surface to render on
        """
        for decoration in self.decorations:
            color = (*decoration['color'], decoration['alpha'])

            if decoration['type'] == 'dot':
                pygame.draw.circle(
                    screen,
                    color,
                    (int(decoration['x']), int(decoration['y'])),
                    int(decoration['size'])
                )
            elif decoration['type'] == 'square':
                size = int(decoration['size'])
                pygame.draw.rect(
                    screen,
                    color,
                    (int(decoration['x'] - size/2), int(decoration['y'] - size/2), size, size)
                )
            elif decoration['type'] == 'line':
                size = int(decoration['size'])
                pygame.draw.line(
                    screen,
                    color,
                    (int(decoration['x'] - size), int(decoration['y'])),
                    (int(decoration['x'] + size), int(decoration['y'])),
                    2
                )

    def is_completed(self):
        """
        Check if the room is completed.

        Returns:
            Boolean indicating if the room is completed
        """
        return self.completed

    def _check_completion(self):
        """
        Check if all required conditions are met to complete the room.
        This should be overridden by subclasses.
        """
        pass

    def check_collision(self, player_rect):
        """
        Check if player's feet collide with any collision rectangle.

        Args:
            player_rect: The player's feet collision rectangle
        """
        if not hasattr(self, 'collision_rects'):
            return False
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)


class RoomManager:
    """
    Manages rooms and transitions between them.
    """
    def __init__(self, path):
        """
        Initialize the room manager with rooms for the selected path.

        Args:
            path: Selected path (PMBOK or Scrum)
        """
        self.rooms = []
        self.current_room_index = 0

        # Create rooms based on selected path
        if path == PATH_PMBOK:
            self._create_pmbok_rooms()
        elif path == PATH_SCRUM:
            self._create_scrum_rooms()

    def get_current_room(self):
        """
        Get the current room.

        Returns:
            Current room object
        """
        return self.rooms[self.current_room_index]

    def go_to_next_room(self):
        """
        Advance to the next room if available.

        Returns:
            Boolean indicating if successfully moved to next room
        """
        if self.has_next_room():
            self.current_room_index += 1
            return True
        return False

    def has_next_room(self):
        """
        Check if there is a next room available.

        Returns:
            Boolean indicating if there is a next room
        """
        return self.current_room_index < len(self.rooms) - 1

    def _create_pmbok_rooms(self):
        """
        Create rooms for the PMBOK path.
        """
        # Get PMBOK educational content
        pmbok_content = get_pmbok_content()

        # Room 1: Initiation
        room1 = PMBOKInitiationRoom(pmbok_content[0])
        self.rooms.append(room1)

        # Room 2: Planning
        room2 = PMBOKPlanningRoom(pmbok_content[1])
        self.rooms.append(room2)

        # Room 3: Execution
        room3 = PMBOKExecutionRoom(pmbok_content[2])
        self.rooms.append(room3)

        # Room 4: Closing
        room4 = PMBOKClosingRoom(pmbok_content[3])
        self.rooms.append(room4)

    def _create_scrum_rooms(self):
        """
        Create rooms for the Scrum path.
        """
        # Get Scrum educational content
        scrum_content = get_scrum_content()

        # Room 1: Scrum Roles
        room1 = ScrumRolesRoom(scrum_content[0])
        self.rooms.append(room1)

        # Room 2: Scrum Artifacts
        room2 = ScrumArtifactsRoom(scrum_content[1])
        self.rooms.append(room2)

        # Room 3: Scrum Events
        room3 = ScrumEventsRoom(scrum_content[2])
        self.rooms.append(room3)


# PMBOK Room Classes
class PMBOKInitiationRoom(Room):
    def __init__(self, content):
        super().__init__("PMBOK: Initiation Phase", "Learn about project initiation", GRAY, "gray")
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_1_pmbok.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición

        # Definir las áreas de colisión especificadas
        self.collision_rects = [
            # Rectángulos donde el jugador no puede acceder
            pygame.Rect(218, 98, 381-218, 317-98),     # Rectángulo 1
            pygame.Rect(383, 98, 446-383, 310-98),     # Rectángulo 2
            pygame.Rect(449, 90, 580-449, 336-90),     # Rectángulo 3
            pygame.Rect(582, 90, 602-582, 333-90),     # Rectángulo 4
            pygame.Rect(0, 159, 19-0, 311-159),        # Rectángulo 5
            pygame.Rect(18, 161, 108-18, 358-161),     # Rectángulo 6
            pygame.Rect(108, 158, 213-108, 342-158),   # Rectángulo 7
            pygame.Rect(0, 381, 186-0, 566-381),       # Rectángulo 8
            pygame.Rect(415, 371, 596-415, 499-371)    # Rectángulo 9
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Usar el rectángulo especificado: (218, 98) a (381, 317) como área de transición
        transition_rect = pygame.Rect(
            218 + self.bg_x_offset,  # Coordenada X inicial
            98 + self.bg_y_offset,   # Coordenada Y inicial
            381 - 218,               # Ancho
            317 - 98                 # Alto
        )

        # Verificar si el rectángulo del jugador colisiona con el área de transición
        inside_area = transition_rect.colliderect(player_rect)

        # Dibujar el área de transición en modo debug para visualización
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 0), transition_rect, 2)
            if inside_area:
                # Si el jugador está dentro, dibujar un indicador más visible
                pygame.draw.rect(pygame.display.get_surface(), (255, 0, 0), transition_rect, 1)
                print("Jugador en área de transición de PMBOKInitiationRoom")

        # Si el jugador está dentro del área, guardar esta información
        if inside_area:
            self.player_in_transition_area = True
        else:
            self.player_in_transition_area = False

        return inside_area

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Nuevo rectángulo PMBOK: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []


class PMBOKPlanningRoom(Room):
    def __init__(self, content):
        super().__init__("PMBOK: Planning Phase", "Learn about project planning", LIGHT_BLUE)
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_2_pmbok.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición

        # Definir las áreas de colisión especificadas
        self.collision_rects = [
            # Rectángulos donde el jugador no puede acceder
            pygame.Rect(203, 104, 374-203, 304-104),  # Rectángulo 1 (área de transición)
            pygame.Rect(409, 70, 588-409, 366-70),    # Rectángulo 2
            pygame.Rect(12, 233, 196-12, 410-233)     # Rectángulo 3
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Definir un área de transición (ajustar según la imagen)
        transition_rect = pygame.Rect(
            300 + self.bg_x_offset,  # Ajustar según la imagen
            100 + self.bg_y_offset,  # Ajustar según la imagen
            100,  # Ancho del área
            150   # Alto del área
        )

        # Verificar si el rectángulo del jugador colisiona con el área de transición
        inside_area = transition_rect.colliderect(player_rect)

        # Dibujar el área de transición en modo debug para visualización
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 0), transition_rect, 2)
            if inside_area:
                # Si el jugador está dentro, dibujar un indicador más visible
                pygame.draw.rect(pygame.display.get_surface(), (255, 0, 0), transition_rect, 1)
                print("Jugador en área de transición de PMBOKPlanningRoom")

        # Si el jugador está dentro del área, guardar esta información
        if inside_area:
            self.player_in_transition_area = True
        else:
            self.player_in_transition_area = False

        return inside_area

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Nuevo rectángulo PMBOK: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []


class PMBOKExecutionRoom(Room):
    def __init__(self, content):
        super().__init__("PMBOK: Execution Phase", "Learn about project execution", GREEN)
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_3_pmbok.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición

        # Definir las áreas de colisión especificadas
        self.collision_rects = [
            # Rectángulos donde el jugador no puede acceder
            pygame.Rect(397, 46, 590-397, 499-46),    # Rectángulo 1
            pygame.Rect(14, 74, 192-14, 346-74),      # Rectángulo 2
            pygame.Rect(231, 142, 371-231, 330-142),  # Rectángulo 3 (también es el área de transición)
            pygame.Rect(24, 366, 202-24, 522-366)     # Rectángulo 4
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Usar el rectángulo especificado: (231, 142) a (371, 330) como área de transición
        transition_rect = pygame.Rect(
            231 + self.bg_x_offset,  # Coordenada X inicial
            142 + self.bg_y_offset,  # Coordenada Y inicial
            371 - 231,               # Ancho
            330 - 142                # Alto
        )

        # Verificar si el rectángulo del jugador está cerca del borde del área de transición
        # Creamos un rectángulo ligeramente más grande para detectar cuando el jugador está cerca
        proximity_rect = transition_rect.inflate(60, 60)  # 60 píxeles más grande en cada dirección

        # Verificar si el rectángulo del jugador colisiona con el área de proximidad
        near_area = proximity_rect.colliderect(player_rect)

        # Dibujar el área de transición en modo debug para visualización
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 0), transition_rect, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 0, 255), proximity_rect, 1)  # Área de proximidad en azul
            if near_area:
                # Si el jugador está cerca, dibujar un indicador más visible
                pygame.draw.rect(pygame.display.get_surface(), (255, 0, 0), proximity_rect, 1)
                print("Jugador cerca del área de transición de PMBOKExecutionRoom")

        # Si el jugador está cerca del área, guardar esta información
        # Usamos near_area en lugar de inside_area porque el jugador no puede entrar debido a la colisión
        self.player_in_transition_area = near_area

        return near_area

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Nuevo rectángulo PMBOK: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []


class PMBOKClosingRoom(Room):
    def __init__(self, content):
        super().__init__("PMBOK: Closing Phase", "Learn about project closure", RED)
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_4_pmbok.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición

        # Definir las áreas de colisión especificadas
        self.collision_rects = [
            # Rectángulos donde el jugador no puede acceder
            pygame.Rect(230, 146, 376-230, 322-146),  # Rectángulo 1 (área de transición)
            pygame.Rect(390, 309, 594-390, 477-309),  # Rectángulo 2
            pygame.Rect(32, 394, 125-32, 521-394),    # Rectángulo 3
            pygame.Rect(21, 141, 190-21, 370-141)     # Rectángulo 4
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Usar el rectángulo especificado: (230, 146) a (376, 322) como área de transición
        transition_rect = pygame.Rect(
            230 + self.bg_x_offset,  # Coordenada X inicial
            146 + self.bg_y_offset,  # Coordenada Y inicial
            376 - 230,               # Ancho
            322 - 146                # Alto
        )

        # Verificar si el rectángulo del jugador está cerca del borde del área de transición
        # Creamos un rectángulo ligeramente más grande para detectar cuando el jugador está cerca
        proximity_rect = transition_rect.inflate(60, 60)  # 60 píxeles más grande en cada dirección

        # Verificar si el rectángulo del jugador colisiona con el área de proximidad
        near_area = proximity_rect.colliderect(player_rect)

        # Dibujar el área de transición en modo debug para visualización
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 0), transition_rect, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 0, 255), proximity_rect, 1)  # Área de proximidad en azul
            if near_area:
                # Si el jugador está cerca, dibujar un indicador más visible
                pygame.draw.rect(pygame.display.get_surface(), (255, 0, 0), proximity_rect, 1)
                print("Jugador cerca del área de transición de PMBOKClosingRoom")

        # Si el jugador está cerca del área, guardar esta información
        # Usamos near_area en lugar de inside_area porque el jugador no puede entrar debido a la colisión
        self.player_in_transition_area = near_area

        return near_area

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Nuevo rectángulo PMBOK: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []


# Scrum Room Classes
class ScrumRolesRoom(Room):
    def __init__(self, content):
        super().__init__("Scrum Roles", "Learn about the different roles in Scrum", BLACK, "blue")
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_1_scrum.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True

        # Definir las áreas de colisión usando rectángulos
        # Las coordenadas son relativas a la imagen
        self.collision_rects = [
            # Rectángulos de colisión para la Sala 1
            pygame.Rect(210, 92, 47, 123),      # Rectángulo vertical superior
            pygame.Rect(202, 95, 189, 200),     # Mesa grande superior
            pygame.Rect(190, 12, 203, 282),     # Área superior completa
            pygame.Rect(394, 226, 205, 203),    # Mesa grande derecha
            pygame.Rect(0, 122, 50, 220),       # Borde izquierdo
            pygame.Rect(52, 126, 90, 256),      # Área izquierda media
            pygame.Rect(143, 126, 50, 211),     # Área izquierda superior
            pygame.Rect(86, 375, 200, 143)      # Área inferior izquierda
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room"""
        transition_rect = pygame.Rect(
            210 + self.bg_x_offset,  # Ajustar por el offset del fondo
            92 + self.bg_y_offset,   # Ajustar por el offset del fondo
            47,  # Ancho del área (257 - 210)
            123  # Alto del área (215 - 92)
        )
        return transition_rect.colliderect(player_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Sala 1 - Nuevo rectángulo: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

        # Se ha eliminado el mensaje de texto que pedía presionar ESPACIO
        # También se ha eliminado la flecha amarilla

class ScrumArtifactsRoom(Room):
    def __init__(self, content):
        super().__init__("Scrum: Artifacts", "Learn about Scrum artifacts", GREEN)
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_2_scrum.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True

        # Definir las áreas de colisión usando rectángulos
        self.collision_rects = [
            pygame.Rect(186, 105, 199, 245),  # Rectángulo central (área de transición)
            pygame.Rect(388, 62, 102, 288),   # Rectángulo derecho superior
            pygame.Rect(478, 245, 121, 193),  # Rectángulo derecho inferior
            pygame.Rect(4, 271, 184, 176)     # Rectángulo izquierdo inferior
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room"""
        transition_rect = pygame.Rect(
            186 + self.bg_x_offset,  # Ajustar por el offset del fondo
            105 + self.bg_y_offset,  # Ajustar por el offset del fondo
            199,  # Ancho del área (385 - 186)
            245   # Alto del área (350 - 105)
        )
        return transition_rect.colliderect(player_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Nuevo rectángulo: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

class ScrumEventsRoom(Room):
    def __init__(self, content):
        super().__init__("Scrum: Events", "Learn about Scrum events", YELLOW)
        self.content = content
        self.collision_rects = []  # Lista para los rectángulos de colisión

        # Cargar y escalar la imagen de fondo una sola vez
        bg_path = os.path.join("img", "sala_3_scrum.png")
        try:
            background = pygame.image.load(bg_path).convert()
            bg_width, bg_height = background.get_width(), background.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)
            self.scaled_bg = pygame.transform.scale(background, (new_width, new_height))
            self.bg_x_offset = (WINDOW_WIDTH - new_width) // 2
            self.bg_y_offset = (WINDOW_HEIGHT - new_height) // 2
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.scaled_bg = None

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición

        # Definir las áreas de colisión usando los rectángulos especificados
        self.collision_rects = [
            # Rectángulos donde el jugador no puede acceder
            pygame.Rect(182, 24, 594-182, 287-24),     # Rectángulo superior
            pygame.Rect(11, 417, 181-11, 510-417),     # Rectángulo inferior izquierdo
            pygame.Rect(415, 288, 594-415, 427-288),   # Rectángulo derecho
            pygame.Rect(15, 89, 178-15, 272-89)        # Rectángulo izquierdo
        ]

        # Convertir las coordenadas relativas a absolutas
        for rect in self.collision_rects:
            rect.x += self.bg_x_offset
            rect.y += self.bg_y_offset

    def check_collision(self, player_rect):
        """Check if player collides with any collision rectangle"""
        return any(rect.colliderect(player_rect) for rect in self.collision_rects)

    def check_transition_area(self, player_rect):
        """Check if player is in the transition area to next room (para finalizar el juego)"""
        # Importar pygame al inicio del método para evitar el error UnboundLocalError
        import pygame

        # Usar el rectángulo especificado: (15, 89) a (178, 272)
        transition_rect = pygame.Rect(
            15 + self.bg_x_offset,   # Coordenada X inicial
            89 + self.bg_y_offset,   # Coordenada Y inicial
            178 - 15,                # Ancho
            272 - 89                 # Alto
        )

        # Calcular el centro del jugador
        player_center_x = player_rect.x + player_rect.width // 2
        player_center_y = player_rect.y + player_rect.height // 2

        # Verificar si el centro del jugador está dentro del área de transición
        inside_area = (transition_rect.x <= player_center_x <= transition_rect.x + transition_rect.width and
                       transition_rect.y <= player_center_y <= transition_rect.y + transition_rect.height)

        # Dibujar el área de transición en modo debug para visualización
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 0), transition_rect, 2)
            if inside_area:
                # Si el jugador está dentro, dibujar un indicador más visible
                pygame.draw.rect(pygame.display.get_surface(), (255, 0, 0), transition_rect, 1)

        # Si el jugador está dentro del área, guardar esta información para mostrar un mensaje
        if inside_area:
            self.player_in_transition_area = True
            # Imprimir mensaje de depuración
            if DEBUG_MODE:
                print("Jugador en área de transición de ScrumEventsRoom")
        else:
            self.player_in_transition_area = False

        return inside_area

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo para iniciar un rectángulo
                self.start_pos = pygame.mouse.get_pos()
            elif event.button == 3 and hasattr(self, 'start_pos'):  # Clic derecho para completar el rectángulo
                end_pos = pygame.mouse.get_pos()
                # Convertir a coordenadas relativas
                rel_start_x = self.start_pos[0] - self.bg_x_offset
                rel_start_y = self.start_pos[1] - self.bg_y_offset
                rel_end_x = end_pos[0] - self.bg_x_offset
                rel_end_y = end_pos[1] - self.bg_y_offset
                print(f"Nuevo rectángulo: ({rel_start_x}, {rel_start_y}) a ({rel_end_x}, {rel_end_y})")

                # Crear el rectángulo (asegurando que width y height sean positivos)
                x = min(self.start_pos[0], end_pos[0])
                y = min(self.start_pos[1], end_pos[1])
                width = abs(end_pos[0] - self.start_pos[0])
                height = abs(end_pos[1] - self.start_pos[1])

                self.collision_rects.append(pygame.Rect(x, y, width, height))
                delattr(self, 'start_pos')
        elif event.type == pygame.KEYDOWN:  # Separar el evento de teclado
            if event.key == pygame.K_c:  # Tecla 'c' para limpiar todos los rectángulos
                self.collision_rects = []

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if DEBUG_MODE:
            # Dibujar los rectángulos existentes
            for rect in self.collision_rects:
                pygame.draw.rect(screen, RED, rect, 2)

            # Si hay un rectángulo en proceso (entre clic izquierdo y derecho)
            if hasattr(self, 'start_pos'):
                current_pos = pygame.mouse.get_pos()
                preview_rect = pygame.Rect(
                    min(self.start_pos[0], current_pos[0]),
                    min(self.start_pos[1], current_pos[1]),
                    abs(current_pos[0] - self.start_pos[0]),
                    abs(current_pos[1] - self.start_pos[1])
                )
                pygame.draw.rect(screen, (255, 165, 0), preview_rect, 2)  # Naranja para el preview

        # Se ha eliminado el mensaje de texto que pedía presionar ESPACIO
        # También se ha eliminado la flecha amarilla