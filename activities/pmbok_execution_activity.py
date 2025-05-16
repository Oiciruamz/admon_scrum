import pygame
import math
import random
from settings import *
from utils import draw_text, draw_panel

# Definición de colores para la actividad
# Colores básicos
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Colores adicionales
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
GRAY = (100, 100, 100)
CHARCOAL = (40, 40, 40)
DARK_BLUE = (25, 25, 112)
LIGHT_BLUE = (70, 130, 180)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)

class PMBOKExecutionActivity:
    """
    Actividad educativa para la sala de Ejecución PMBOK.
    El jugador debe relacionar cada rol de desarrollo con su función correcta.
    """
    def __init__(self):
        self.active = False
        self.completed = False
        self.show_result = False
        self.result_message = ""
        self.result_color = GREEN
        self.feedback_active = False
        self.feedback_button_rect = None
        self.errors_count = 0
        self.max_errors = 3  # Número máximo de errores antes del game over
        self.failed = False  # Flag para indicar si la actividad ha fallado (game over)

        # Fuentes (tamaño reducido pero legible)
        self.font_title = pygame.font.Font(None, 22)  # Antes 28
        self.font_medium = pygame.font.Font(None, 18)  # Antes 24
        self.font_small = pygame.font.Font(None, 16)  # Antes 20

        # Roles del equipo de desarrollo
        self.roles = [
            {
                "id": 1,
                "nombre": "Tester",
                "rect": None,
                "matched": False,
                "dragging": False
            },
            {
                "id": 2,
                "nombre": "BackEnd",
                "rect": None,
                "matched": False,
                "dragging": False
            },
            {
                "id": 3,
                "nombre": "FrontEnd",
                "rect": None,
                "matched": False,
                "dragging": False
            },
            {
                "id": 4,
                "nombre": "Líder",
                "rect": None,
                "matched": False,
                "dragging": False
            }
        ]

        # Funciones de cada rol
        self.funciones = [
            {
                "id": 1,
                "descripcion": [
                    "Definir los tipos de pruebas a realizar",
                    "Preparar entornos de prueba",
                    "Ejecutar pruebas unitarias y de integración",
                    "Identificar errores y documentarlos"
                ],
                "rol_correcto": "Tester",
                "matched": False,
                "rect": None
            },
            {
                "id": 2,
                "descripcion": [
                    "Crear Mockup de la interfaz",
                    "Mediante html, css y js crear la interfaz web",
                    "Establecer y validar rutas de conexión"
                ],
                "rol_correcto": "FrontEnd",
                "matched": False,
                "rect": None
            },
            {
                "id": 3,
                "descripcion": [
                    "Conectar backend con página web",
                    "Implementación de API para la comunicación entre sistemas",
                    "Implementar backups automáticos"
                ],
                "rol_correcto": "BackEnd",
                "matched": False,
                "rect": None
            },
            {
                "id": 4,
                "descripcion": [
                    "Definir requisitos clave y establecer visión general",
                    "Validar arquitectura y experiencia de usuario",
                    "Supervisar estructura de la base de datos"
                ],
                "rol_correcto": "Líder",
                "matched": False,
                "rect": None
            }
        ]

        # Definición del panel principal y áreas
        self.panel_width = int(WINDOW_WIDTH * 0.8)
        self.panel_height = int(WINDOW_HEIGHT * 0.85)
        self.panel_x = (WINDOW_WIDTH - self.panel_width) // 2
        self.panel_y = (WINDOW_HEIGHT - self.panel_height) // 2

        # Área de roles (izquierda)
        self.roles_panel_width = int(self.panel_width * 0.2)
        self.roles_panel_height = self.panel_height - 100
        self.roles_panel_x = self.panel_x + 30
        self.roles_panel_y = self.panel_y + 70

        # Área de funciones (derecha)
        self.funciones_panel_width = int(self.panel_width * 0.6)
        self.funciones_panel_height = self.panel_height - 100
        self.funciones_panel_x = self.roles_panel_x + self.roles_panel_width + 50
        self.funciones_panel_y = self.roles_panel_y

        self._init_layouts()

    def _init_layouts(self):
        """Inicializa las posiciones de roles y funciones."""
        # Posicionar roles verticalmente
        role_height = 75  # Aumentado de 60 a 75 para evitar overflow del icono
        role_margin = 20
        role_width = self.roles_panel_width - 20
        
        for i, rol in enumerate(self.roles):
            x = self.roles_panel_x + 10
            y = self.roles_panel_y + 40 + i * (role_height + role_margin)
            rol["rect"] = pygame.Rect(x, y, role_width, role_height)
            rol["original_pos"] = (x, y)
        
        # Posicionar funciones verticalmente
        funcion_height = 100
        funcion_margin = 15
        funcion_width = self.funciones_panel_width - 20
        
        random_indices = list(range(len(self.funciones)))
        random.shuffle(random_indices)
        
        for i, index in enumerate(random_indices):
            funcion = self.funciones[index]
            x = self.funciones_panel_x + 10
            y = self.funciones_panel_y + i * (funcion_height + funcion_margin)
            funcion["rect"] = pygame.Rect(x, y, funcion_width, funcion_height)

    def activate(self):
        """Activa la actividad."""
        self.active = True
        self.completed = False
        self.show_result = False
        self.feedback_active = False
        self.errors_count = 0
        self.failed = False  # Reiniciar el estado de fallo
        
        # Reiniciar estado de roles y funciones
        for rol in self.roles:
            rol["matched"] = False
            rol["dragging"] = False
        
        for funcion in self.funciones:
            funcion["matched"] = False
            
        # Reposicionar elementos
        self._init_layouts()

    def deactivate(self):
        """Desactiva la actividad."""
        self.active = False

    def handle_event(self, event):
        """Maneja los eventos de la actividad."""
        if not self.active:
            return

        # Manejar eventos cuando se muestra el resultado
        if self.show_result and hasattr(self, 'result_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.result_button_rect.collidepoint(event.pos):
                    if self.completed:
                        self.deactivate()
                    elif self.failed:
                        # No hacer nada, el game over se activará en la próxima actualización
                        pass
                    else:
                        self.show_result = False
                    return
            return  # Ignorar otros eventos mientras se muestra un resultado

        # Manejar eventos cuando se muestra feedback
        if self.feedback_active and hasattr(self, 'feedback_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.feedback_button_rect.collidepoint(event.pos):
                    self.feedback_active = False
                    
                    # Verificar si se completó la actividad después de cerrar el feedback
                    if self.completed:
                        self.show_result = True
                        self.result_message = "¡Excelente! Has relacionado correctamente todos los roles con sus funciones."
                        self.result_color = GREEN
                    return
            return  # Ignorar otros eventos mientras se muestra feedback

        # Si se presiona el botón de cerrar manual
        if hasattr(self, 'manual_close_rect') and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.manual_close_rect.collidepoint(event.pos):
                self.deactivate()
                return

        # Arrastrar y soltar roles
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                for rol in self.roles:
                    if rol["rect"].collidepoint(event.pos) and not rol["matched"]:
                        rol["dragging"] = True
                        # Guardar el offset para un arrastre más natural
                        self.drag_offset_x = event.pos[0] - rol["rect"].x
                        self.drag_offset_y = event.pos[1] - rol["rect"].y
                        break  # Solo arrastrar un rol a la vez
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Liberación de clic izquierdo
                for rol in self.roles:
                    if rol["dragging"]:
                        rol["dragging"] = False
                        # Verificar si el rol se soltó sobre una función
                        self._check_role_drop(rol)
                        
        elif event.type == pygame.MOUSEMOTION:
            for rol in self.roles:
                if rol["dragging"]:
                    # Actualizar posición con el offset
                    rol["rect"].x = event.pos[0] - self.drag_offset_x
                    rol["rect"].y = event.pos[1] - self.drag_offset_y

    def _check_role_drop(self, rol):
        """Verificar si un rol ha sido colocado sobre una función y si es correcto."""
        for funcion in self.funciones:
            if funcion["matched"]:
                continue  # Saltar funciones ya emparejadas
                
            # Verificar si el rol está sobre una función
            if funcion["rect"].colliderect(rol["rect"]):
                # Comprobar si el emparejamiento es correcto
                if funcion["rol_correcto"] == rol["nombre"]:
                    # Emparejamiento correcto
                    funcion["matched"] = True
                    rol["matched"] = True
                    
                    # Posicionar el rol correctamente sobre la función
                    rol["rect"].x = funcion["rect"].x + funcion["rect"].width - rol["rect"].width - 20
                    rol["rect"].y = funcion["rect"].y + 10
                    
                    # Verificar si se han emparejado todos los roles
                    if all(r["matched"] for r in self.roles):
                        self.completed = True
                        # No mostrar el resultado aquí, solo activar el feedback de éxito
                        self.feedback_active = True
                        self.result_message = f"¡Correcto! Has emparejado el rol de {rol['nombre']} con su función correspondiente. ¡Has completado todos los emparejamientos!"
                        self.result_color = GREEN
                    else:
                        # Mostrar feedback de éxito para este emparejamiento
                        self.feedback_active = True
                        self.result_message = f"¡Correcto! Has emparejado el rol de {rol['nombre']} con su función correspondiente."
                        self.result_color = GREEN
                else:
                    # Emparejamiento incorrecto
                    self.errors_count += 1
                    self.feedback_active = True
                    
                    # Reposicionar el rol a su posición original
                    rol["rect"].x = rol["original_pos"][0]
                    rol["rect"].y = rol["original_pos"][1]
                    
                    # Verificar si ha alcanzado el límite de errores
                    if self.errors_count >= self.max_errors:
                        self.failed = True
                        self.result_message = f"¡Has cometido demasiados errores! Game Over."
                        self.result_color = RED
                        self.show_result = True
                    else:
                        # Todavía tiene intentos
                        remaining = self.max_errors - self.errors_count
                        self.result_message = f"Incorrecto. El rol de {rol['nombre']} no corresponde a esta función. Te quedan {remaining} {'intento' if remaining == 1 else 'intentos'}."
                        self.result_color = RED
                
                return True
                
        return False

    def _wrap_text(self, text, font, max_width):
        """Divide un texto en líneas para que quepa en un ancho máximo."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Si ni siquiera una palabra cabe, la cortamos
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

    def render(self, screen):
        """Renderiza la actividad en pantalla."""
        if not self.active:
            return
            
        # Fondo semitransparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Panel principal
        draw_panel(screen, self.panel_x, self.panel_y, self.panel_width, self.panel_height, 
                   DARK_GRAY, WHITE, 3, 15)
        
        # Título
        title_text = self.font_title.render("Roles y Funciones en el Equipo de Desarrollo", True, WHITE)
        title_rect = title_text.get_rect(center=(self.panel_x + self.panel_width // 2, self.panel_y + 30))
        screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_small.render("Arrastra cada rol hacia sus funciones correspondientes", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(self.panel_x + self.panel_width // 2, self.panel_y + 55))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Panel de roles (izquierda)
        pygame.draw.rect(screen, CHARCOAL, 
                         (self.roles_panel_x, self.roles_panel_y, self.roles_panel_width, self.roles_panel_height))
        pygame.draw.rect(screen, LIGHT_GRAY, 
                         (self.roles_panel_x, self.roles_panel_y, self.roles_panel_width, self.roles_panel_height), 2)
        
        # Título del panel de roles
        roles_title = self.font_medium.render("Roles", True, WHITE)
        roles_title_rect = roles_title.get_rect(
            center=(self.roles_panel_x + self.roles_panel_width // 2, self.roles_panel_y + 20))
        screen.blit(roles_title, roles_title_rect)
        
        # Panel de funciones (derecha)
        pygame.draw.rect(screen, CHARCOAL, 
                         (self.funciones_panel_x, self.funciones_panel_y, self.funciones_panel_width, self.funciones_panel_height))
        pygame.draw.rect(screen, LIGHT_GRAY, 
                         (self.funciones_panel_x, self.funciones_panel_y, self.funciones_panel_width, self.funciones_panel_height), 2)
        
        # Título del panel de funciones
        funciones_title = self.font_medium.render("Funciones", True, WHITE)
        funciones_title_rect = funciones_title.get_rect(
            center=(self.funciones_panel_x + self.funciones_panel_width // 2, self.funciones_panel_y + 20))
        screen.blit(funciones_title, funciones_title_rect)
        
        # Dibujar funciones
        for funcion in self.funciones:
            # Color de fondo según si está emparejada o no
            color = DARK_GREEN if funcion["matched"] else DARK_BLUE
            border_color = GREEN if funcion["matched"] else LIGHT_BLUE
            
            # Dibujar rectángulo de función
            pygame.draw.rect(screen, color, funcion["rect"], border_radius=5)
            pygame.draw.rect(screen, border_color, funcion["rect"], 2, border_radius=5)
            
            # Dibujar descripción de la función
            y_offset = 15
            for i, linea in enumerate(funcion["descripcion"]):
                item_text = self.font_small.render(f"• {linea}", True, WHITE)
                item_rect = item_text.get_rect(
                    x=funcion["rect"].x + 15,
                    y=funcion["rect"].y + y_offset + i * 20
                )
                screen.blit(item_text, item_rect)
        
        # Dibujar roles
        for rol in self.roles:
            # No dibujar si ya está emparejado y completo
            if rol["matched"]:
                # Dibujar un icono de persona simple
                icon_rect = pygame.Rect(
                    rol["rect"].x,
                    rol["rect"].y,
                    rol["rect"].width,
                    rol["rect"].height
                )
                pygame.draw.rect(screen, LIGHT_BLUE, icon_rect, border_radius=10)
                pygame.draw.rect(screen, WHITE, icon_rect, 2, border_radius=10)
                
                # Dibujar icono de persona
                # Círculo para la cabeza
                head_radius = 7
                head_center = (icon_rect.centerx, icon_rect.y + 25)
                pygame.draw.circle(screen, WHITE, head_center, head_radius)
                
                # Rectángulo para el cuerpo
                body_rect = pygame.Rect(
                    icon_rect.centerx - 7,
                    head_center[1] + head_radius,
                    14,
                    14
                )
                pygame.draw.rect(screen, WHITE, body_rect, border_radius=3)
                
                # Nombre del rol
                name_text = self.font_medium.render(rol["nombre"], True, WHITE)
                name_rect = name_text.get_rect(center=(icon_rect.centerx, icon_rect.bottom - 18))
                screen.blit(name_text, name_rect)
            else:
                # Color normal para roles no emparejados
                color = LIGHT_BLUE
                
                # Dibujar tarjeta de rol
                pygame.draw.rect(screen, color, rol["rect"], border_radius=10)
                pygame.draw.rect(screen, WHITE, rol["rect"], 2, border_radius=10)
                
                # Dibujar icono de persona
                # Círculo para la cabeza
                head_radius = 7
                head_center = (rol["rect"].centerx, rol["rect"].y + 25)
                pygame.draw.circle(screen, WHITE, head_center, head_radius)
                
                # Rectángulo para el cuerpo
                body_rect = pygame.Rect(
                    rol["rect"].centerx - 7,
                    head_center[1] + head_radius,
                    14,
                    14
                )
                pygame.draw.rect(screen, WHITE, body_rect, border_radius=3)
                
                # Nombre del rol
                name_text = self.font_medium.render(rol["nombre"], True, WHITE)
                name_rect = name_text.get_rect(center=(rol["rect"].centerx, rol["rect"].bottom - 18))
                screen.blit(name_text, name_rect)
        
        # Contador de errores
        if self.errors_count > 0:
            error_text = self.font_small.render(f"Errores: {self.errors_count}/{self.max_errors}", True, ORANGE)
            error_rect = error_text.get_rect(
                topright=(self.panel_x + self.panel_width - 20, self.panel_y + 20)
            )
            screen.blit(error_text, error_rect)
            
        # Botón de cerrar
        close_btn_width = 70
        close_btn_height = 25
        close_btn_x = self.panel_x + self.panel_width - 80
        close_btn_y = self.panel_y + 10
        self.manual_close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_width, close_btn_height)
        
        pygame.draw.rect(screen, DARK_GRAY, self.manual_close_rect, border_radius=5)
        pygame.draw.rect(screen, LIGHT_GRAY, self.manual_close_rect, 2, border_radius=5)
        
        close_text = pygame.font.Font(None, 14).render("Cerrar", True, WHITE)  # Fuente reducida usando Font directamente
        close_text_rect = close_text.get_rect(center=self.manual_close_rect.center)
        screen.blit(close_text, close_text_rect)
        
        # Mostrar mensaje de resultado si es necesario
        if self.show_result:
            self._render_result_modal(screen)
            
        # Mostrar feedback si hay error
        if self.feedback_active:
            self._render_feedback_modal(screen)
    
    def _render_result_modal(self, screen):
        """Renderiza el modal de resultado."""
        # Fondo oscurecido para destacar el modal
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Negro semitransparente
        screen.blit(overlay, (0, 0))
        
        # Modal con dimensiones fijas
        modal_width = 400
        modal_height = 200
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Fondo del modal según resultado
        if self.completed:
            bg_color = (20, 60, 30)  # Verde oscuro
        elif self.failed:
            bg_color = (60, 20, 20)  # Rojo oscuro
        else:
            bg_color = (60, 50, 20)  # Naranja oscuro
            
        # Dibujar el panel principal
        pygame.draw.rect(screen, bg_color, (modal_x, modal_y, modal_width, modal_height), border_radius=15)
        pygame.draw.rect(screen, self.result_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=15)
        
        # Título con efecto de sombra
        title = "¡ÉXITO!" if self.completed else "¡GAME OVER!" if self.failed else "ERROR"
        title_shadow = self.font_title.render(title, True, (0, 0, 0))
        title_text = self.font_title.render(title, True, self.result_color)
        
        # Dibujar sombra y luego texto
        screen.blit(title_shadow, (modal_x + modal_width // 2 - title_shadow.get_width() // 2 + 2, modal_y + 30 + 2))
        screen.blit(title_text, (modal_x + modal_width // 2 - title_text.get_width() // 2, modal_y + 30))
        
        # Mensaje wrapeado
        text_color = (220, 255, 220) if self.completed else (255, 220, 220) if self.failed else (255, 255, 220)
        wrapped_lines = self._wrap_text(self.result_message, self.font_medium, modal_width - 60)
        
        for i, line in enumerate(wrapped_lines):
            line_text = self.font_medium.render(line, True, text_color)
            line_rect = line_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 70 + i * 25))
            screen.blit(line_text, line_rect)
        
        # Botón (solo si no es game over)
        if not self.failed:
            button_width = 100
            button_height = 30
            button_x = modal_x + (modal_width - button_width) // 2
            button_y = modal_y + modal_height - 50
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(screen, self.result_color, button_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=10)
            
            button_text = self.font_medium.render("Aceptar", True, WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, button_text_rect)
            
            # Guardar referencia al botón
            self.result_button_rect = button_rect
    
    def _render_feedback_modal(self, screen):
        """Renderiza el modal de feedback."""
        modal_width = 400
        modal_height = 150
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Determinar si el feedback es positivo o negativo
        is_correct = self.result_color == GREEN
        
        # Fondo del modal según el tipo de feedback
        if is_correct:
            # Estilo para feedback positivo (verde)
            bg_color = (20, 50, 20)  # Verde oscuro
            border_color = GREEN
            text_color = (200, 255, 200)  # Verde claro
            title = "¡CORRECTO!"
        else:
            # Estilo para feedback negativo (rojo/naranja)
            bg_color = (50, 20, 20)  # Rojo oscuro
            border_color = ORANGE
            text_color = (255, 200, 200)  # Rojo claro
            title = "INCORRECTO"
        
        # Dibujar el panel principal
        pygame.draw.rect(screen, bg_color, (modal_x, modal_y, modal_width, modal_height), border_radius=15)
        pygame.draw.rect(screen, border_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=15)
        
        # Título 
        title_text = self.font_title.render(title, True, border_color)
        title_rect = title_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 30))
        screen.blit(title_text, title_rect)
        
        # Mensaje 
        lines = self._wrap_text(self.result_message, self.font_small, modal_width - 40)
        for i, line in enumerate(lines):
            line_text = self.font_small.render(line, True, text_color)
            line_rect = line_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 70 + i * 25))
            screen.blit(line_text, line_rect)
            
        # Botón de cerrar
        button_width = 70
        button_height = 25
        button_x = modal_x + (modal_width - button_width) // 2
        button_y = modal_y + modal_height - 30
        self.feedback_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Color del botón según el tipo de feedback
        button_bg_color = (30, 70, 30) if is_correct else (80, 20, 20)
        
        pygame.draw.rect(screen, button_bg_color, self.feedback_button_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.feedback_button_rect, 2, border_radius=8)
        
        button_text = pygame.font.Font(None, 14).render("Entendido", True, WHITE)
        button_rect = button_text.get_rect(center=self.feedback_button_rect.center)
        screen.blit(button_text, button_rect) 