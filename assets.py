"""
Asset management for the Escape Room game.
"""
import os
import math
import pygame
from settings import *
from utils import load_image, load_sound, color_lerp

class AssetManager:
    """
    Manages game assets (images, sounds, fonts).
    """
    def __init__(self):
        """
        Initialize the asset manager.
        """
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.animations = {}
        self.initialized = False

        # Initialize pygame font module
        if not pygame.font.get_init():
            pygame.font.init()

        # Load fonts
        self._load_fonts()

    def initialize(self):
        """
        Initialize assets after pygame.display is initialized.
        This should be called after pygame.display.set_mode().
        """
        if self.initialized:
            return

        # Load actual game assets
        self.load_game_assets()

        # Create placeholder images for development
        self.create_placeholder_images()

        self.initialized = True

    def load_game_assets(self):
        """
        Load actual game assets from files.
        """
        # Cargar la imagen de fondo para todas las pantallas
        try:
            # Cargar la imagen original
            original_bg = load_image("img/fondo.png", None, True)
            if original_bg is None:
                raise ValueError("No se pudo cargar la imagen de fondo")

            # Escalar la imagen para que se ajuste a la ventana manteniendo la proporción
            bg_width, bg_height = original_bg.get_width(), original_bg.get_height()
            scale_factor = min(WINDOW_WIDTH / bg_width, WINDOW_HEIGHT / bg_height)
            new_width = int(bg_width * scale_factor)
            new_height = int(bg_height * scale_factor)

            # Crear una superficie del tamaño de la ventana
            background_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            background_image.fill(BLACK)  # Fondo negro para las áreas no cubiertas

            # Escalar la imagen original
            scaled_bg = pygame.transform.scale(original_bg, (new_width, new_height))

            # Centrar la imagen en la ventana
            x_offset = (WINDOW_WIDTH - new_width) // 2
            y_offset = (WINDOW_HEIGHT - new_height) // 2
            background_image.blit(scaled_bg, (x_offset, y_offset))

            # Guardar la imagen de fondo como un recurso común para todas las pantallas
            self.images["common_background"] = background_image
            print("Imagen de fondo cargada y escalada correctamente para todas las pantallas")
        except Exception as e:
            print(f"Error al cargar la imagen de fondo: {e}")

        # Cargar el sprite sheet del personaje (mono con traje) sin animación hacia abajo
        sprite_sheet = load_image("img/mono_traje.png", None, True)
        if sprite_sheet is None:
            raise ValueError("No se pudo cargar el sprite sheet del personaje")
        # Obtener dimensiones del sprite sheet
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        frame_width = sheet_width // 3  # 3 columnas
        frame_height = sheet_height // 2  # 2 filas
        self.animations["player_down"] = []
        # Usar el primer frame como imagen estática del jugador
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.fill((0, 0, 0, 0))
        frame.blit(sprite_sheet, (0, 0), (0, 0, frame_width, frame_height))
        frame = pygame.transform.scale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.images["player"] = frame

        # Cargar el sprite sheet original para las otras direcciones
        sprite_sheet = load_image("img/mono_traje.png", None, True)
        if sprite_sheet is None:
            raise ValueError("No se pudo cargar el sprite sheet del personaje para otras direcciones")
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        frame_width = sheet_width // 3
        frame_height = sheet_height // 2
        self.animations["player_up"] = []
        for i in range(1, 3):
            back_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            back_frame.fill((0, 0, 0, 0))
            back_frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            back_frame = pygame.transform.scale(back_frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.animations["player_up"].append(back_frame)
        self.animations["player_left"] = []
        self.animations["player_right"] = []
        for i in range(3):
            left_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            left_frame.fill((0, 0, 0, 0))
            left_frame.blit(sprite_sheet, (0, 0), (i * frame_width, frame_height, frame_width, frame_height))
            left_frame = pygame.transform.scale(left_frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.animations["player_left"].append(left_frame)
            right_frame = pygame.transform.flip(left_frame, True, False)
            self.animations["player_right"].append(right_frame)
        print("Sprite sheets del personaje cargados y divididos correctamente")

    def initialize_fonts(self):
        """
        Initialize fonts after pygame.font is initialized.
        This should be called after pygame.font.init().
        """
        self.load_default_fonts()

    def load_default_fonts(self):
        """
        Load default system fonts.
        """
        self.fonts["large"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_LARGE)
        self.fonts["medium"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_MEDIUM)
        self.fonts["small"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL)
        self.fonts["tiny"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_TINY)

        # Bold variants
        self.fonts["large_bold"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_LARGE, bold=True)
        self.fonts["medium_bold"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_MEDIUM, bold=True)
        self.fonts["small_bold"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_SMALL, bold=True)
        self.fonts["tiny_bold"] = pygame.font.SysFont("Arial", UI_FONT_SIZE_TINY, bold=True)

    def _load_fonts(self):
        """
        Load fonts into the assets manager.
        """
        self.fonts["stardew_large"] = pygame.font.Font("assets/fonts/Stardew_Valley.ttf", 72)
        self.fonts["stardew_medium"] = pygame.font.Font("assets/fonts/Stardew_Valley.ttf", 36)
        self.fonts["stardew_small"] = pygame.font.Font("assets/fonts/Stardew_Valley.ttf", 24)

    def create_placeholder_images(self):
        """
        Create placeholder images for development.
        """
        # Player placeholder (solo si no se cargó la imagen real)
        if "player" not in self.images:
            player_surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(player_surface, BLUE, (PLAYER_WIDTH // 2, PLAYER_HEIGHT // 2), PLAYER_WIDTH // 2)
            pygame.draw.circle(player_surface, WHITE, (PLAYER_WIDTH // 2, PLAYER_HEIGHT // 2), PLAYER_WIDTH // 2, 2)
            self.images["player"] = player_surface

        # Room background placeholders
        for color_name, color in [
            ("gray", GRAY),
            ("blue", LIGHT_BLUE),
            ("green", GREEN),
            ("red", RED),
            ("yellow", YELLOW),
            ("purple", PURPLE),
            ("cyan", CYAN),
            ("orange", ORANGE)
        ]:
            room_surface = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT))
            room_surface.fill(color)

            # Add grid pattern
            grid_size = 50
            for x in range(0, ROOM_WIDTH, grid_size):
                pygame.draw.line(room_surface, (*color_lerp(color, BLACK, 0.2), 128), (x, 0), (x, ROOM_HEIGHT))
            for y in range(0, ROOM_HEIGHT, grid_size):
                pygame.draw.line(room_surface, (*color_lerp(color, BLACK, 0.2), 128), (0, y), (ROOM_WIDTH, y))

            # Add border
            pygame.draw.rect(room_surface, color_lerp(color, WHITE, 0.3), (0, 0, ROOM_WIDTH, ROOM_HEIGHT), ROOM_BORDER_WIDTH)

            self.images[f"room_{color_name}"] = room_surface

        # Object placeholders
        for shape in ["circle", "square", "triangle", "diamond", "hexagon"]:
            for color_name, color in [
                ("red", RED),
                ("green", GREEN),
                ("blue", BLUE),
                ("yellow", YELLOW),
                ("purple", PURPLE),
                ("cyan", CYAN),
                ("orange", ORANGE),
                ("white", WHITE)
            ]:
                obj_surface = pygame.Surface((100, 100), pygame.SRCALPHA)

                if shape == "circle":
                    pygame.draw.circle(obj_surface, color, (50, 50), 40)
                    pygame.draw.circle(obj_surface, WHITE, (50, 50), 40, 2)
                elif shape == "square":
                    pygame.draw.rect(obj_surface, color, (10, 10, 80, 80))
                    pygame.draw.rect(obj_surface, WHITE, (10, 10, 80, 80), 2)
                elif shape == "triangle":
                    pygame.draw.polygon(obj_surface, color, [(50, 10), (10, 90), (90, 90)])
                    pygame.draw.polygon(obj_surface, WHITE, [(50, 10), (10, 90), (90, 90)], 2)
                elif shape == "diamond":
                    pygame.draw.polygon(obj_surface, color, [(50, 10), (90, 50), (50, 90), (10, 50)])
                    pygame.draw.polygon(obj_surface, WHITE, [(50, 10), (90, 50), (50, 90), (10, 50)], 2)
                elif shape == "hexagon":
                    points = []
                    for i in range(6):
                        angle = i * (2 * 3.14159 / 6)
                        points.append((50 + 40 * math.cos(angle), 50 + 40 * math.sin(angle)))
                    pygame.draw.polygon(obj_surface, color, points)
                    pygame.draw.polygon(obj_surface, WHITE, points, 2)

                self.images[f"object_{shape}_{color_name}"] = obj_surface

        # UI elements
        # Button
        button_surface = pygame.Surface((UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, CHARCOAL, (0, 0, UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT), border_radius=UI_BUTTON_RADIUS)
        pygame.draw.rect(button_surface, WHITE, (0, 0, UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT), 2, border_radius=UI_BUTTON_RADIUS)
        self.images["button"] = button_surface

        # Button hover
        button_hover_surface = pygame.Surface((UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(button_hover_surface, color_lerp(CHARCOAL, WHITE, 0.3), (0, 0, UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT), border_radius=UI_BUTTON_RADIUS)
        pygame.draw.rect(button_hover_surface, WHITE, (0, 0, UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT), 2, border_radius=UI_BUTTON_RADIUS)
        self.images["button_hover"] = button_hover_surface

        # Panel
        panel_surface = pygame.Surface((400, 300), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*CHARCOAL, 220), (0, 0, 400, 300), border_radius=10)
        pygame.draw.rect(panel_surface, WHITE, (0, 0, 400, 300), 2, border_radius=10)
        self.images["panel"] = panel_surface

        # Icons
        # Clock icon
        clock_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(clock_surface, WHITE, (16, 16), 15, 2)
        pygame.draw.line(clock_surface, WHITE, (16, 16), (16, 8), 2)
        pygame.draw.line(clock_surface, WHITE, (16, 16), (22, 16), 2)
        self.images["icon_clock"] = clock_surface

        # Info icon
        info_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(info_surface, WHITE, (16, 16), 15, 2)
        pygame.draw.line(info_surface, WHITE, (16, 10), (16, 10), 3)
        pygame.draw.line(info_surface, WHITE, (16, 14), (16, 22), 2)
        self.images["icon_info"] = info_surface

        # Check icon
        check_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.polygon(check_surface, GREEN, [(8, 16), (14, 22), (24, 10), (22, 8), (14, 18), (10, 14)])
        self.images["icon_check"] = check_surface

        # Cross icon
        cross_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, RED, (8, 8), (24, 24), 3)
        pygame.draw.line(cross_surface, RED, (24, 8), (8, 24), 3)
        self.images["icon_cross"] = cross_surface

        # Lock icon
        lock_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(lock_surface, WHITE, (8, 14, 16, 14), 2, border_radius=2)
        pygame.draw.arc(lock_surface, WHITE, (8, 4, 16, 20), 3.14, 0, 2)
        self.images["icon_lock"] = lock_surface

        # Key icon
        key_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(key_surface, YELLOW, (10, 16), 6, 2)
        pygame.draw.line(key_surface, YELLOW, (16, 16), (26, 16), 2)
        pygame.draw.line(key_surface, YELLOW, (22, 12), (22, 20), 2)
        pygame.draw.line(key_surface, YELLOW, (26, 12), (26, 20), 2)
        self.images["icon_key"] = key_surface

    def load_image(self, name, path, scale=None, alpha=True):
        """
        Load an image and store it with the given name.

        Args:
            name: Name to reference the image
            path: Image file path
            scale: Optional tuple (width, height) to scale the image
            alpha: Whether the image has transparency
        """
        self.images[name] = load_image(path, scale, alpha)

    def load_sound(self, name, path):
        """
        Load a sound and store it with the given name.

        Args:
            name: Name to reference the sound
            path: Sound file path
        """
        self.sounds[name] = load_sound(path)

    def load_font(self, name, path, size):
        """
        Load a font and store it with the given name.

        Args:
            name: Name to reference the font
            path: Font file path
            size: Font size
        """
        try:
            self.fonts[name] = pygame.font.Font(path, size)
        except pygame.error as e:
            print(f"Error loading font {path}: {e}")
            # Fall back to system font
            self.fonts[name] = pygame.font.SysFont("Arial", size)

    def load_animation(self, name, path_pattern, frame_count, scale=None, alpha=True):
        """
        Load an animation sequence.

        Args:
            name: Name to reference the animation
            path_pattern: Pattern for frame paths (e.g., "player_{:02d}.png")
            frame_count: Number of frames
            scale: Optional tuple (width, height) to scale the frames
            alpha: Whether the frames have transparency
        """
        frames = []
        for i in range(frame_count):
            path = path_pattern.format(i)
            frame = load_image(path, scale, alpha)
            frames.append(frame)

        self.animations[name] = frames

    def get_image(self, name):
        """
        Get an image by name.

        Args:
            name: Image name

        Returns:
            Pygame Surface
        """
        if name in self.images:
            return self.images[name]
        else:
            print(f"Warning: Image '{name}' not found")
            return self.images.get("player", pygame.Surface((32, 32)))

    def get_sound(self, name):
        """
        Get a sound by name.

        Args:
            name: Sound name

        Returns:
            Pygame Sound object
        """
        return self.sounds.get(name)

    def get_font(self, name):
        """
        Get a font by name.

        Args:
            name: Font name

        Returns:
            Pygame Font object
        """
        return self.fonts.get(name, self.fonts["medium"])

    def get_animation(self, name):
        """
        Get an animation by name.

        Args:
            name: Animation name

        Returns:
            List of Pygame Surfaces
        """
        return self.animations.get(name, [])

# Global asset manager instance
assets = AssetManager()
