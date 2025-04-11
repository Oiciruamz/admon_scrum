"""
Utility functions for the Escape Room game.
"""
import math
import random
import pygame
from settings import *

def draw_text(surface, text, font, color, x, y, align="center"):
    """
    Draw text on a surface with alignment options.

    Args:
        surface: Pygame surface to draw on
        text: Text to draw
        font: Pygame font object
        color: Text color
        x, y: Position coordinates
        align: Text alignment ("left", "center", "right")
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if align == "left":
        text_rect.topleft = (x, y)
    elif align == "center":
        text_rect.center = (x, y)
    elif align == "right":
        text_rect.topright = (x, y)

    surface.blit(text_surface, text_rect)
    return text_rect

def draw_button(surface, text, font, text_color, button_color, hover_color, x, y, width, height, radius=10, border_width=2, border_color=WHITE, hover=False):
    """
    Draw a button with text, hover effect, and rounded corners.

    Args:
        surface: Pygame surface to draw on
        text: Button text
        font: Pygame font object
        text_color: Text color
        button_color: Button background color
        hover_color: Button color when hovered
        x, y: Position coordinates (center of button)
        width, height: Button dimensions
        radius: Corner radius
        border_width: Border width
        border_color: Border color
        hover: Whether the button is being hovered

    Returns:
        Pygame Rect object for the button
    """
    button_rect = pygame.Rect(0, 0, width, height)
    button_rect.center = (x, y)

    # Draw button background with rounded corners
    color = hover_color if hover else button_color
    pygame.draw.rect(surface, color, button_rect, border_radius=radius)

    # Draw border
    if border_width > 0:
        pygame.draw.rect(surface, border_color, button_rect, border_width, border_radius=radius)

    # Draw text
    draw_text(surface, text, font, text_color, x, y, "center")

    return button_rect

def draw_panel(surface, x, y, width, height, color, border_color=WHITE, border_width=2, radius=10, alpha=255):
    """
    Draw a panel with rounded corners and optional transparency.

    Args:
        surface: Pygame surface to draw on
        x, y: Position coordinates (top-left corner)
        width, height: Panel dimensions
        color: Panel background color
        border_color: Border color
        border_width: Border width
        radius: Corner radius
        alpha: Transparency (0-255)

    Returns:
        Pygame Rect object for the panel
    """
    panel_rect = pygame.Rect(x, y, width, height)

    # Create a temporary surface for transparency
    if alpha < 255:
        temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, (*color, alpha), (0, 0, width, height), border_radius=radius)
        if border_width > 0:
            pygame.draw.rect(temp_surface, (*border_color, alpha), (0, 0, width, height), border_width, border_radius=radius)
        surface.blit(temp_surface, (x, y))
    else:
        pygame.draw.rect(surface, color, panel_rect, border_radius=radius)
        if border_width > 0:
            pygame.draw.rect(surface, border_color, panel_rect, border_width, border_radius=radius)

    return panel_rect

def draw_progress_bar(surface, x, y, width, height, progress, bg_color, fill_color, border_color=WHITE, border_width=2, radius=5):
    """
    Draw a progress bar.

    Args:
        surface: Pygame surface to draw on
        x, y: Position coordinates (top-left corner)
        width, height: Bar dimensions
        progress: Progress value (0.0 to 1.0)
        bg_color: Background color
        fill_color: Fill color
        border_color: Border color
        border_width: Border width
        radius: Corner radius
    """
    # Clamp progress value
    progress = max(0.0, min(1.0, progress))

    # Draw background
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, bg_rect, border_radius=radius)

    # Draw fill
    if progress > 0:
        fill_width = int(width * progress)
        fill_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=radius)

    # Draw border
    if border_width > 0:
        pygame.draw.rect(surface, border_color, bg_rect, border_width, border_radius=radius)

def draw_tooltip(surface, text, font, x, y, padding=10, bg_color=CHARCOAL, text_color=WHITE, border_color=WHITE, border_width=1, radius=5, max_width=300):
    """
    Draw a tooltip with text wrapping.

    Args:
        surface: Pygame surface to draw on
        text: Tooltip text
        font: Pygame font object
        x, y: Position coordinates (point where tooltip appears)
        padding: Padding inside tooltip
        bg_color: Background color
        text_color: Text color
        border_color: Border color
        border_width: Border width
        radius: Corner radius
        max_width: Maximum width for text wrapping
    """
    # Wrap text
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word + ' ', True, text_color)
        word_width = word_surface.get_width()

        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width

    if current_line:
        lines.append(' '.join(current_line))

    # Calculate tooltip dimensions
    line_height = font.get_height()
    tooltip_height = len(lines) * line_height + 2 * padding
    tooltip_width = max_width + 2 * padding

    # Position tooltip to avoid going off screen
    tooltip_x = x
    if tooltip_x + tooltip_width > WINDOW_WIDTH:
        tooltip_x = WINDOW_WIDTH - tooltip_width - 10

    tooltip_y = y - tooltip_height - 10
    if tooltip_y < 10:
        tooltip_y = y + 30

    # Draw tooltip background
    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(surface, bg_color, tooltip_rect, border_radius=radius)

    # Draw border
    if border_width > 0:
        pygame.draw.rect(surface, border_color, tooltip_rect, border_width, border_radius=radius)

    # Draw text
    for i, line in enumerate(lines):
        line_y = tooltip_y + padding + i * line_height
        draw_text(surface, line, font, text_color, tooltip_x + padding, line_y, "left")

def create_particle_effect(x, y, count=20, colors=None, min_speed=1, max_speed=3, min_size=2, max_size=5, min_lifetime=20, max_lifetime=40):
    """
    Create a particle effect.

    Args:
        x, y: Position coordinates (center of effect)
        count: Number of particles
        colors: List of colors to choose from
        min_speed, max_speed: Speed range
        min_size, max_size: Size range
        min_lifetime, max_lifetime: Lifetime range in frames

    Returns:
        List of particle dictionaries
    """
    if colors is None:
        colors = [WHITE, YELLOW, ORANGE]

    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(min_speed, max_speed)
        size = random.randint(min_size, max_size)
        lifetime = random.randint(min_lifetime, max_lifetime)
        color = random.choice(colors)

        particles.append({
            'x': x,
            'y': y,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'size': size,
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })

    return particles

def update_particles(particles):
    """
    Update particle positions and lifetimes.

    Args:
        particles: List of particle dictionaries

    Returns:
        Updated list of particles
    """
    updated_particles = []

    for particle in particles:
        # Update position
        particle['x'] += particle['dx']
        particle['y'] += particle['dy']

        # Update lifetime
        particle['lifetime'] -= 1

        # Keep particle if still alive
        if particle['lifetime'] > 0:
            updated_particles.append(particle)

    return updated_particles

def render_particles(surface, particles):
    """
    Render particles on the surface.

    Args:
        surface: Pygame surface to draw on
        particles: List of particle dictionaries
    """
    for particle in particles:
        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
        color = particle['color']

        # Draw particle
        pygame.draw.circle(
            surface,
            color,
            (int(particle['x']), int(particle['y'])),
            particle['size']
        )

def distance(point1, point2):
    """
    Calculate Euclidean distance between two points.

    Args:
        point1: First point (x, y)
        point2: Second point (x, y)

    Returns:
        Distance between points
    """
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def lerp(start, end, t):
    """
    Linear interpolation between two values.

    Args:
        start: Start value
        end: End value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value
    """
    return start + (end - start) * t

def color_lerp(color1, color2, t):
    """
    Linear interpolation between two colors.

    Args:
        color1: First color (r, g, b)
        color2: Second color (r, g, b)
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated color (r, g, b)
    """
    r = int(lerp(color1[0], color2[0], t))
    g = int(lerp(color1[1], color2[1], t))
    b = int(lerp(color1[2], color2[2], t))
    return (r, g, b)

def pulse_value(base_value, amplitude, speed, time):
    """
    Create a pulsing value over time.

    Args:
        base_value: Base value
        amplitude: Pulse amplitude
        speed: Pulse speed
        time: Current time

    Returns:
        Pulsed value
    """
    return base_value + amplitude * math.sin(speed * time)

def shake_value(base_value, intensity):
    """
    Create a shaking effect.

    Args:
        base_value: Base value
        intensity: Shake intensity

    Returns:
        Shaken value
    """
    return base_value + random.uniform(-intensity, intensity)

def load_image(path, scale=None, alpha=False):
    """
    Load an image from file.

    Args:
        path: Image file path
        scale: Optional tuple (width, height) to scale the image
        alpha: Whether the image has transparency

    Returns:
        Pygame Surface or None if error
    """
    try:
        # Verificar que el archivo existe
        import os
        if not os.path.exists(path):
            print(f"Error: El archivo de imagen no existe: {path}")
            raise FileNotFoundError(f"No se encontró el archivo: {path}")

        # Cargar la imagen
        print(f"Cargando imagen: {path}")
        image = pygame.image.load(path)

        # Convertir formato según transparencia
        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

        # Escalar si es necesario
        if scale:
            image = pygame.transform.scale(image, scale)

        print(f"Imagen cargada correctamente: {path} - Dimensiones: {image.get_width()}x{image.get_height()}")
        return image
    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado - {path}: {e}")
        # Create a placeholder surface
        placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, PURPLE, (0, 0, 64, 64))
        pygame.draw.line(placeholder, BLACK, (0, 0), (64, 64), 2)
        pygame.draw.line(placeholder, BLACK, (64, 0), (0, 64), 2)
        return placeholder
    except pygame.error as e:
        print(f"Error de Pygame al cargar imagen {path}: {e}")
        # Create a placeholder surface
        placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, PURPLE, (0, 0, 64, 64))
        pygame.draw.line(placeholder, BLACK, (0, 0), (64, 64), 2)
        pygame.draw.line(placeholder, BLACK, (64, 0), (0, 64), 2)
        return placeholder
    except Exception as e:
        print(f"Error inesperado al cargar imagen {path}: {e}")
        # Create a placeholder surface
        placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, RED, (0, 0, 64, 64))
        pygame.draw.line(placeholder, BLACK, (0, 0), (64, 64), 2)
        pygame.draw.line(placeholder, BLACK, (64, 0), (0, 64), 2)
        return placeholder

def load_sound(path):
    """
    Load a sound from file.

    Args:
        path: Sound file path

    Returns:
        Pygame Sound object
    """
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Error loading sound {path}: {e}")
        return None

def play_sound(sound, volume=1.0, loop=False):
    """
    Play a sound.

    Args:
        sound: Pygame Sound object
        volume: Volume (0.0 to 1.0)
        loop: Whether to loop the sound
    """
    if sound:
        sound.set_volume(volume)
        if loop:
            sound.play(-1)
        else:
            sound.play()

def stop_sound(sound):
    """
    Stop a sound.

    Args:
        sound: Pygame Sound object
    """
    if sound:
        sound.stop()

def color_lerp(color1, color2, t):
    """
    Linearly interpolate between two colors.

    Args:
        color1: First color (r, g, b) tuple
        color2: Second color (r, g, b) tuple
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated color
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    t = max(0.0, min(1.0, t))  # Clamp t to range [0, 1]

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return (r, g, b)

def draw_decorative_border(surface, rect, color, width=4, corner_size=20, dash_pattern=None):
    """
    Draw a decorative border with stylized corners in Stardew Valley style.

    Args:
        surface: Pygame surface to draw on
        rect: Rectangle to draw border around
        color: Border color
        width: Border width
        corner_size: Size of corner decorations
        dash_pattern: Optional tuple (dash_length, gap_length) for dashed lines
    """
    x, y, w, h = rect

    # Draw the main border lines
    if dash_pattern:
        dash_length, gap_length = dash_pattern
        # Top line
        draw_dashed_line(surface, color, (x + corner_size, y), (x + w - corner_size, y), width, dash_length, gap_length)
        # Bottom line
        draw_dashed_line(surface, color, (x + corner_size, y + h), (x + w - corner_size, y + h), width, dash_length, gap_length)
        # Left line
        draw_dashed_line(surface, color, (x, y + corner_size), (x, y + h - corner_size), width, dash_length, gap_length)
        # Right line
        draw_dashed_line(surface, color, (x + w, y + corner_size), (x + w, y + h - corner_size), width, dash_length, gap_length)
    else:
        # Top line
        pygame.draw.line(surface, color, (x + corner_size, y), (x + w - corner_size, y), width)
        # Bottom line
        pygame.draw.line(surface, color, (x + corner_size, y + h), (x + w - corner_size, y + h), width)
        # Left line
        pygame.draw.line(surface, color, (x, y + corner_size), (x, y + h - corner_size), width)
        # Right line
        pygame.draw.line(surface, color, (x + w, y + corner_size), (x + w, y + h - corner_size), width)

    # Draw decorative corners
    # Top-left corner
    pygame.draw.line(surface, color, (x, y + corner_size), (x + corner_size, y), width)
    # Top-right corner
    pygame.draw.line(surface, color, (x + w - corner_size, y), (x + w, y + corner_size), width)
    # Bottom-left corner
    pygame.draw.line(surface, color, (x, y + h - corner_size), (x + corner_size, y + h), width)
    # Bottom-right corner
    pygame.draw.line(surface, color, (x + w - corner_size, y + h), (x + w, y + h - corner_size), width)

    # Add small decorative dots at corners
    dot_size = width // 2 + 1
    pygame.draw.circle(surface, color, (x + corner_size, y), dot_size)
    pygame.draw.circle(surface, color, (x + w - corner_size, y), dot_size)
    pygame.draw.circle(surface, color, (x + corner_size, y + h), dot_size)
    pygame.draw.circle(surface, color, (x + w - corner_size, y + h), dot_size)
    pygame.draw.circle(surface, color, (x, y + corner_size), dot_size)
    pygame.draw.circle(surface, color, (x + w, y + corner_size), dot_size)
    pygame.draw.circle(surface, color, (x, y + h - corner_size), dot_size)
    pygame.draw.circle(surface, color, (x + w, y + h - corner_size), dot_size)

def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=10, gap_length=5):
    """
    Draw a dashed line.

    Args:
        surface: Pygame surface to draw on
        color: Line color
        start_pos: Start position (x, y)
        end_pos: End position (x, y)
        width: Line width
        dash_length: Length of each dash
        gap_length: Length of each gap
    """
    x1, y1 = start_pos
    x2, y2 = end_pos

    # Calculate line length and angle
    dx = x2 - x1
    dy = y2 - y1
    distance = max(1, math.sqrt(dx * dx + dy * dy))

    # Normalize direction vector
    dx, dy = dx / distance, dy / distance

    # Calculate number of segments
    segment_length = dash_length + gap_length
    num_segments = int(distance / segment_length) + 1

    # Draw dashed line
    for i in range(num_segments):
        start = i * segment_length
        end = min(start + dash_length, distance)

        # Calculate dash start and end points
        dash_start_x = x1 + dx * start
        dash_start_y = y1 + dy * start
        dash_end_x = x1 + dx * end
        dash_end_y = y1 + dy * end

        pygame.draw.line(surface, color, (dash_start_x, dash_start_y), (dash_end_x, dash_end_y), width)

def draw_stardew_button(surface, rect, text, font, text_color=WHITE, bg_color=SDV_BROWN,
                       border_color=SDV_LIGHT_BROWN, hover=False, active=False):
    """
    Draw a button in Stardew Valley style.

    Args:
        surface: Pygame surface to draw on
        rect: Button rectangle
        text: Button text
        font: Pygame font object
        text_color: Text color
        bg_color: Background color
        border_color: Border color
        hover: Whether the button is being hovered
        active: Whether the button is active/selected
    """
    x, y, w, h = rect

    # Draw button background with a wood-like gradient
    if hover:
        bg_color = color_lerp(bg_color, WHITE, 0.2)
    elif active:
        bg_color = color_lerp(bg_color, BLACK, 0.2)

    # Create a gradient effect
    for i in range(h):
        shade = 1.0 - (i / h) * 0.3  # Darker at bottom
        current_color = color_lerp(bg_color, BLACK, 1.0 - shade)
        pygame.draw.line(surface, current_color, (x, y + i), (x + w - 1, y + i))

    # Draw border
    border_width = 2
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=5)

    # Add a highlight at the top for 3D effect
    highlight_color = color_lerp(bg_color, WHITE, 0.5)
    pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + w - 3, y + 2), 1)

    # Draw text with a slight shadow for depth
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))

    # Draw text shadow
    shadow_surface = font.render(text, True, BLACK)
    shadow_rect = shadow_surface.get_rect(center=(x + w // 2 + 2, y + h // 2 + 2))
    surface.blit(shadow_surface, shadow_rect)

    # Draw text
    surface.blit(text_surface, text_rect)

    return rect

def draw_stardew_title(surface, text, font, x, y, main_color=SDV_YELLOW, shadow_color=SDV_BROWN, outline=True):
    """
    Draw a title in Stardew Valley style with shadow and outline.

    Args:
        surface: Pygame surface to draw on
        text: Title text
        font: Pygame font object
        x, y: Position coordinates (center of title)
        main_color: Main text color
        shadow_color: Shadow color
        outline: Whether to draw an outline
    """
    # Draw shadow (offset text)
    shadow_offset = 4
    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(center=(x + shadow_offset, y + shadow_offset))
    surface.blit(shadow_surface, shadow_rect)

    # Draw main text
    text_surface = font.render(text, True, main_color)
    text_rect = text_surface.get_rect(center=(x, y))

    # Draw outline if requested
    if outline:
        # Draw text slightly offset in all directions for outline effect
        outline_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for offset_x, offset_y in outline_offsets:
            outline_rect = text_rect.copy()
            outline_rect.x += offset_x
            outline_rect.y += offset_y
            outline_surface = font.render(text, True, BLACK)
            surface.blit(outline_surface, outline_rect)

    # Draw main text on top
    surface.blit(text_surface, text_rect)

    return text_rect

def create_shadow(surface, offset=(4, 4), color=BLACK, alpha=128):
    """
    Create a shadow effect for a surface.

    Args:
        surface: Pygame Surface
        offset: Shadow offset (x, y)
        color: Shadow color
        alpha: Shadow transparency (0-255)

    Returns:
        Shadow surface
    """
    shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shadow_rect = shadow.get_rect(topleft=offset)

    # Create mask from original surface
    mask = pygame.mask.from_surface(surface)
    mask_surface = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))

    # Apply alpha
    mask_surface.set_alpha(alpha)

    # Blit mask to shadow surface
    shadow.blit(mask_surface, (0, 0))

    return shadow
