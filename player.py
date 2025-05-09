"""
Player class for the Escape Room game.
"""
import math
import random
import pygame
from settings import *
from assets import assets
from utils import create_particle_effect, update_particles, render_particles

class Player:
    """
    Player character that can move around and interact with objects.
    """
    def __init__(self):
        """
        Initialize the player.
        """
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        # Cambiar posición inicial al borde inferior derecho
        self.x = WINDOW_WIDTH - self.width - 50  # 50 píxeles desde el borde derecho
        self.y = WINDOW_HEIGHT - self.height - 50  # 50 píxeles desde el borde inferior
        self.speed = PLAYER_SPEED
        self.base_speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Crear un rectángulo de colisión más pequeño para los pies
        # Ajustamos el tamaño del rectángulo de colisión para que sea proporcional al nuevo tamaño del jugador
        feet_width = self.width // 3  # El rectángulo de los pies será 1/3 del ancho del sprite
        feet_height = self.height // 4  # Y 1/4 de la altura
        self.feet_rect = pygame.Rect(
            self.x + (self.width - feet_width) // 2,  # Centrado horizontalmente
            self.y + self.height - feet_height,  # En la parte inferior del sprite
            feet_width,
            feet_height
        )

        # Movement flags
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

        # Direction (for animation)
        self.direction = 'down'  # 'up', 'down', 'left', 'right'

        # Animation
        self.animation_frame = 0
        self.animation_time = 0
        self.animation_speed = PLAYER_ANIMATION_SPEED
        self.is_moving = False

        # Interaction
        self.interacting = False
        self.interaction_radius = OBJECT_INTERACTION_DISTANCE
        self.interaction_cooldown = 0
        self.interaction_cooldown_max = 20  # frames

        # Visual effects
        self.particles = []
        self.shadow_offset = (4, 4)
        self.glow_radius = 0
        self.glow_max = 20
        self.glow_speed = 0.1
        self.glow_time = 0

        # Status effects
        self.speed_boost = 0
        self.speed_boost_time = 0
        self.invincible = False
        self.invincible_time = 0
        self.confused = False
        self.confused_time = 0

    def handle_event(self, event):
        """
        Handle player input events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.moving_left = True
            elif event.key == pygame.K_RIGHT:
                self.moving_right = True
            elif event.key == pygame.K_UP:
                self.moving_up = True
            elif event.key == pygame.K_DOWN:
                self.moving_down = True
            elif event.key == pygame.K_SPACE:
                self.interacting = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.moving_left = False
            elif event.key == pygame.K_RIGHT:
                self.moving_right = False
            elif event.key == pygame.K_UP:
                self.moving_up = False
            elif event.key == pygame.K_DOWN:
                self.moving_down = False
            elif event.key == pygame.K_SPACE:
                self.interacting = False

    def update(self):
        """
        Update player position based on movement flags.
        """
        # Update status effects
        self._update_status_effects()

        # Update movement
        self._update_movement()

        # Update animation
        self._update_animation()

        # Update interaction cooldown
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= 1

        # Update particles
        self.particles = update_particles(self.particles)

        # Update glow effect
        self.glow_time += self.glow_speed
        self.glow_radius = math.sin(self.glow_time) * self.glow_max / 2 + self.glow_max / 2

    def _update_status_effects(self):
        """
        Update player status effects.
        """
        # Speed boost
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost = 0

        # Invincibility
        if self.invincible_time > 0:
            self.invincible_time -= 1
            if self.invincible_time <= 0:
                self.invincible = False

        # Confusion
        if self.confused_time > 0:
            self.confused_time -= 1
            if self.confused_time <= 0:
                self.confused = False

        # Update speed based on effects
        self.speed = self.base_speed + self.speed_boost

    def _update_movement(self):
        """
        Update player position based on movement flags.
        """
        # Reset movement flag
        self.is_moving = False

        # Verificar si hay una actividad activa en la sala actual
        # Si hay una actividad activa, no permitir el movimiento
        if hasattr(self, 'current_room') and self.current_room:
            if hasattr(self.current_room, 'activity') and self.current_room.activity.active:
                return

        # Calculate movement based on direction flags
        dx = 0
        dy = 0

        if self.moving_left:
            dx -= self.speed
            self.direction = 'left'
            self.is_moving = True
        if self.moving_right:
            dx += self.speed
            self.direction = 'right'
            self.is_moving = True
        if self.moving_up:
            dy -= self.speed
            self.direction = 'up'
            self.is_moving = True
        if self.moving_down:
            dy += self.speed
            self.direction = 'down'
            self.is_moving = True

        # Apply confusion effect (reverse controls)
        if self.confused:
            dx = -dx
            dy = -dy

        # Crear un rect temporal para probar el movimiento
        temp_feet_rect = self.feet_rect.copy()
        temp_feet_rect.x = int(self.x + dx + (self.width - self.feet_rect.width) // 2)
        temp_feet_rect.y = int(self.y + dy + self.height - self.feet_rect.height)

        # Verificar si la nueva posición colisiona con algún área prohibida
        if hasattr(self, 'current_room') and self.current_room:
            if hasattr(self.current_room, 'check_collision'):
                if self.current_room.check_collision(temp_feet_rect):
                    # Si hay colisión, no permitir el movimiento
                    return

        # Si no hay colisión, actualizar la posición
        self.x += dx
        self.y += dy

        # Keep player within screen bounds
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))

        # Update rectangle positions
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.feet_rect.x = int(self.x + (self.width - self.feet_rect.width) // 2)
        self.feet_rect.y = int(self.y + self.height - self.feet_rect.height)

        # Create movement particles if moving
        if self.is_moving and random.random() < 0.1:
            particle_x = self.x + self.width // 2
            particle_y = self.y + self.height
            new_particles = create_particle_effect(
                particle_x, particle_y,
                count=3,
                colors=[GRAY, SILVER],
                min_speed=0.5, max_speed=1.5,
                min_size=2, max_size=4,
                min_lifetime=10, max_lifetime=20
            )
            self.particles.extend(new_particles)

    def _update_animation(self):
        """
        Update player animation frame.
        """
        if self.is_moving:
            # Actualizar el tiempo de animación
            self.animation_time += self.animation_speed

            # Reiniciar el tiempo de animación cuando llega a 1
            if self.animation_time >= 1:
                self.animation_time = 0
        else:
            # Cuando el jugador está quieto, reiniciar la animación
            self.animation_time = 0

    def render(self, screen):
        """
        Render the player.

        Args:
            screen: Pygame surface to render on
        """
        # Draw shadow
        shadow_x = self.x + self.shadow_offset[0]
        shadow_y = self.y + self.shadow_offset[1]
        pygame.draw.ellipse(screen, (*BLACK, 128), (shadow_x + self.width // 4, shadow_y + self.height // 2, self.width // 2, self.height // 4))

        # Get player image based on direction and animation frame
        player_image = self._get_current_frame()

        # Draw player
        screen.blit(player_image, (self.x, self.y))

        # Draw glow effect when interacting
        if self.interacting or self.interaction_cooldown > 0:
            glow_surface = pygame.Surface((self.width + self.glow_radius * 2, self.height + self.glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*YELLOW, 100),
                (self.width // 2 + self.glow_radius, self.height // 2 + self.glow_radius),
                self.interaction_radius
            )
            screen.blit(
                glow_surface,
                (self.x - self.glow_radius, self.y - self.glow_radius),
                special_flags=pygame.BLEND_ADD
            )

        # Draw particles
        render_particles(screen, self.particles)

        # Draw feet collision box if in debug mode
        if DEBUG_MODE:
            pygame.draw.rect(screen, (0, 255, 0), self.feet_rect, 2)

        # Draw status effect indicators
        self._render_status_effects(screen)

    def _get_current_frame(self):
        """
        Get the current animation frame based on direction and movement state.

        Returns:
            Pygame Surface with the current frame
        """
        # Determinar la animación a usar según la dirección
        animation_key = f"player_{self.direction}"

        # Obtener la lista de frames para esta dirección
        frames = assets.animations.get(animation_key, [])

        # Si no hay frames disponibles, usar la imagen estática
        if not frames:
            return assets.get_image("player")

        # Si el jugador está quieto, usar el primer frame
        if not self.is_moving:
            if self.direction == "down":
                return frames[0]  # Frame mirando al frente
            elif self.direction == "up":
                return frames[0]  # Primer frame mirando hacia atrás
            else:  # left o right
                return frames[0]  # Primer frame lateral

        # Si está en movimiento, usar el frame según el contador de animación
        frame_index = int(self.animation_time * len(frames))
        if frame_index >= len(frames):
            frame_index = 0

        return frames[frame_index]

    def _render_status_effects(self, screen):
        """
        Render status effect indicators.

        Args:
            screen: Pygame surface to render on
        """
        indicator_y = self.y - 20
        indicator_spacing = 15

        # Speed boost indicator
        if self.speed_boost > 0:
            pygame.draw.polygon(
                screen,
                CYAN,
                [
                    (self.x + self.width // 2, indicator_y),
                    (self.x + self.width // 2 - 5, indicator_y + 10),
                    (self.x + self.width // 2 + 5, indicator_y + 10)
                ]
            )
            indicator_y -= indicator_spacing

        # Invincibility indicator
        if self.invincible:
            pygame.draw.circle(screen, YELLOW, (self.x + self.width // 2, indicator_y + 5), 5)
            indicator_y -= indicator_spacing

        # Confusion indicator
        if self.confused:
            pygame.draw.line(screen, PURPLE,
                            (self.x + self.width // 2 - 5, indicator_y + 5),
                            (self.x + self.width // 2 + 5, indicator_y + 5), 2)
            pygame.draw.line(screen, PURPLE,
                            (self.x + self.width // 2, indicator_y),
                            (self.x + self.width // 2, indicator_y + 10), 2)
            indicator_y -= indicator_spacing

    def get_rect(self):
        """
        Get the player's rectangle for collision detection.

        Returns:
            Pygame Rect object
        """
        return self.rect

    def is_interacting(self):
        """
        Check if the player is currently interacting.

        Returns:
            Boolean indicating if the player is interacting
        """
        return self.interacting
