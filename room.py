"""
Room management for the Escape Room game.
"""
import math
import random
import os
import pygame
from activities.pmbok_closing_activity import PMBOKClosingActivity
from settings import *
from educational_content import get_pmbok_content, get_scrum_content
from assets import assets
from utils import draw_text, draw_panel, draw_progress_bar, draw_tooltip
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
    def __init__(self, path, game_instance):
        self.game = game_instance
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

        # Room 4: Closing - Pasamos adicionalmente la referencia al juego
        closing_content = {"content": pmbok_content[4], "game_instance": self.game}
        room4 = PMBOKClosingRoom(closing_content)
        self.rooms.append(room4)

    def _create_scrum_rooms(self):
        """
        Create rooms for the Scrum path.
        """
        # Get Scrum educational content
        scrum_content = get_scrum_content()

        # Room 1: Scrum Roles
        room1 = ScrumRolesRoom(scrum_content[0],self.game)
        self.rooms.append(room1)

        # Room 2: Scrum Artifacts
        room2 = ScrumArtifactsRoom(scrum_content[1],self.game)
        self.rooms.append(room2)

        # Room 3: Scrum Events
        room3 = ScrumEventsRoom(scrum_content[2])
        self.rooms.append(room3)


# PMBOK Room Classes
class PMBOKActivity:
    """
    Clase para manejar la actividad educativa de PMBOK.
    """
    def __init__(self):
        self.active = False
        self.font_large = assets.get_font("large")
        self.font_medium = assets.get_font("medium")
        self.font_small = assets.get_font("small")

        # Sistema de intentos y fallo
        self.max_errors = 3  # Número máximo de errores permitidos
        self.error_count = 0  # Contador de errores cometidos
        self.failed = False  # Flag para indicar si la actividad ha fallado (game over)

        # Elementos de la actividad - Textos resumidos para mejor visualización
        self.items = [
            {"text": "Crear un videojuego educativo en 2D, tipo escape room, para aprender metodologías PMBOK y Scrum mediante desafíos interactivos.", "position": "left", "correct_target": "Definición del proyecto"},
            {"text": "Desarrollo de un juego con dos caminos de aprendizaje (PMBOK y Scrum), cada uno con salas que representan etapas de las metodologías.", "position": "left", "correct_target": "Alcance del proyecto"},
            {"text": "Interfaz intuitiva con menú de selección. PMBOK: 4 salas con desafíos. Scrum: 3 salas con ejercicios de planificación ágil.", "position": "left", "correct_target": "Alcance del producto"}
        ]

        self.targets = [
            {"name": "Definición del proyecto", "position": "right", "matched": False},
            {"name": "Alcance del proyecto", "position": "right", "matched": False},
            {"name": "Alcance del producto", "position": "right", "matched": False}
        ]

        # Colores mejorados
        self.bg_gradient_top = (40, 40, 70)  # Azul oscuro
        self.bg_gradient_bottom = (20, 20, 35)  # Azul más oscuro
        self.panel_bg_color = (30, 35, 60)  # Azul oscuro para el panel principal
        self.panel_border_color = (80, 130, 200)  # Azul claro para bordes
        self.title_color = (220, 220, 255)  # Blanco azulado para títulos

        # Para las tarjetas
        self.item_bg = (45, 60, 100)  # Azul medio
        self.item_hover_bg = (55, 70, 115)  # Azul medio más claro (para hover)
        self.item_selected_bg = (70, 85, 130)  # Azul más claro cuando está seleccionado
        self.item_matched_color = (100, 200, 120)  # Verde para elementos emparejados

        # Para los objetivos
        self.target_bg = (65, 50, 90)  # Púrpura oscuro
        self.target_border = (150, 120, 200)  # Púrpura claro
        self.target_matched_color = (120, 200, 100)  # Verde para objetivos emparejados

        # Efectos visuales adicionales
        self.use_particle_effects = True
        self.particles = []  # Para efectos de partículas cuando hay un match correcto
        self.animation_time = 0
        self.pulse_speed = 0.05
        
        # Hover y selección
        self.hover_item = None
        self.hover_target = None
        self.selected_item = None
        self.completed = False
        self.show_result = False
        self.result_message = ""
        self.result_color = GREEN

    def activate(self):
        """Activar la actividad"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.hover_item = None
        self.hover_target = None
        self.selected_item = None
        self.particles = []
        self.error_count = 0  # Reiniciar contador de errores
        self.failed = False  # Reiniciar estado de fallo
        
        # Reiniciar el estado de los elementos
        for item in self.items:
            item["matched"] = False
        for target in self.targets:
            target["matched"] = False

    def deactivate(self):
        """Desactivar la actividad"""
        self.active = False

    def handle_event(self, event):
        """Manejar eventos de la actividad"""
        if not self.active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                mouse_pos = pygame.mouse.get_pos()

                # Si se muestra un resultado (éxito o error)
                if self.show_result:
                    # Si la actividad está completada, mostrar el botón de cerrar
                    if self.completed:
                        # Usar las mismas dimensiones definidas en _render_result_modal
                        modal_width = 500
                        modal_height = 150
                        modal_x = (WINDOW_WIDTH - modal_width) // 2
                        modal_y = (WINDOW_HEIGHT - modal_height) // 2
                        # Botón ACEPTAR con dimensiones actualizadas
                        close_rect = pygame.Rect(modal_x + modal_width // 2 - 70, modal_y + modal_height - 40, 140, 35)
                        if close_rect.collidepoint(mouse_pos):
                            self.deactivate()
                            return
                    elif self.failed:
                        # Si la actividad ha fallado, no se puede cerrar el mensaje ya que llevará al Game Over
                        # El game over se activará en la próxima actualización del juego
                        return
                    else:
                        # Si es un mensaje de error, cualquier clic lo cierra
                        # Añadir un botón específico para cerrar el mensaje de error
                        error_close_rect = pygame.Rect(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, 80, 30)
                        if error_close_rect.collidepoint(mouse_pos):
                            self.show_result = False
                            return

                    # Si se hace clic en cualquier otro lugar, también cerrar el mensaje de error
                    # pero solo si no está completada la actividad y no ha fallado
                    if not self.completed and not self.failed:
                        self.show_result = False
                        return

                # Verificar si se seleccionó un elemento
                if self.selected_item is None:
                    for i, item in enumerate(self.items):
                        item_rect = self._get_item_rect(i)
                        if item_rect.collidepoint(mouse_pos) and not item.get("matched", False):
                            self.selected_item = i
                            # Sonido de selección (simulado)
                            print(f"Elemento seleccionado: {i}")
                            return  # Salir después de seleccionar un elemento
                else:
                    # Verificar si se seleccionó un objetivo
                    for i, target in enumerate(self.targets):
                        target_rect = self._get_target_rect(i)
                        if target_rect.collidepoint(mouse_pos) and not target.get("matched", False):
                            # Comprobar si la relación es correcta
                            if self.items[self.selected_item]["correct_target"] == target["name"]:
                                # Relación correcta - Crear partículas para celebrar
                                if self.use_particle_effects:
                                    self._create_success_particles(target_rect.center)
                                
                                # Marcar como emparejados
                                self.items[self.selected_item]["matched"] = True
                                target["matched"] = True

                                # Verificar si se completó la actividad
                                if all(item.get("matched", False) for item in self.items):
                                    self.completed = True
                                    self.show_result = True
                                    self.result_message = "¡Excelente! Has relacionado correctamente todos los elementos."
                                    self.result_color = GREEN
                            else:
                                # Relación incorrecta
                                self.error_count += 1  # Incrementar contador de errores
                                self.show_result = True
                                
                                # Verificar si se ha alcanzado el límite de errores
                                if self.error_count >= self.max_errors:
                                    self.failed = True
                                    self.result_message = f"¡Has agotado tus {self.max_errors} intentos! Game Over."
                                    self.result_color = RED
                                else:
                                    # Todavía tiene intentos, mostrar cuántos le quedan
                                    remaining = self.max_errors - self.error_count
                                    self.result_message = f"Relación incorrecta. Te quedan {remaining} {'intento' if remaining == 1 else 'intentos'}."
                                    self.result_color = RED

                            self.selected_item = None
                            return  # Salir después de intentar una relación

                    # Si se hizo clic en cualquier otro lugar, deseleccionar
                    if not any(self._get_target_rect(i).collidepoint(mouse_pos) for i in range(len(self.targets))):
                        self.selected_item = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Actualizar elementos bajo el cursor (hover)
            mouse_pos = pygame.mouse.get_pos()
            
            # Detectar hover en elementos
            self.hover_item = None
            for i, item in enumerate(self.items):
                if not item.get("matched", False):  # Solo hover en elementos no emparejados
                    if self._get_item_rect(i).collidepoint(mouse_pos):
                        self.hover_item = i
                        break
            
            # Detectar hover en objetivos
            self.hover_target = None
            for i, target in enumerate(self.targets):
                if not target.get("matched", False):  # Solo hover en objetivos no emparejados
                    if self._get_target_rect(i).collidepoint(mouse_pos):
                        self.hover_target = i
                        break

    def _create_success_particles(self, position):
        """Crear partículas para un emparejamiento exitoso"""
        for _ in range(20):  # Crear 20 partículas
            angle = random.uniform(0, math.pi * 2)  # Ángulo aleatorio
            speed = random.uniform(2, 5)  # Velocidad aleatoria
            size = random.uniform(2, 6)  # Tamaño aleatorio
            lifetime = random.uniform(30, 60)  # Vida en frames
            color = (
                random.randint(180, 255),  # R
                random.randint(180, 255),  # G
                random.randint(100, 200)   # B
            )
            
            particle = {
                'x': position[0],
                'y': position[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'age': 0
            }
            self.particles.append(particle)

    def _update_particles(self):
        """Actualizar partículas (posición, vida, etc.)"""
        particles_to_keep = []
        
        for particle in self.particles:
            # Actualizar posición
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Aplicar gravedad suave
            particle['vy'] += 0.1
            
            # Envejecer la partícula
            particle['age'] += 1
            
            # Si la partícula sigue viva, conservarla
            if particle['age'] < particle['lifetime']:
                particles_to_keep.append(particle)
        
        # Reemplazar la lista de partículas
        self.particles = particles_to_keep

    def render(self, screen):
        """Renderizar la actividad"""
        if not self.active:
            return

        # Actualizar efectos visuales
        self.animation_time += 1
        if self.use_particle_effects:
            self._update_particles()
            
        # Eliminar el código de temporización automática
        
        # Dibujar el fondo con gradiente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            # Calcular color interpolado para cada línea del gradiente
            ratio = y / WINDOW_HEIGHT
            color = (
                int(self.bg_gradient_top[0] * (1 - ratio) + self.bg_gradient_bottom[0] * ratio),
                int(self.bg_gradient_top[1] * (1 - ratio) + self.bg_gradient_bottom[1] * ratio),
                int(self.bg_gradient_top[2] * (1 - ratio) + self.bg_gradient_bottom[2] * ratio)
            )
            pygame.draw.line(overlay, color, (0, y), (WINDOW_WIDTH, y))
        
        # Añadir un poco de transparencia
        overlay.set_alpha(230)
        screen.blit(overlay, (0, 0))

        # Dibujar estrellas aleatorias en el fondo para efecto espacial
        for _ in range(50):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            size = random.choice([1, 1, 1, 2, 2, 3])  # Mayormente estrellas pequeñas
            brightness = random.randint(120, 255)
            # Hacer parpadear algunas estrellas
            if random.random() < 0.1:  # 10% de probabilidad de parpadeo
                brightness = random.randint(50, 150)
            
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

        # Dibujar el panel principal con un borde iluminado
        panel_width = 600
        panel_height = 480
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Panel con un borde suave
        pygame.draw.rect(screen, self.panel_bg_color, (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        
        # Borde iluminado con efecto pulsante
        border_glow = int(180 + 75 * math.sin(self.animation_time * self.pulse_speed))
        border_color = (
            min(255, self.panel_border_color[0] * border_glow // 180),
            min(255, self.panel_border_color[1] * border_glow // 180),
            min(255, self.panel_border_color[2] * border_glow // 180)
        )
        pygame.draw.rect(screen, border_color, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)

        # Dibujar título con un efecto de sombra
        font_title = pygame.font.Font(None, 26)  # Fuente más grande y legible
        shadow_text = font_title.render("Relaciona los elementos con su contexto", True, (20, 20, 40))
        title_text = font_title.render("Relaciona los elementos con su contexto", True, self.title_color)
        
        # Primero la sombra ligeramente desplazada
        shadow_rect = shadow_text.get_rect(center=(WINDOW_WIDTH // 2 + 2, panel_y + 40 + 2))
        screen.blit(shadow_text, shadow_rect)
        
        # Luego el texto principal
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 40))
        screen.blit(title_text, title_rect)

        # Dibujar los elementos a relacionar con efecto de hover y selección
        for i, item in enumerate(self.items):
            item_rect = self._get_item_rect(i)
            
            # Determinar color de fondo según estado
            if item.get("matched", False):
                bg_color = self.item_matched_color
                text_color = (20, 20, 20)  # Casi negro para contrastar con verde
                border_width = 2
            elif self.selected_item == i:
                bg_color = self.item_selected_bg
                text_color = WHITE
                border_width = 3
            elif self.hover_item == i:
                bg_color = self.item_hover_bg
                text_color = WHITE
                border_width = 2
            else:
                bg_color = self.item_bg
                text_color = (220, 220, 220)  # Blanco ligeramente atenuado
                border_width = 2
            
            # Dibujar fondo del elemento con sombra
            shadow_rect = item_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(screen, (20, 20, 30), shadow_rect, border_radius=10)
            
            # Dibujar el elemento principal
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=10)
            pygame.draw.rect(screen, self.panel_border_color, item_rect, border_width, border_radius=10)
            
            # Añadir un indicador visual (icono) al inicio
            icon_radius = 10
            icon_x = item_rect.x + 20
            icon_y = item_rect.y + item_rect.height // 2
            
            if item.get("matched", False):
                # Dibujar un check si está emparejado
                pygame.draw.circle(screen, self.item_matched_color, (icon_x, icon_y), icon_radius)
                pygame.draw.circle(screen, self.panel_border_color, (icon_x, icon_y), icon_radius, 1)
                # Dibujar un símbolo de check
                pygame.draw.line(screen, (20, 20, 20), (icon_x - 5, icon_y), (icon_x - 2, icon_y + 4), 2)
                pygame.draw.line(screen, (20, 20, 20), (icon_x - 2, icon_y + 4), (icon_x + 5, icon_y - 4), 2)
            else:
                # Dibujar un círculo para elementos no emparejados
                pygame.draw.circle(screen, (200, 200, 200), (icon_x, icon_y), icon_radius)
                pygame.draw.circle(screen, self.panel_border_color, (icon_x, icon_y), icon_radius, 1)

            # Dibujar el texto del elemento con mejor formato
            text = item["text"]
            words = text.split()
            lines = []
            current_line = []
            
            # Usar una fuente un poco más grande para mejor legibilidad
            font_to_use = pygame.font.Font(None, 16)  # Fuente más legible
            
            for word in words:
                test_line = " ".join(current_line + [word])
                if font_to_use.size(test_line)[0] < item_rect.width - 50:  # Más espacio para el texto
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(" ".join(current_line))
            
            # Calcular la altura total del texto
            line_height = 18  # Ligeramente mayor espaciado
            text_height = len(lines) * line_height
            start_y = item_rect.y + (item_rect.height - text_height) // 2
            
            # Dibujar cada línea de texto
            for j, line in enumerate(lines):
                y_pos = start_y + j * line_height
                if y_pos < item_rect.y + item_rect.height - 10:
                    text_surface = font_to_use.render(line, True, text_color)
                    text_rect = text_surface.get_rect(x=item_rect.x + 40, y=y_pos)  # Alineado a la izquierda con margen
                    screen.blit(text_surface, text_rect)

        # Dibujar los objetivos con efectos mejorados
        for i, target in enumerate(self.targets):
            target_rect = self._get_target_rect(i)
            
            # Determinar color según estado
            if target.get("matched", False):
                bg_color = self.target_matched_color
                border_color = (40, 100, 40)
                text_color = (20, 20, 20)
                glow = True
            elif self.hover_target == i:
                bg_color = (75, 60, 100)  # Ligeramente más claro al pasar el mouse
                border_color = self.target_border
                text_color = (240, 240, 240)
                glow = True
            else:
                bg_color = self.target_bg
                border_color = self.target_border
                text_color = (220, 220, 220)
                glow = False
            
            # Efecto de resplandor para objetivos resaltados
            if glow:
                glow_surface = pygame.Surface((target_rect.width + 10, target_rect.height + 10), pygame.SRCALPHA)
                glow_color = (*border_color, 70)  # Añadir alfa
                pygame.draw.rect(glow_surface, glow_color, (0, 0, target_rect.width + 10, target_rect.height + 10), border_radius=12)
                screen.blit(glow_surface, (target_rect.x - 5, target_rect.y - 5))
            
            # Dibujar fondo con sombra
            shadow_rect = target_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, (20, 20, 30), shadow_rect, border_radius=10)
            
            # Dibujar el objetivo principal
            pygame.draw.rect(screen, bg_color, target_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, target_rect, 2, border_radius=10)
            
            # Dibujar un ícono decorativo (rombo para objetivos)
            icon_x = target_rect.x + 25
            icon_y = target_rect.centery
            icon_size = 8
            
            icon_points = [
                (icon_x, icon_y - icon_size),
                (icon_x + icon_size, icon_y),
                (icon_x, icon_y + icon_size),
                (icon_x - icon_size, icon_y)
            ]
            
            if target.get("matched", False):
                pygame.draw.polygon(screen, (220, 220, 220), icon_points)
                pygame.draw.polygon(screen, border_color, icon_points, 1)
            else:
                pygame.draw.polygon(screen, (180, 180, 180), icon_points)
                pygame.draw.polygon(screen, border_color, icon_points, 1)
            
            # Dibujar el texto centrado
            font_target = pygame.font.Font(None, 18)  # Fuente más legible
            target_text = font_target.render(target["name"], True, text_color)
            text_rect = target_text.get_rect(center=(target_rect.centerx + 10, target_rect.centery))  # Ligeramente desplazado para no solapar el ícono
            screen.blit(target_text, text_rect)

        # Renderizar las partículas (para efectos de éxito)
        if self.use_particle_effects:
            for particle in self.particles:
                # Calcular opacidad basada en la vida restante
                alpha = 255 * (1 - particle['age'] / particle['lifetime'])
                color = (*particle['color'], int(alpha))
                
                # Dibujar partícula como círculo semi-transparente
                surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (particle['size'], particle['size']), particle['size'])
                screen.blit(surf, (particle['x'] - particle['size'], particle['y'] - particle['size']))

        # Si se está mostrando un mensaje de resultado
        if self.show_result:
            self._render_result_modal(screen)

    def _render_result_modal(self, screen):
        """Renderizar el modal de resultado con mejor estética"""
        # Crear un fondo oscurecido para destacar el modal
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Negro semitransparente
        screen.blit(overlay, (0, 0))
        
        # Configurar el modal
        modal_width = 500
        modal_height = 150
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Efecto de brillo para el modal
        for i in range(5, 0, -1):
            glow_color = (*self.result_color, 20 * i)  # Color con transparencia gradual
            glow_rect = pygame.Rect(
                modal_x - i, modal_y - i, 
                modal_width + 2 * i, modal_height + 2 * i
            )
            pygame.draw.rect(screen, glow_color, glow_rect, border_radius=15)
        
        # Dibujar el fondo del modal
        pygame.draw.rect(screen, (30, 30, 40), (modal_x, modal_y, modal_width, modal_height), border_radius=15)
        pygame.draw.rect(screen, self.result_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=15)
        
        # Renderizar título y mensaje
        if self.completed:
            title = "¡Éxito!"
            # Si está completado, mostrar botón de Aceptar para cerrar
            pygame.draw.rect(screen, (60, 60, 70), (modal_x + modal_width // 2 - 70, modal_y + modal_height - 40, 140, 35), border_radius=5)
            pygame.draw.rect(screen, self.result_color, (modal_x + modal_width // 2 - 70, modal_y + modal_height - 40, 140, 35), 2, border_radius=5)
            close_text = self.font_small.render("ACEPTAR", True, WHITE)
            screen.blit(close_text, close_text.get_rect(center=(modal_x + modal_width // 2, modal_y + modal_height - 23)))
        elif self.failed:
            title = "¡Game Over!"
            # Si ha fallado, no mostrar botón ya que pasará al estado Game Over
        else:
            title = "Error"
            # Si es error pero no ha fallado, mostrar botón para continuar
            pygame.draw.rect(screen, (60, 60, 70), (WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, 80, 30), border_radius=5)
            pygame.draw.rect(screen, self.result_color, (WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, 80, 30), 2, border_radius=5)
            ok_text = self.font_small.render("OK", True, WHITE)
            screen.blit(ok_text, ok_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 45)))
        
        # Renderizar título con efecto de sombra
        title_shadow = self.font_medium.render(title, True, BLACK)
        title_text = self.font_medium.render(title, True, self.result_color)
        screen.blit(title_shadow, title_shadow.get_rect(center=(modal_x + modal_width // 2 + 2, modal_y + 28 + 2)))
        screen.blit(title_text, title_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 28)))
        
        # Renderizar mensaje (con wrapeo de texto)
        wrapped_lines = self._wrap_text(self.result_message, self.font_small, modal_width - 40)
        for i, line in enumerate(wrapped_lines):
            line_text = self.font_small.render(line, True, WHITE)
            screen.blit(line_text, line_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 65 + i * 22)))

    def _wrap_text(self, text, font, max_width):
        """Divide un texto en líneas para ajustarse al ancho máximo."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Si una palabra es demasiado larga, añadirla de todas formas
                    lines.append(word)
                    
        if current_line:
            lines.append(" ".join(current_line))
            
        return lines

    def _get_item_rect(self, index):
        """Obtener el rectángulo para un elemento"""
        # Aumentar el tamaño del panel principal en un 20%
        panel_width = 600  # Antes 500
        panel_height = 480  # Antes 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2

        # Aumentar el ancho y la altura de los elementos en un 20%
        item_width = 288  # Antes 240 (240 * 1.2 = 288)
        item_height = 96  # Antes 80 (80 * 1.2 = 96)

        # Ajustar la posición para mantener el centrado
        item_x = panel_x + 30  # Ajustado para centrar mejor

        # Distribuir los elementos verticalmente con más espacio
        spacing = 30  # Antes 25
        item_y = panel_y + 90 + index * (item_height + spacing)

        return pygame.Rect(item_x, item_y, item_width, item_height)

    def _get_target_rect(self, index):
        """Obtener el rectángulo para un objetivo"""
        # Usar el mismo panel aumentado en un 20%
        panel_width = 600  # Antes 500
        panel_height = 480  # Antes 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2

        # Aumentar el ancho y la altura de los objetivos en un 20%
        target_width = 216  # Antes 180 (180 * 1.2 = 216)
        target_height = 48  # Antes 40 (40 * 1.2 = 48)

        # Ajustar la posición para mantener el centrado
        target_x = panel_x + panel_width - target_width - 30  # Ajustado para centrar mejor

        # Alinear los objetivos con los elementos
        item_height = 96  # Debe coincidir con el nuevo item_height
        spacing = 30  # Debe coincidir con el nuevo spacing
        target_y = panel_y + 115 + index * (item_height + spacing)

        return pygame.Rect(target_x, target_y, target_width, target_height)


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

        # Cargar la imagen de la misión
        mission_path = os.path.join("img", "MISION.png")
        try:
            mission_img = pygame.image.load(mission_path).convert_alpha()
            self.mission_img = pygame.transform.scale(mission_img, (120, 120))  # Tamaño más grande para mejor visibilidad
        except Exception as e:
            print(f"Error loading mission image: {e}")
            self.mission_img = None

        # Crear la actividad educativa
        self.activity = PMBOKActivity()

        # Área interactiva para la misión
        self.mission_rect = pygame.Rect(2, 378, 190-2, 562-378)
        self.player_near_mission = False

        # Variables para la animación de flotación
        self.animation_time = 0
        self.float_amplitude = 10  # Amplitud de la flotación (en píxeles)
        self.float_speed = 0.05    # Velocidad de la flotación
        self.rotation_amplitude = 5  # Amplitud de la rotación (en grados)
        self.glow_value = 0        # Valor para el efecto de brillo

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición
        self.player_near_mission = False  # Inicializar variable para el área de la misión

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

    def check_mission_area(self, player_rect):
        """Check if player is near the mission area"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Convertir las coordenadas relativas a absolutas para el área de la misión
        mission_rect_abs = pygame.Rect(
            self.mission_rect.x + self.bg_x_offset,
            self.mission_rect.y + self.bg_y_offset,
            self.mission_rect.width,
            self.mission_rect.height
        )

        # Crear un rectángulo más grande para detectar proximidad
        proximity_rect = mission_rect_abs.inflate(100, 100)  # 100 píxeles más grande en cada dirección para facilitar la interacción

        # Verificar si el jugador está cerca del área de la misión
        near_mission = proximity_rect.colliderect(player_rect)

        # Dibujar el área de la misión en modo debug
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 255), mission_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 200, 200), proximity_rect, 1)
            if near_mission:
                pygame.draw.rect(pygame.display.get_surface(), (255, 255, 0), proximity_rect, 1)
                print("Jugador cerca del área de la misión")

        # Actualizar el estado
        self.player_near_mission = near_mission

        return near_mission

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Dibujar la imagen de la misión con animación
        if self.mission_img:
            # Calcular la posición base para centrar la imagen en el rectángulo
            base_x = self.mission_rect.x + self.bg_x_offset + (self.mission_rect.width - self.mission_img.get_width()) // 2
            base_y = self.mission_rect.y + self.bg_y_offset + (self.mission_rect.height - self.mission_img.get_height()) // 2

            # Aplicar efecto de flotación usando funciones sinusoidales
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude

            # Posición final con efecto de flotación
            mission_pos = (base_x, base_y + float_offset_y)

            # Aplicar efecto de brillo si el jugador está cerca
            if self.player_near_mission:
                # Crear una superficie para el halo
                glow_width = self.mission_img.get_width() + 20
                glow_height = self.mission_img.get_height() + 20
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

                # Dibujar un halo alrededor de la imagen
                glow_color = (255, 255, 100, int(100 * self.glow_value))  # Amarillo con transparencia variable
                pygame.draw.circle(
                    glow_surface,
                    glow_color,
                    (glow_width // 2, glow_height // 2),
                    min(glow_width, glow_height) // 2 - 5
                )

                # Dibujar el halo
                glow_pos = (mission_pos[0] - 10, mission_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            # Dibujar la imagen principal
            screen.blit(self.mission_img, mission_pos)

            # Efecto simple de partículas si el jugador está cerca
            if self.player_near_mission and random.random() < 0.03:  # 3% de probabilidad por frame
                # Dibujar pequeños destellos alrededor de la imagen
                for _ in range(2):  # Crear solo 2 partículas a la vez para evitar sobrecarga
                    # Posición aleatoria alrededor de la imagen
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-20, 20)
                    particle_pos = (
                        mission_pos[0] + self.mission_img.get_width() // 2 + offset_x,
                        mission_pos[1] + self.mission_img.get_height() // 2 + offset_y
                    )
                    # Color aleatorio para el destello
                    particle_color = (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    )
                    # Dibujar un pequeño círculo como destello
                    pygame.draw.circle(screen, particle_color, particle_pos, random.randint(1, 3))

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

    def update(self):
        """Update room state"""
        super().update()  # Llamar al método update de la clase padre

        # Actualizar el tiempo de animación
        self.animation_time += 1

        # Actualizar el valor de brillo (oscila entre 0 y 1)
        self.glow_value = (math.sin(self.animation_time * 0.05) + 1) / 2

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        # Si la actividad está activa, manejar sus eventos
        if self.activity.active:
            self.activity.handle_event(event)
            return

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
            elif event.key == pygame.K_SPACE:  # Tecla espacio para interactuar con la misión
                # Verificar si el jugador está cerca del área de la misión
                if self.player_near_mission:
                    # Activar la actividad educativa
                    self.activity.activate()
                    print("Actividad educativa activada")


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

        # Cargar la imagen de la misión
        mission_path = os.path.join("img", "MISION.png")
        try:
            mission_img = pygame.image.load(mission_path).convert_alpha()
            self.mission_img = pygame.transform.scale(mission_img, (120, 120))  # Tamaño más grande para mejor visibilidad
        except Exception as e:
            print(f"Error loading mission image: {e}")
            self.mission_img = None

        # Crear la actividad educativa (usar la nueva actividad de planificación)
        from activities.pmbok_planning_activity import PMBOKPlanningActivity
        self.activity = PMBOKPlanningActivity()

        # Área interactiva para la misión (usando el nuevo rectángulo especificado)
        self.mission_rect = pygame.Rect(434, 175, 540-434, 337-175)
        self.player_near_mission = False

        # Variables para la animación de flotación
        self.animation_time = 0
        self.float_amplitude = 10  # Amplitud de la flotación (en píxeles)
        self.float_speed = 0.05    # Velocidad de la flotación
        self.rotation_amplitude = 5  # Amplitud de la rotación (en grados)
        self.glow_value = 0        # Valor para el efecto de brillo

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición
        self.player_near_mission = False  # Inicializar variable para el área de la misión

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
        
    def check_mission_area(self, player_rect):
        """Check if player is near the mission area"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Convertir las coordenadas relativas a absolutas para el área de la misión
        mission_rect_abs = pygame.Rect(
            self.mission_rect.x + self.bg_x_offset,
            self.mission_rect.y + self.bg_y_offset,
            self.mission_rect.width,
            self.mission_rect.height
        )

        # Crear un rectángulo más grande para detectar proximidad
        proximity_rect = mission_rect_abs.inflate(100, 100)  # 100 píxeles más grande en cada dirección para facilitar la interacción

        # Verificar si el jugador está cerca del área de la misión
        near_mission = proximity_rect.colliderect(player_rect)

        # Dibujar el área de la misión en modo debug
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 255), mission_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 200, 200), proximity_rect, 1)
            if near_mission:
                pygame.draw.rect(pygame.display.get_surface(), (255, 255, 0), proximity_rect, 1)
                print("Jugador cerca del área de la misión")

        # Actualizar el estado
        self.player_near_mission = near_mission

        return near_mission

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Dibujar la imagen de la misión con animación
        if self.mission_img:
            # Calcular la posición base para centrar la imagen en el rectángulo
            base_x = self.mission_rect.x + self.bg_x_offset + (self.mission_rect.width - self.mission_img.get_width()) // 2
            base_y = self.mission_rect.y + self.bg_y_offset + (self.mission_rect.height - self.mission_img.get_height()) // 2

            # Aplicar efecto de flotación usando funciones sinusoidales
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude

            # Posición final con efecto de flotación
            mission_pos = (base_x, base_y + float_offset_y)

            # Aplicar efecto de brillo si el jugador está cerca
            if self.player_near_mission:
                # Crear una superficie para el halo
                glow_width = self.mission_img.get_width() + 20
                glow_height = self.mission_img.get_height() + 20
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

                # Dibujar un halo alrededor de la imagen
                glow_color = (255, 255, 100, int(100 * self.glow_value))  # Amarillo con transparencia variable
                pygame.draw.circle(
                    glow_surface,
                    glow_color,
                    (glow_width // 2, glow_height // 2),
                    min(glow_width, glow_height) // 2 - 5
                )

                # Dibujar el halo
                glow_pos = (mission_pos[0] - 10, mission_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            # Dibujar la imagen principal
            screen.blit(self.mission_img, mission_pos)

            # Efecto simple de partículas si el jugador está cerca
            if self.player_near_mission and random.random() < 0.03:  # 3% de probabilidad por frame
                # Dibujar pequeños destellos alrededor de la imagen
                for _ in range(2):  # Crear solo 2 partículas a la vez para evitar sobrecarga
                    # Posición aleatoria alrededor de la imagen
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-20, 20)
                    particle_pos = (
                        mission_pos[0] + self.mission_img.get_width() // 2 + offset_x,
                        mission_pos[1] + self.mission_img.get_height() // 2 + offset_y
                    )
                    # Color aleatorio para el destello
                    particle_color = (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    )
                    # Dibujar un pequeño círculo como destello
                    pygame.draw.circle(screen, particle_color, particle_pos, random.randint(1, 3))

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

    def update(self):
        """Update room state"""
        super().update()  # Llamar al método update de la clase padre

        # Actualizar el tiempo de animación
        self.animation_time += 1

        # Actualizar el valor de brillo (oscila entre 0 y 1)
        self.glow_value = (math.sin(self.animation_time * 0.05) + 1) / 2

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        # Si la actividad está activa, manejar sus eventos
        if self.activity.active:
            self.activity.handle_event(event)
            return
            
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
            elif event.key == pygame.K_SPACE:  # Tecla espacio para interactuar con la misión
                # Verificar si el jugador está cerca del área de la misión
                if self.player_near_mission:
                    # Activar la actividad educativa
                    self.activity.activate()
                    print("Actividad educativa activada")


class PMBOKExecutionRoom(Room):
    def __init__(self, content):
        super().__init__("PMBOK: Execution Phase", "Aprende sobre la ejecución del proyecto", BLUE, "blue")
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

        # Cargar la imagen de la misión
        mission_path = os.path.join("img", "MISION.png")
        try:
            mission_img = pygame.image.load(mission_path).convert_alpha()
            self.mission_img = pygame.transform.scale(mission_img, (120, 120))  # Tamaño más grande para mejor visibilidad
        except Exception as e:
            print(f"Error loading mission image: {e}")
            self.mission_img = None

        # Crear la actividad educativa para la sala de ejecución
        from activities.pmbok_execution_activity import PMBOKExecutionActivity
        self.activity = PMBOKExecutionActivity()

        # Área interactiva para la misión - Usa las coordenadas definidas anteriormente
        self.mission_rect = pygame.Rect(451, 342, 553-451, 454-342)
        self.player_near_mission = False

        # Variables para la animación de flotación
        self.animation_time = 0
        self.float_amplitude = 10  # Amplitud de la flotación (en píxeles)
        self.float_speed = 0.05
        self.rotation_amplitude = 5  # Amplitud de la rotación (en grados)
        self.glow_value = 0        # Valor para el efecto de brillo

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición
        self.player_near_mission = False  # Inicializar variable para el área de la misión

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
        
    def check_mission_area(self, player_rect):
        """Check if player is near the mission area"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Convertir las coordenadas relativas a absolutas para el área de la misión
        mission_rect_abs = pygame.Rect(
            self.mission_rect.x + self.bg_x_offset,
            self.mission_rect.y + self.bg_y_offset,
            self.mission_rect.width,
            self.mission_rect.height
        )

        # Crear un rectángulo más grande para detectar proximidad
        proximity_rect = mission_rect_abs.inflate(100, 100)  # 100 píxeles más grande en cada dirección para facilitar la interacción

        # Verificar si el jugador está cerca del área de la misión
        near_mission = proximity_rect.colliderect(player_rect)

        # Dibujar el área de la misión en modo debug
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 255), mission_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 200, 200), proximity_rect, 1)
            if near_mission:
                pygame.draw.rect(pygame.display.get_surface(), (255, 255, 0), proximity_rect, 1)
                print("Jugador cerca del área de la misión")

        # Actualizar el estado
        self.player_near_mission = near_mission

        return near_mission

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Dibujar la imagen de la misión con animación
        if self.mission_img:
            # Calcular la posición base para centrar la imagen en el rectángulo
            base_x = self.mission_rect.x + self.bg_x_offset + (self.mission_rect.width - self.mission_img.get_width()) // 2
            base_y = self.mission_rect.y + self.bg_y_offset + (self.mission_rect.height - self.mission_img.get_height()) // 2

            # Aplicar efecto de flotación usando funciones sinusoidales
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude

            # Posición final con efecto de flotación
            mission_pos = (base_x, base_y + float_offset_y)

            # Aplicar efecto de brillo si el jugador está cerca
            if self.player_near_mission:
                # Crear una superficie para el halo
                glow_width = self.mission_img.get_width() + 20
                glow_height = self.mission_img.get_height() + 20
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

                # Dibujar un halo alrededor de la imagen
                glow_color = (255, 255, 100, int(100 * self.glow_value))  # Amarillo con transparencia variable
                pygame.draw.circle(
                    glow_surface,
                    glow_color,
                    (glow_width // 2, glow_height // 2),
                    min(glow_width, glow_height) // 2 - 5
                )

                # Dibujar el halo
                glow_pos = (mission_pos[0] - 10, mission_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            # Dibujar la imagen principal
            screen.blit(self.mission_img, mission_pos)

            # Efecto simple de partículas si el jugador está cerca
            if self.player_near_mission and random.random() < 0.03:  # 3% de probabilidad por frame
                # Dibujar pequeños destellos alrededor de la imagen
                for _ in range(2):  # Crear solo 2 partículas a la vez para evitar sobrecarga
                    # Posición aleatoria alrededor de la imagen
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-20, 20)
                    particle_pos = (
                        mission_pos[0] + self.mission_img.get_width() // 2 + offset_x,
                        mission_pos[1] + self.mission_img.get_height() // 2 + offset_y
                    )
                    # Color aleatorio para el destello
                    particle_color = (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    )
                    # Dibujar un pequeño círculo como destello
                    pygame.draw.circle(screen, particle_color, particle_pos, random.randint(1, 3))

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

    def update(self):
        """Update room state"""
        super().update()  # Llamar al método update de la clase padre

        # Actualizar el tiempo de animación
        self.animation_time += 1

        # Actualizar el valor de brillo (oscila entre 0 y 1)
        self.glow_value = (math.sin(self.animation_time * 0.05) + 1) / 2

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        # Si la actividad está activa, manejar sus eventos
        if self.activity.active:
            self.activity.handle_event(event)
            return
            
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
            elif event.key == pygame.K_SPACE:  # Tecla espacio para interactuar con la misión
                # Verificar si el jugador está cerca del área de la misión
                if self.player_near_mission:
                    # Activar la actividad educativa
                    self.activity.activate()
                    print("Actividad educativa activada")


class PMBOKClosingRoom(Room):
    """
    Sala 4 del camino PMBOK - Cierre del Proyecto.
    """
    def __init__(self, content):
        super().__init__("PMBOKClosingRoom", "Sala de Cierre del Proyecto", (50, 50, 70), theme="red")
        
        # Guardar referencia al juego (pasada en el contenido)
        self.game_instance = content.get("game_instance")
        
        # Variables específicas de la sala
        self.bg_x_offset = 0
        self.bg_y_offset = 0
        
        # Cargar el fondo
        self.background = pygame.image.load("img/sala_4_pmbok.png")
        
        # Escalar el fondo al tamaño de la ventana
        self.scaled_bg = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Rectángulos de colisión para limitar el movimiento del jugador
        self.collision_rects = []
        
        # Añadir rectángulos de colisión según sea necesario
        # Estos valores son aproximados y deberían ajustarse según la imagen real
        # Por ejemplo, para impedir que el jugador camine a través de paredes
        
        # Zona del jugador libre para moverse: centro-abajo de la pantalla
        
        # Áreas de misión (para activar actividades educativas)
        self.mission_rect = pygame.Rect(446, 310, 516-446, 472-310)  # Rectángulo exacto donde debe aparecer la misión
        self.player_near_mission = False  # Flag para detectar si el jugador está cerca
        
        # Configuración para efectos visuales
        self.animation_time = 0
        self.float_speed = 0.04  # Velocidad de flotación de elementos
        self.float_amplitude = 3  # Amplitud de flotación
        self.glow_value = 0  # Valor de brillo (0-1)
        mission_path = os.path.join("img", "MISION.png")
                
        # Cargar imagen de misión (objeto que brillará y flotará)        mission_img_path = "img/MISION.png"
        try:
            self.mission_img = pygame.image.load(mission_path)
            self.mission_img = pygame.transform.scale(self.mission_img, (64, 64))
        except:
            print(f"Error al cargar la imagen: {mission_path}")
            self.mission_img = None
        
        # Inicializar la actividad educativa para esta sala
        # Pasar la referencia al juego a la actividad
        self.activity = PMBOKClosingActivity(self.game_instance)  # Crear una instancia de la actividad
        
        # Configurar la sala
        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición
        self.player_near_mission = False  # Inicializar variable para el área de la misión

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
        
    def check_mission_area(self, player_rect):
        """Check if player is near the mission area"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Convertir las coordenadas relativas a absolutas para el área de la misión
        mission_rect_abs = pygame.Rect(
            self.mission_rect.x + self.bg_x_offset,
            self.mission_rect.y + self.bg_y_offset,
            self.mission_rect.width,
            self.mission_rect.height
        )

        # Crear un rectángulo más grande para detectar proximidad
        proximity_rect = mission_rect_abs.inflate(100, 100)  # 100 píxeles más grande en cada dirección para facilitar la interacción

        # Verificar si el jugador está cerca del área de la misión
        near_mission = proximity_rect.colliderect(player_rect)

        # Dibujar el área de la misión en modo debug
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 255), mission_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 200, 200), proximity_rect, 1)
            if near_mission:
                pygame.draw.rect(pygame.display.get_surface(), (255, 255, 0), proximity_rect, 1)
                print("Jugador cerca del área de la misión")

        # Actualizar el estado
        self.player_near_mission = near_mission

        return near_mission

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Dibujar la imagen de la misión con animación
        if self.mission_img:
            # Calcular la posición base para centrar la imagen en el rectángulo
            base_x = self.mission_rect.x + self.bg_x_offset + (self.mission_rect.width - 128) // 2  # Tamaño de imagen 128x128
            base_y = self.mission_rect.y + self.bg_y_offset + (self.mission_rect.height - 128) // 2

            # Aplicar efecto de flotación usando funciones sinusoidales
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude

            # Posición final con efecto de flotación
            mission_pos = (base_x, base_y + float_offset_y)

            # Dibujar el rectángulo de la misión con borde muy visible
            mission_rect_abs = pygame.Rect(
                self.mission_rect.x + self.bg_x_offset,
                self.mission_rect.y + self.bg_y_offset,
                self.mission_rect.width,
                self.mission_rect.height
            )
            pygame.draw.rect(screen, (255, 0, 0), mission_rect_abs, 3)

            # Aplicar efecto de brillo si el jugador está cerca
            if self.player_near_mission:
                # Crear una superficie para el halo
                glow_width = 128 + 40  # Tamaño aumentado
                glow_height = 128 + 40
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

                # Dibujar un halo alrededor de la imagen
                glow_color = (255, 255, 100, int(150 * self.glow_value))  # Brillo aumentado
                pygame.draw.circle(
                    glow_surface,
                    glow_color,
                    (glow_width // 2, glow_height // 2),
                    min(glow_width, glow_height) // 2 - 5
                )

                # Dibujar el halo
                glow_pos = (mission_pos[0] - 20, mission_pos[1] - 20)
                screen.blit(glow_surface, glow_pos)

            # Dibujar la imagen principal con tamaño aumentado
            mission_img_large = pygame.transform.scale(self.mission_img, (128, 128))  # Tamaño doble
            screen.blit(mission_img_large, mission_pos)

            # Efecto simple de partículas si el jugador está cerca
            if self.player_near_mission and random.random() < 0.03:  # 3% de probabilidad por frame
                for _ in range(4):  # Más partículas
                    offset_x = random.randint(-30, 30)
                    offset_y = random.randint(-30, 30)
                    particle_pos = (
                        mission_pos[0] + 64 + offset_x,  # centro de la imagen 128x128
                        mission_pos[1] + 64 + offset_y
                    )
                    particle_color = (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(100, 200)
                    )
                    pygame.draw.circle(screen, particle_color, particle_pos, random.randint(2, 5))  # Partículas más grandes

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

    def update(self):
        """Update room state"""
        super().update()  # Llamar al método update de la clase padre

        # Actualizar el tiempo de animación
        self.animation_time += 1

        # Actualizar el valor de brillo (oscila entre 0 y 1)
        self.glow_value = (math.sin(self.animation_time * 0.05) + 1) / 2

        if hasattr(self, "player"):
            self.check_info_area(self.player.rect)

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True
        

    def handle_event(self, event):
        # Si la actividad está activa, manejar sus eventos
        if self.activity.active:
            self.activity.handle_event(event)
            return
       

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
            elif event.key == pygame.K_SPACE:  # Tecla espacio para interactuar con la misión
                # Verificar si el jugador está cerca del área de la misión
                if self.player_near_mission:
                    # Activar la actividad educativa
                    self.activity.activate()
                    print("Actividad educativa activada")

                    

class ScrumPrioritizationActivity:
    def __init__(self, game_instance):
        self.game = game_instance
        self.active = False
        self.font = pygame.font.Font(None, 22)
        self.result_message = ""
        self.result_color = GREEN
        self.show_result = False
        self.completed = False
        self.feedback_active = False
        self.feedback_active = False
        self.feedback_button_rect = None

        # Historias de usuario con prioridades (1 = más alta)
        self.items = [
            {"id": 1, "text": "Guardar progreso automáticamente", "priority": 3, "rect": None, "dragging": False},
            {"id": 2, "text": "Ver un tutorial inicial", "priority": 4, "rect": None, "dragging": False},
            {"id": 3, "text": "Errores visuales animados", "priority": 1, "rect": None, "dragging": False},
            {"id": 4, "text": "Tabla de puntuaciones", "priority": 2, "rect": None, "dragging": False},
            {"id": 5, "text": "Pausar partida", "priority": 5, "rect": None, "dragging": False},
        ]
        self.items = [
            {
                "id": "H5",
                "title": "Diseño del mapa y dinámicas de juego total",
                "priority": 4,
                "description": "Como paciente, quiero seleccionar especialidad, médico y fecha para agendar una cita desde la web sin llamar por teléfono.",
                "rect": None,
                "dragging": False
            },
            {
                "id": "H4",
                "title": "Diseño del mapa y dinámicas de juego total",
                "priority": 2,
                "description": "Como paciente, quiero recibir un correo si mi cita cambia, para estar informado en todo momento.",
                "rect": None,
                "dragging": False
            },
            {
                "id": "H1",
                "title": "Diseño del mapa y dinámicas de juego total",
                "priority": 5,
                "description": "Como paciente, quiero ver solo los médicos que atienden mi padecimiento, para elegir más fácilmente.",
                "rect": None,
                "dragging": False
            },
            {
                "id": "H2",
                "title": "Diseño del mapa y dinámicas de juego total",
                "priority": 1,
                "description": "Como paciente, quiero revisar todas las citas que he tenido, para llevar un mejor seguimiento de mi salud.",
                "rect": None,
                "dragging": False
            },
            {
                "id": "H3",
                "title": "Diseño del mapa y dinámicas de juego total",
                "priority": 3,
                "description": "Como administrador, quiero cambiar la paleta de colores del sitio para que combine con el logotipo del consultorio.",
                "rect": None,
                "dragging": False
            },
            
        ]

        # Posición inicial de las tarjetas
        self.panel_top = 90
        self.panel_left = WINDOW_WIDTH // 2 - 200
        #self.item_height = 160
        self.spacing = 5
        self.drag_offset_y = 0

        self._position_items()

    def _position_items(self):
        card_width = 550
        x = (WINDOW_WIDTH - card_width) // 2  # 👈 Centrado horizontal
        y = self.panel_top
        font_text = pygame.font.Font(None, 16)

        for item in self.items:
           # Calcular líneas necesarias antes del render
            lines = self._wrap_text(item["description"], font_text, card_width - 20)
            cabecera_altura = 65
            altura_por_linea = 18
            height = cabecera_altura + len(lines) * altura_por_linea

            # Asignar el rect con altura correcta
            item["rect"] = pygame.Rect(x, y, card_width, height)

            # Avanzar para la siguiente tarjeta (espaciado uniforme)
            y += height + self.spacing  # ← aquí controlas el espacio entre tarjetas


    def activate(self):
        self.active = True
        self.completed = False
        self.show_result = False
        self._position_items()

    def deactivate(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return
        
        if not self.show_result and not self.feedback_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, 'manual_close_rect') and self.manual_close_rect.collidepoint(event.pos):
                    self.deactivate()
                    return

        
        if self.show_result and hasattr(self, 'result_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.result_button_rect.collidepoint(event.pos):
                    self.show_result = False
                    self.deactivate()
                    return
        
        if self.feedback_active and self.feedback_button_rect:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.feedback_button_rect.collidepoint(event.pos):
                    self.feedback_active = False
                    self.feedback_button_rect = None
                    self.game.state = STATE_GAME_OVER  # 👈 Llama directamente el Game Over
                    return


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for item in self.items:
                    if item["rect"].collidepoint(event.pos):
                        item["dragging"] = True
                        self.drag_offset_y = event.pos[1] - item["rect"].y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for item in self.items:
                    item["dragging"] = False
                self._reorder_items()

        elif event.type == pygame.MOUSEMOTION:
            for item in self.items:
                if item["dragging"]:
                    item["rect"].y = event.pos[1] - self.drag_offset_y

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._verificar_orden()

    def _reorder_items(self):
        self.items.sort(key=lambda item: item["rect"].y)
        self._position_items()

    def _verificar_orden(self):
        orden_actual = [item["id"] for item in self.items]
        orden_correcto = sorted(self.items, key=lambda x: x["priority"])
        if orden_actual == [item["id"] for item in orden_correcto]:
            self.completed = True
            self.result_message = "¡Orden correcto! Has priorizado correctamente las historias de usuario."
            self.result_color = GREEN
            self.show_result = True
        else:
            self.result_message = (
                "Historias de usuario críticas para el objetivo principal del Sprint deben ir primero."
                "En este caso, el objetivo es lanzar una versión funcional que permita agendar citas. Por eso, la funcionalidad de agendar una cita (H1) es la más importante. Sin eso, el sistema no cumple su propósito."

                "Las mejoras de experiencia o conveniencia tienen prioridad media."
                "Filtrar doctores (H3) y notificar cambios (H2) son útiles, pero no indispensables para una primera versión funcional. Van después de lo esencial."

                "Funcionalidades de consulta histórica o visuales suelen tener baja prioridad al inicio."
                "El historial (H4) y la personalización visual (H5) no bloquean el uso básico del sistema. Pueden agregarse en iteraciones posteriores."

                "“Al priorizar, pregúntate: ¿Qué pasa si esta historia no se implementa? Si la respuesta es que el usuario no podrá usar el producto, entonces es prioridad alta."
            )
            self.result_color = RED
            self.feedback_active = True  # Mostrar el recuadro de error
            

    def render(self, screen):
        if not self.active:
            return

        panel_width = 580
        panel_padding = 30  # margen interno del panel

        # Calcular altura total de las tarjetas
        total_height = sum(item["rect"].height for item in self.items) + self.spacing * (len(self.items) - 1)

        # Posición centrada y alto dinámico
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = self.panel_top - panel_padding
        panel_height = total_height + 2 * panel_padding

        # Panel tipo pizarrón (verde tiza)
        panel_color = (30, 60, 30)  # Verde oscuro pizarrón
        border_color = (220, 220, 220)  # Borde blanco tipo tiza

        pygame.draw.rect(screen, panel_color, (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(screen, border_color, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=15)
        

        title_surface = self.font.render("Ordena las historias de usuario por prioridad", True, WHITE)
        title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + 10))  # Y aquí va el ajuste vertical
        screen.blit(title_surface, title_rect)



        # Dibujar las tarjetas
        for item in self.items:

            font_text = pygame.font.Font(None, 16)
            # Ajustar la altura según cuántas líneas requiere la descripción
            lines = self._wrap_text(item["description"], font_text, item["rect"].width - 20)
            # Estimar altura: cabecera fija + líneas de descripción
            cabecera_altura = 60
            altura_por_linea = 18
            #item["rect"].height = cabecera_altura + len(lines) * altura_por_linea

            # Fondo de ficha
            card_color = (245, 240, 220)
            border_color = (100, 80, 60)
            text_color = (40, 40, 40)

            # Dibujar fondo y borde
            pygame.draw.rect(screen, card_color, item["rect"], border_radius=6)
            pygame.draw.rect(screen, border_color, item["rect"], 2, border_radius=6)

            # Fuente para texto
            font_label = pygame.font.Font(None, 18)
            font_bold = pygame.font.Font(None, 16)
            font_bold.set_bold(True)
            

            x = item["rect"].x + 10
            y = item["rect"].y + 8

            # Línea superior: ID, Título, Prioridad
            id_text = font_bold.render(f"ID {item['id']}", True, text_color)
            title_text = font_label.render(f"Título: {item['title']}", True, text_color)
            priority_text = font_bold.render(f"Prioridad: {item['priority']}", True, text_color)

            screen.blit(id_text, (x, y))
            screen.blit(title_text, (x + 100, y))
            screen.blit(priority_text, (x + 420, y))

            # Línea de separación
            pygame.draw.line(screen, border_color, (x, y + 20), (x + item["rect"].width - 20, y + 20), 1)

            # Descripción (etiqueta)
            screen.blit(font_bold.render("Descripción", True, text_color), (x, y + 30))

            # Descripción (texto largo, envuelto)
            desc_lines = self._wrap_text(item["description"], font_text, item["rect"].width - 20)
            for i, line in enumerate(desc_lines):
                screen.blit(font_text.render(line, True, text_color), (x, y + 45 + i * 15))

        # Mostrar mensaje de resultado
        if self.show_result:
            # Fondo del modal
            modal_width = 500
            modal_height = 160
            modal_x = (WINDOW_WIDTH - modal_width) // 2
            modal_y = (WINDOW_HEIGHT - modal_height) // 2

            # Fondo del modal (color crema con efecto suave)
            bg_color = (250, 245, 235)
            border_color = (140, 120, 90)

            pygame.draw.rect(screen, bg_color, (modal_x, modal_y, modal_width, modal_height), border_radius=16)
            pygame.draw.rect(screen, border_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=16)

            # Texto del mensaje centrado
            result_font = pygame.font.Font(None, 22)
            # Icono de éxito o título
            if self.completed:
                success_font = pygame.font.Font(None, 28)
                success_text = success_font.render(" ¡Éxito!", True, (20, 120, 40))
                success_rect = success_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 25))
                screen.blit(success_text, success_rect)

            # Texto envuelto para que no se desborde
            wrapped_lines = self._wrap_text(self.result_message, result_font, modal_width - 40)
            for i, line in enumerate(wrapped_lines):
                line_surface = result_font.render(line, True, self.result_color)
                line_rect = line_surface.get_rect(center=(modal_x + modal_width // 2, modal_y + 70 + i * 25))
                screen.blit(line_surface, line_rect)


            # Botón de cerrar
            btn_width = 100
            btn_height = 40
            btn_x = modal_x + (modal_width - btn_width) // 2
            btn_y = modal_y + modal_height - btn_height - 15
            self.result_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

            btn_color = (50, 120, 80)
            btn_border = (20, 60, 40)

            pygame.draw.rect(screen, btn_color, self.result_button_rect, border_radius=10)
            pygame.draw.rect(screen, btn_border, self.result_button_rect, 2, border_radius=10)

            btn_text = result_font.render("Cerrar", True, WHITE)
            btn_text_rect = btn_text.get_rect(center=self.result_button_rect.center)
            screen.blit(btn_text, btn_text_rect)


            #pygame.draw.rect(screen, (200, 80, 60), self.result_button_rect, border_radius=8)
            #pygame.draw.rect(screen, (80, 40, 30), self.result_button_rect, 2, border_radius=8)

            #btn_text = result_font.render("Cerrar", True, WHITE)
            #btn_text_rect = btn_text.get_rect(center=self.result_button_rect.center)
            #screen.blit(btn_text, btn_text_rect)
        if self.feedback_active:
            modal_width = 500
            font = pygame.font.Font(None, 20)
             # Ajustar altura dinámica según las líneas de retroalimentación
            lines = self._wrap_text(self.result_message, font, modal_width - 40)
            line_height = 25
            modal_height = 100 + len(lines) * line_height  # Aumentado de 80 a 100 para dar más espacio
            
            modal_x = (WINDOW_WIDTH - modal_width) // 2
            modal_y = (WINDOW_HEIGHT - modal_height) // 2

            pygame.draw.rect(screen, (255, 240, 240), (modal_x, modal_y, modal_width, modal_height), border_radius=12)
            pygame.draw.rect(screen, (180, 40, 40), (modal_x, modal_y, modal_width, modal_height), 3, border_radius=12)

            
            lines = self._wrap_text(self.result_message, font, modal_width - 40)
            for i, line in enumerate(lines):
                text_surf = font.render(line, True, (80, 20, 20))
                text_rect = text_surf.get_rect(center=(modal_x + modal_width // 2, modal_y + 40 + i * 25))
                screen.blit(text_surf, text_rect)

            # Botón de cerrar - Ahora más abajo
            btn_width = 100
            btn_height = 35
            btn_x = modal_x + (modal_width - btn_width) // 2
            btn_y = modal_y + modal_height - btn_height - 20  # Aumentado de 10 a 20 para bajar más el botón
            self.feedback_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

            pygame.draw.rect(screen, (200, 80, 60), self.feedback_button_rect, border_radius=10)
            pygame.draw.rect(screen, (120, 40, 30), self.feedback_button_rect, 2, border_radius=10)

            btn_text = font.render("Cerrar", True, WHITE)
            btn_text_rect = btn_text.get_rect(center=self.feedback_button_rect.center)
            screen.blit(btn_text, btn_text_rect)
        # Mostrar botón de cerrar solo si no se está mostrando feedback ni resultado
        if not self.show_result and not self.feedback_active:
            close_btn_width = 90
            close_btn_height = 30
            close_btn_x = panel_x + panel_width - 100
            close_btn_y = panel_y + 1

            self.manual_close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_width, close_btn_height)

            pygame.draw.rect(screen, (100, 100, 100), self.manual_close_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, self.manual_close_rect, 2, border_radius=10)

            close_font = pygame.font.Font(None, 20)
            close_text = close_font.render("Cerrar", True, WHITE)
            close_text_rect = close_text.get_rect(center=self.manual_close_rect.center)
            screen.blit(close_text, close_text_rect)


    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= max_width:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines

    
# Scrum Room Classes
class ScrumRolesRoom(Room):
    def __init__(self, content, game_instance):
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
        
         # Cargar la imagen de la misión
        mission_path = os.path.join("img", "MISION.png")
        try:
            mission_img = pygame.image.load(mission_path).convert_alpha()
            self.mission_img = pygame.transform.scale(mission_img, (120, 120))  # Tamaño más grande para mejor visibilidad
        except Exception as e:
            print(f"Error loading mission image: {e}")
            self.mission_img = None

        self.game = game_instance  # ✅ AQUÍ asignas correctamente
        self.activity = ScrumPrioritizationActivity(self.game)  # ✅ y ahora sí puedes usarlo
        
        # Área interactiva para la misión
        self.mission_rect = pygame.Rect(400, 200, 188, 184)
        self.player_near_mission = False

        # Segundo objeto informativo (ajusta la posición según tu sala)
        self.info_rect = pygame.Rect(130, 395, 100, 100)
        self.player_near_info = False
        self.showing_info = False

        # Variables para la animación de flotación
        self.animation_time = 0
        self.float_amplitude = 10  # Amplitud de la flotación (en píxeles)
        self.float_speed = 0.05    # Velocidad de la flotación
        self.rotation_amplitude = 5  # Amplitud de la rotación (en grados)
        self.glow_value = 0        # Valor para el efecto de brillo

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición
        self.player_near_mission = False  # Inicializar variable para el área de la misión


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
    def check_mission_area(self, player_rect):
        """Check if player is near the mission area"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Convertir las coordenadas relativas a absolutas para el área de la misión
        mission_rect_abs = pygame.Rect(
            self.mission_rect.x + self.bg_x_offset,
            self.mission_rect.y + self.bg_y_offset,
            self.mission_rect.width,
            self.mission_rect.height
        )

        # Crear un rectángulo más grande para detectar proximidad
        proximity_rect = mission_rect_abs.inflate(20, 20)  # 100 píxeles más grande en cada dirección para facilitar la interacción

        # Verificar si el jugador está cerca del área de la misión
        near_mission = proximity_rect.colliderect(player_rect)

        # Dibujar el área de la misión en modo debug
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 255), mission_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 200, 200), proximity_rect, 1)
            if near_mission:
                pygame.draw.rect(pygame.display.get_surface(), (255, 255, 0), proximity_rect, 1)
                print("Jugador cerca del área de la misión")

        # Actualizar el estado
        self.player_near_mission = near_mission
        #print("[DEBUG] check_mission_area se llamó")

        return near_mission
    
    
    
    def check_info_area(self, player_rect):
        """Detecta si el jugador está cerca del segundo objeto interactivo"""
        import pygame 
    
        info_rect_abs = pygame.Rect(
            self.info_rect.x + self.bg_x_offset,
            self.info_rect.y + self.bg_y_offset,
            self.info_rect.width,
            self.info_rect.height
        )
        proximity_rect = info_rect_abs.inflate(130, 60)

        self.player_near_info = proximity_rect.colliderect(player_rect)

        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 100, 255), info_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 80, 200), proximity_rect, 1)
            if self.player_near_info:
                print("Jugador cerca del objeto informativo")

        return self.player_near_info
    
    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= max_width:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines
    
    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))

        # Dibujar la imagen de la misión con animación
        if self.mission_img:
            # Calcular la posición base para centrar la imagen en el rectángulo
            base_x = self.mission_rect.x + self.bg_x_offset + (self.mission_rect.width - self.mission_img.get_width()) // 2
            base_y = self.mission_rect.y + self.bg_y_offset + (self.mission_rect.height - self.mission_img.get_height()) // 2

            # Aplicar efecto de flotación usando funciones sinusoidales
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude

            # Posición final con efecto de flotación
            mission_pos = (base_x, base_y + float_offset_y)

            # Aplicar efecto de brillo si el jugador está cerca
            if self.player_near_mission:
                # Crear una superficie para el halo
                glow_width = self.mission_img.get_width() + 60
                glow_height = self.mission_img.get_height() + 30
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

                # Dibujar un halo alrededor de la imagen
                glow_color = (255, 255, 100, int(100 * self.glow_value))  # Amarillo con transparencia variable
                halo_rect = pygame.Rect(0, 0, glow_width, glow_height)
                halo_rect.inflate_ip(1, -20)  # Más ancho, menos alto

                pygame.draw.ellipse(
                    glow_surface,
                    glow_color,
                    halo_rect
                )

                # Dibujar el halo
                glow_pos = (mission_pos[0] - 30, mission_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            # Dibujar la imagen principal
            #screen.blit(self.mission_img, mission_pos)

            # Efecto simple de partículas si el jugador está cerca
            if self.player_near_mission and random.random() < 0.03:  # 3% de probabilidad por frame
                # Dibujar pequeños destellos alrededor de la imagen
                for _ in range(2):  # Crear solo 2 partículas a la vez para evitar sobrecarga
                    # Posición aleatoria alrededor de la imagen
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-20, 20)
                    particle_pos = (
                        mission_pos[0] + self.mission_img.get_width() // 2 + offset_x,
                        mission_pos[1] + self.mission_img.get_height() // 2 + offset_y
                    )
                    # Color aleatorio para el destello
                    particle_color = (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    )
                    # Dibujar un pequeño círculo como destello
                    pygame.draw.circle(screen, particle_color, particle_pos, random.randint(1, 3))

                    # Solo dibuja los rectángulos de colisión si estamos en modo debug

        if self.mission_img:
            # Imagen flotante para el segundo objeto
            base_x = self.info_rect.x + self.bg_x_offset + (self.info_rect.width - self.mission_img.get_width()) // 2
            base_y = self.info_rect.y + self.bg_y_offset + (self.info_rect.height - self.mission_img.get_height()) // 2
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude
            info_pos = (base_x, base_y + float_offset_y)

            if self.player_near_info:
                glow_width = self.mission_img.get_width() + 20
                glow_height = self.mission_img.get_height() + 20
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                glow_color = (120, 220, 255, int(100 * self.glow_value))  # Azul claro
                pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect())
                glow_pos = (info_pos[0] - 10, info_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            #screen.blit(self.mission_img, info_pos)

        
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
        
        if self.showing_info:
            modal_width = 500
            modal_height = 200
            modal_x = (WINDOW_WIDTH - modal_width) // 2
            modal_y = (WINDOW_HEIGHT - modal_height) // 2

            pygame.draw.rect(screen, (240, 250, 255), (modal_x, modal_y, modal_width, modal_height), border_radius=12)
            pygame.draw.rect(screen, (30, 100, 160), (modal_x, modal_y, modal_width, modal_height), 3, border_radius=12)

            font = pygame.font.Font(None, 22)
            # Texto largo que se adapta al ancho
            info_text = (
                "¡Hola! Soy el Product Owner del proyecto 'DocOnline', una plataforma web para reservar citas médicas. Nuestro objetivo es lanzar una versión mínima funcional lo antes posible para que los pacientes puedan agendar y consultar sus citas desde casa. Todo lo que no afecte directamente esta experiencia puede esperar."
            )

            # Usa el método de envoltura de texto ya existente
            wrapped_info = self._wrap_text(info_text, font, modal_width - 40)
            for i, line in enumerate(wrapped_info):
                text_surf = font.render(line, True, (20, 40, 60))
                text_rect = text_surf.get_rect(center=(modal_x + modal_width // 2, modal_y + 40 + i * 25))
                screen.blit(text_surf, text_rect)

            self.info_close_button = pygame.Rect(modal_x + modal_width - 110, modal_y + modal_height - 50, 90, 30)
            pygame.draw.rect(screen, (30, 100, 160), self.info_close_button, border_radius=8)
            screen.blit(font.render("Cerrar", True, WHITE), self.info_close_button.move(20, 5))
    


    
    def update(self):
        """Update room state"""
        super().update()  # Llamar al método update de la clase padre

        # Actualizar el tiempo de animación
        self.animation_time += 1

        # Actualizar el valor de brillo (oscila entre 0 y 1)
        self.glow_value = (math.sin(self.animation_time * 0.05) + 1) / 2

        if hasattr(self, "player"):
            self.check_info_area(self.player.rect)

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True
        

    def handle_event(self, event):
        # Si la actividad está activa, manejar sus eventos
        if self.activity.active:
            self.activity.handle_event(event)
            return
        
        if self.showing_info and hasattr(self, "info_close_button"):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.info_close_button.collidepoint(event.pos):
                    self.showing_info = False


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
            elif event.key == pygame.K_SPACE:  # Tecla espacio para interactuar con la misión
                # Verificar si el jugador está cerca del área de la misión
                if self.player_near_mission:
                    # Activar la actividad educativa
                    self.activity.activate()
                    print("Actividad educativa activada")
                elif self.player_near_info:
                    self.showing_info = True
                    

class ScrumSala2:
    def __init__(self, game_instance):
        self.game = game_instance
        self.active = False
        self.font = pygame.font.Font(None, 22)
        COLUMN_WIDTH = 195
        COLUMN_SPACING = 2
        TOP_MARGIN = 120
        LEFT_MARGIN = (601 - (3 * COLUMN_WIDTH + 2 * COLUMN_SPACING)) // 2

        self.column_positions = {
            "Por hacer": LEFT_MARGIN,
            "En progreso": LEFT_MARGIN + COLUMN_WIDTH + COLUMN_SPACING,
            "Hecho": LEFT_MARGIN + 2 * (COLUMN_WIDTH + COLUMN_SPACING)
        }
        self.column_rects = {
            col: pygame.Rect(x, TOP_MARGIN, COLUMN_WIDTH, 450)
            for col, x in self.column_positions.items()
        }
        self.columns = ["Por hacer", "En progreso", "Hecho"]
        

        self.result_message = ""
        self.result_color = GREEN
        self.show_result = False
        self.feedback_active = False
        self.feedback_button_rect = None
        self.completed = False
        self.manual_close_rect = None  # botón "cerrar actividad"
        self.card_font = pygame.font.Font(None, 17)

        self.items = [
            {
                "text": "HU01 \n Diseñar logo de la app\n Como diseñador, quiero crear y entregar el logotipo de FitHomeApp para definir la identidad visual del producto.",
                "correct_column": "Hecho",
                "rect": None,
                "dragging": False
            },
            {
                "text": "HU02 \n Programar pantalla de inicio\nComo usuario, quiero ver una pantalla de bienvenida clara y funcional, para acceder fácilmente a la aplicación.",
                "correct_column": "En progreso",
                "rect": None,
                "dragging": False
            },
            {
                "text": "HU03 \n Implementar base de datos\nComo desarrollador, necesito crear la base de datos que almacene rutinas y perfiles, para que los usuarios tengan un seguimiento personalizado.",
                "correct_column": "Por hacer",
                "rect": None,
                "dragging": False
            },
            {
                "text": "HU04 \n Revisar código de funcionalidades\nComo equipo, queremos revisar el código desarrollado hasta ahora, para asegurar que cumple con los estándares del proyecto.",
                "correct_column": "Por hacer",
                "rect": None,
                "dragging": False
            },
            {
                "text": "HU05 \n Redactar documentación técnica\nComo redactora técnica, quiero documentar las funcionalidades implementadas, para que el equipo tenga claridad sobre el sistema y sus componentes.",
                "correct_column": "En progreso",
                "rect": None,
                "dragging": False
            }
        ]
        self._position_items()

    def _position_items(self):
        CARD_WIDTH = 175
        #CARD_HEIGHT = 50
        CARD_SPACING = 5
        MARGIN_Y = 140
        START_X = self.column_positions["Por hacer"] + (195 - CARD_WIDTH) // 2  # centradas dentro de la columna
        START_Y = 140  # espacio debajo del título de columna

        font = self.card_font

         # Inicializa contadores de altura por columna
        columnas_y = {
            "Por hacer": MARGIN_Y,
            "En progreso": MARGIN_Y,
            "Hecho": MARGIN_Y
        }

        for i, item in enumerate(self.items):
            # Determinar columna por índice
            if i < 2:
                columna = "Por hacer"
            elif i < 4:
                columna = "En progreso"
            else:
                columna = "Hecho"

            # Calcular altura de la tarjeta
            lines = self._wrap_text(item["text"], self.card_font, CARD_WIDTH - 20)
            line_height = self.card_font.get_height() + 6
            total_height = 10 + len(lines) * line_height + 10

            # Centrar tarjeta en la columna
            x = self.column_positions[columna] + (195 - CARD_WIDTH) // 2
            y = columnas_y[columna]

            # Asignar rect
            item["rect"] = pygame.Rect(x, y, CARD_WIDTH, total_height)

            # Actualiza el acumulado de altura para esa columna
            columnas_y[columna] += total_height + CARD_SPACING


    def activate(self):
        self.active = True
        self.show_result = False
        self.feedback_active = False
        self.completed = False
        self._position_items()

    def deactivate(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.manual_close_rect and self.manual_close_rect.collidepoint(event.pos):
                self.deactivate()
                return

        
        if self.show_result and hasattr(self, 'result_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.result_button_rect.collidepoint(event.pos):
                    self.show_result = False
                    self.deactivate()
                    return

        if self.feedback_active and self.feedback_button_rect:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.feedback_button_rect.collidepoint(event.pos):
                    self.feedback_active = False
                    self.feedback_button_rect = None
                    self.game.state = STATE_GAME_OVER
                    return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for item in self.items:
                    if item["rect"].collidepoint(event.pos):
                        item["dragging"] = True
                        self.drag_offset = (event.pos[0] - item["rect"].x, event.pos[1] - item["rect"].y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for item in self.items:
                    item["dragging"] = False

        elif event.type == pygame.MOUSEMOTION:
            for item in self.items:
                if item["dragging"]:
                    item["rect"].x = event.pos[0] - self.drag_offset[0]
                    item["rect"].y = event.pos[1] - self.drag_offset[1]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._verificar_clasificacion()

    def _verificar_clasificacion(self):
        correctas = 0
        for item in self.items:
            x = item["rect"].centerx
            assigned_column = None
            for col, rect in self.column_rects.items():
                if rect.collidepoint(x, item["rect"].centery):
                    assigned_column = col
                    break
            if assigned_column == item["correct_column"]:
                correctas += 1

        if correctas == len(self.items):
            self.completed = True
            self.result_message = "¡Correcto! Has clasificado todas las tareas correctamente."
            self.result_color = (20, 130, 40)
            self.show_result = True
        else:
            self.result_message = (
                " Parece que algunas tareas están colocadas en columnas incorrectas.\n\n"
                "Recuerda los principios del tablero Scrum:\n"
                "• Hecho: ya fue completado y aprobado.\n"
                "• En progreso: se está trabajando actualmente.\n"
                "• Por hacer: aún no se ha comenzado.\n\n"
                "El tablero Scrum es la brújula del equipo: mantenerlo actualizado ayuda a todos a saber en qué estado está el trabajo.\n"
                "Revisa el informe del Scrum Master y vuelve a intentar clasificar las tareas. "
            )
            self.result_color = (180, 40, 40)
            self.feedback_active = True

    def draw_scrum_tablero(self, screen, font):
        COLUMN_WIDTH = 195
        CARD_WIDTH = 190
        COLUMN_SPACING = 2
        TOP_MARGIN = 120
        LEFT_MARGIN = (601 - (3 * COLUMN_WIDTH + 2 * COLUMN_SPACING)) // 2
        
        # Colores suaves por columna
        column_colors = {
            "Por hacer": (180, 60, 60),
            "En progreso": (240, 180, 50),
            "Hecho": (60, 160, 90)
        }

        title_font = pygame.font.Font(None, 26)
        title_font.set_bold(True)

        for col, rect in self.column_rects.items():
            # Dibujar fondo de columna
            pygame.draw.rect(screen, (255, 255, 255), rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2)

            # Dibujar fondo redondeado del título
            title_rect = pygame.Rect(rect.x, rect.y - 30, rect.width, 30)
            pygame.draw.rect(screen, column_colors[col], title_rect, border_radius=8)

            # Dibujar texto centrado
            title_text = title_font.render(col, True, (255, 255, 255))
            title_text_rect = title_text.get_rect(center=title_rect.center)
            screen.blit(title_text, title_text_rect)

        for item in self.items:
            rect = item["rect"]
            x = rect.x
            y = rect.y
            w = rect.width
            h = rect.height

            # Sombra suave para dar volumen
            shadow_offset = 4
            pygame.draw.rect(screen, (200, 200, 200), (x + shadow_offset, y + shadow_offset, w, h), border_radius=6)

            # Fondo crema claro tipo papel
            pygame.draw.rect(screen, (252, 250, 240), rect, border_radius=6)

            # Margen rojo (como en hojas de cuaderno)
            margin_x = x + 20
            pygame.draw.line(screen, (200, 50, 50), (margin_x, y + 10), (margin_x, y + h - 10), 2)

            # Líneas horizontales tipo hoja rayada
            line_y = y + 10
            line_spacing = self.card_font.get_height() + 6
            while line_y < y + h - 10:
                pygame.draw.line(screen, (200, 200, 200), (x + 8, line_y), (x + w - 8, line_y), 1)
                line_y += line_spacing

            # Borde principal
            pygame.draw.rect(screen, (90, 80, 60), rect, 2, border_radius=6)

            # Dibujar texto encima
            text_lines = self._wrap_text(item["text"], self.card_font, w - 30)  # 30 = padding + margen rojo
            text_x = x + 28  # margen izquierdo más grande por línea roja
            text_y = y + 10

            for line in text_lines:
                rendered = self.card_font.render(line, True, (30, 30, 30))
                screen.blit(rendered, (text_x, text_y))
                text_y += rendered.get_height() + 4

    
    def render(self, screen):
        if not self.active:
            return

        font = pygame.font.Font(None, 24)
        #screen.fill((230, 230, 230)) está borrando el HUD del juego así que por eso lo comenté

        self.draw_scrum_tablero(screen, self.font)

        # Mostrar resultado si es correcto
        if self.show_result:
            self._draw_modal(screen, self.result_message, self.result_color, True)

        # Botón de cerrar actividad (superior derecha)
        close_btn_width = 90
        close_btn_height = 30
        close_btn_x = 600 - close_btn_width - 10  # Ajustado para pantalla 600x600
        close_btn_y = 60

        self.manual_close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_width, close_btn_height)

        pygame.draw.rect(screen, (100, 100, 100), self.manual_close_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.manual_close_rect, 2, border_radius=10)

        font_btn = pygame.font.Font(None, 22)
        close_text = font_btn.render("Cerrar", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=self.manual_close_rect.center)
        screen.blit(close_text, close_text_rect)

        # Mostrar retroalimentación si es incorrecto
        if self.feedback_active:
            self._draw_modal(screen, self.result_message, self.result_color, False)

    def _draw_modal(self, screen, message, color, success):
        modal_width = 500
        font = pygame.font.Font(None, 22)
        lines = self._wrap_text(message, font, modal_width - 40)
        
        # Aumentar espacio vertical para el texto
        line_spacing = 20  # Aumentado de 18 a 20
        
        # Aumentar altura del modal según el texto
        modal_height = 100 + len(lines) * line_spacing  # Aumentado de 80 a 100
        modal_x = (screen.get_width() - modal_width) // 2
        modal_y = (screen.get_height() - modal_height) // 2

        pygame.draw.rect(screen, (255, 255, 255), (modal_x, modal_y, modal_width, modal_height), border_radius=12)
        pygame.draw.rect(screen, color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=12)

        for i, line in enumerate(lines):
            text = font.render(line, True, color)
            text_rect = text.get_rect(center=(modal_x + modal_width // 2, modal_y + 40 + i * line_spacing))
            screen.blit(text, text_rect)

        # Botón - alejado del texto
        btn_width = 120
        btn_height = 35
        btn_x = modal_x + (modal_width - btn_width) // 2
        btn_y = modal_y + modal_height - btn_height - 20  # Aumentado de 50 a 20 para posicionarlo más abajo
        rect_btn = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

        pygame.draw.rect(screen, color, rect_btn, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), rect_btn, 2, border_radius=8)
        btn_text = font.render("Cerrar", True, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=rect_btn.center)
        screen.blit(btn_text, btn_text_rect)

        if success:
            self.result_button_rect = rect_btn
        else:
            self.feedback_button_rect = rect_btn

    def _wrap_text(self, text, font, max_width):
        paragraphs = text.split('\n')
        lines = []

        for paragraph in paragraphs:
            words = paragraph.split()
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Añade una línea vacía entre párrafos si había un \n explícito
            if paragraph != paragraphs[-1]:
                lines.append("")  # línea en blanco (opcional)
        return lines

    
    

class ScrumArtifactsRoom(Room):
    def __init__(self, content, game_instance):
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
        
        # Cargar la imagen de la misión
        mission_path = os.path.join("img", "MISION.png")
        try:
            mission_img = pygame.image.load(mission_path).convert_alpha()
            self.mission_img = pygame.transform.scale(mission_img, (120, 120))  # Tamaño más grande para mejor visibilidad
        except Exception as e:
            print(f"Error loading mission image: {e}")
            self.mission_img = None
        
        self.game = game_instance
        self.activity = ScrumSala2(self.game)

         # Área interactiva para la misión
        self.mission_rect = pygame.Rect(400, 80, 188, 184)
        self.player_near_mission = False

        # Segundo objeto informativo (ajusta la posición según tu sala)
        self.info_rect = pygame.Rect(50, 280, 100, 100)
        self.player_near_info = False
        self.showing_info = False

        # Variables para la animación de flotación
        self.animation_time = 0
        self.float_amplitude = 10  # Amplitud de la flotación (en píxeles)
        self.float_speed = 0.05    # Velocidad de la flotación
        self.rotation_amplitude = 5  # Amplitud de la rotación (en grados)
        self.glow_value = 0        # Valor para el efecto de brillo

        self._setup_room()

    def _setup_room(self):
        """Set up room display only"""
        self.completed = True
        self.player_in_transition_area = False  # Inicializar variable para el área de transición
        self.player_near_mission = False  # Inicializar variable para el área de la misión

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
            100,  # Ancho del área (385 - 186)
            245   # Alto del área (350 - 105)
        )
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
    
    def check_mission_area(self, player_rect):
        """Check if player is near the mission area"""
        # Importar pygame al inicio del método para evitar errores
        import pygame

        # Convertir las coordenadas relativas a absolutas para el área de la misión
        mission_rect_abs = pygame.Rect(
            self.mission_rect.x + self.bg_x_offset,
            self.mission_rect.y + self.bg_y_offset,
            self.mission_rect.width,
            self.mission_rect.height
        )
         # Crear un rectángulo más grande para detectar proximidad
        proximity_rect = mission_rect_abs.inflate(50, 50)  # 100 píxeles más grande en cada dirección para facilitar la interacción

        # Verificar si el jugador está cerca del área de la misión
        near_mission = proximity_rect.colliderect(player_rect)

        # Dibujar el área de la misión en modo debug
        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 255, 255), mission_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 200, 200), proximity_rect, 1)
            if near_mission:
                pygame.draw.rect(pygame.display.get_surface(), (255, 255, 0), proximity_rect, 1)
                print("Jugador cerca del área de la misión")

        # Actualizar el estado
        self.player_near_mission = near_mission
        #print("[DEBUG] check_mission_area se llamó")

        return near_mission
    
    def check_info_area(self, player_rect):
        """Detecta si el jugador está cerca del segundo objeto interactivo"""
        import pygame 
    
        info_rect_abs = pygame.Rect(
            self.info_rect.x + self.bg_x_offset,
            self.info_rect.y + self.bg_y_offset,
            self.info_rect.width,
            self.info_rect.height
        )
        proximity_rect = info_rect_abs.inflate(230, 230)

        self.player_near_info = proximity_rect.colliderect(player_rect)

        if DEBUG_MODE:
            pygame.draw.rect(pygame.display.get_surface(), (0, 100, 255), info_rect_abs, 2)
            pygame.draw.rect(pygame.display.get_surface(), (0, 80, 200), proximity_rect, 1)
            if self.player_near_info:
                print("Jugador cerca del objeto informativo")

        return self.player_near_info

    def update(self):
        """Update room state"""
        super().update()  # Llamar al método update de la clase padre

        # Actualizar el tiempo de animación
        self.animation_time += 1

        # Actualizar el valor de brillo (oscila entre 0 y 1)
        self.glow_value = (math.sin(self.animation_time * 0.05) + 1) / 2

        if hasattr(self, "player"):
            self.check_info_area(self.player.rect)

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= max_width:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines

    def _check_completion(self):
        """Room is always completed"""
        self.completed = True

    def handle_event(self, event):
        # Si la actividad está activa, manejar sus eventos
        if self.activity.active:
            self.activity.handle_event(event)
            return
        
        if self.showing_info and hasattr(self, "info_close_button"):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.info_close_button.collidepoint(event.pos):
                    self.showing_info = False
        
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
            elif event.key == pygame.K_SPACE:  # Tecla espacio para interactuar con la misión
                # Verificar si el jugador está cerca del área de la misión
                if self.player_near_mission:
                    # Activar la actividad educativa
                    self.activity.activate()
                    print("Actividad educativa activada")
                elif self.player_near_info:
                    self.showing_info = True

    def render(self, screen):
        if self.scaled_bg:
            screen.blit(self.scaled_bg, (self.bg_x_offset, self.bg_y_offset))
        else:
            screen.fill((0,0,0))
         # Dibujar la imagen de la misión con animación
        if self.mission_img:
            # Calcular la posición base para centrar la imagen en el rectángulo
            base_x = self.mission_rect.x + self.bg_x_offset + (self.mission_rect.width - self.mission_img.get_width()) // 2
            base_y = self.mission_rect.y + self.bg_y_offset + (self.mission_rect.height - self.mission_img.get_height()) // 2

            # Aplicar efecto de flotación usando funciones sinusoidales
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude

            # Posición final con efecto de flotación
            mission_pos = (base_x, base_y + float_offset_y)

            # Aplicar efecto de brillo si el jugador está cerca
            if self.player_near_mission:
                # Crear una superficie para el halo
                glow_width = self.mission_img.get_width() + 60
                glow_height = self.mission_img.get_height() + 30
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

                # Dibujar un halo alrededor de la imagen
                glow_color = (255, 255, 100, int(100 * self.glow_value))  # Amarillo con transparencia variable
                halo_rect = pygame.Rect(0, 0, glow_width, glow_height)
                halo_rect.inflate_ip(1, -20)  # Más ancho, menos alto

                pygame.draw.ellipse(
                    glow_surface,
                    glow_color,
                    halo_rect
                )

                # Dibujar el halo
                glow_pos = (mission_pos[0] - 30, mission_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            # Dibujar la imagen principal
            #screen.blit(self.mission_img, mission_pos)

            # Efecto simple de partículas si el jugador está cerca
            if self.player_near_mission and random.random() < 0.03:  # 3% de probabilidad por frame
                # Dibujar pequeños destellos alrededor de la imagen
                for _ in range(2):  # Crear solo 2 partículas a la vez para evitar sobrecarga
                    # Posición aleatoria alrededor de la imagen
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-20, 20)
                    particle_pos = (
                        mission_pos[0] + self.mission_img.get_width() // 2 + offset_x,
                        mission_pos[1] + self.mission_img.get_height() // 2 + offset_y
                    )
                    # Color aleatorio para el destello
                    particle_color = (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    )
                    # Dibujar un pequeño círculo como destello
                    pygame.draw.circle(screen, particle_color, particle_pos, random.randint(1, 3))

                    # Solo dibuja los rectángulos de colisión si estamos en modo debug
        if self.mission_img:
            # Imagen flotante para el segundo objeto
            base_x = self.info_rect.x + self.bg_x_offset + (self.info_rect.width - self.mission_img.get_width()) // 2
            base_y = self.info_rect.y + self.bg_y_offset + (self.info_rect.height - self.mission_img.get_height()) // 2
            float_offset_y = math.sin(self.animation_time * self.float_speed) * self.float_amplitude
            info_pos = (base_x, base_y + float_offset_y)

            if self.player_near_info:
                glow_width = self.mission_img.get_width() + 20
                glow_height = self.mission_img.get_height() + 20
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                glow_color = (120, 220, 255, int(100 * self.glow_value))  # Azul claro
                pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect())
                glow_pos = (info_pos[0] - 10, info_pos[1] - 10)
                screen.blit(glow_surface, glow_pos)

            #screen.blit(self.mission_img, info_pos)


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
    
    def render_info_modal(self, screen):
        modal_width = 500
        font = pygame.font.Font(None, 22)

        info_text = (
            "Hola, bienvenido. Estás colaborando con el equipo de desarrollo de FitHomeApp. "
            "Nuestro equipo ha estado trabajando en varias funcionalidades clave. Tu tarea es ayudarnos a actualizar el tablero Scrum, colocando cada actividad en la columna que le corresponde según su estado real. "
            "El diseño del logo fue aprobado por el cliente ayer después de algunos ajustes. "
            "Los desarrolladores están actualmente trabajando en la pantalla de inicio, integrando imágenes y botones funcionales. "
            "La base de datos aún no se ha iniciado, ya que se está esperando el esquema final aprobado. "
            "La revisión de código está asignada pero nadie la ha comenzado. "
            "Esta mañana, la redactora técnica comenzó a documentar las funcionalidades implementadas."
        )

        wrapped_info = self._wrap_text(info_text, font, modal_width - 40)

        line_spacing = 25
        text_margin_top = 40
        text_margin_bottom = 60
        modal_height = text_margin_top + len(wrapped_info) * line_spacing + text_margin_bottom

        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2

        pygame.draw.rect(screen, (240, 250, 255), (modal_x, modal_y, modal_width, modal_height), border_radius=12)
        pygame.draw.rect(screen, (30, 100, 160), (modal_x, modal_y, modal_width, modal_height), 3, border_radius=12)

        for i, line in enumerate(wrapped_info):
            text_surf = font.render(line, True, (20, 40, 60))
            text_rect = text_surf.get_rect(center=(modal_x + modal_width // 2, modal_y + 40 + i * 25))
            screen.blit(text_surf, text_rect)

        self.info_close_button = pygame.Rect(modal_x + modal_width - 110, modal_y + modal_height - 50, 90, 30)
        pygame.draw.rect(screen, (30, 100, 160), self.info_close_button, border_radius=8)
        screen.blit(font.render("Cerrar", True, WHITE), self.info_close_button.move(20, 5))



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

