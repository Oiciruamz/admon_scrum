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

class PMBOKPlanningActivity:
    """
    Actividad educativa para la sala de Planificación PMBOK.
    El jugador debe organizar tareas en un cronograma semanal.
    """
    def __init__(self):
        self.active = False
        self.completed = False
        self.show_result = False
        self.result_message = ""
        self.result_color = GREEN
        self.feedback_active = False
        self.feedback_button_rect = None
        self.error_count = 0  # Contador de errores
        self.max_errors = 3   # Número máximo de errores permitidos
        self.failed = False   # Flag para indicar si la actividad ha fallado (game over)

        # Fuentes (aumentadas un 25%)
        self.font_title = pygame.font.Font(None, 25)  # Antes 20
        self.font_medium = pygame.font.Font(None, 24)  # Antes 19
        self.font_small = pygame.font.Font(None, 21)  # Antes 17

        # Definición de semanas para el cronograma
        self.semanas = [
            "7 Abril - 13 Abril",
            "14 Abril - 20 Abril",
            "21 Abril - 27 Abril",
            "28 Abril - 4 Mayo",
            "5 Mayo - 11 Mayo"
        ]

        # Tareas a organizar con sus fechas correctas
        self.tareas = [
            {
                "id": 1,
                "nombre": "Diseño del mapa y dinámicas",
                "fase": "Diseño", 
                "semana_correcta": 0,  # Primera semana
                "rect": None,
                "dragging": False,
                "colocada": False,
                "celda_actual": None
            },
            {
                "id": 2,
                "nombre": "Menú y sala principal",
                "fase": "Diseño",
                "semana_correcta": 1,  # Segunda semana
                "rect": None, 
                "dragging": False,
                "colocada": False,
                "celda_actual": None
            },
            {
                "id": 3,
                "nombre": "Desarrollo Niveles",
                "fase": "Programación",
                "semana_correcta": 1,  # Segunda semana
                "rect": None,
                "dragging": False,
                "colocada": False,
                "celda_actual": None
            },
            {
                "id": 4,
                "nombre": "Animaciones y colisiones",
                "fase": "Programación",
                "semana_correcta": 2,  # Tercera semana
                "rect": None,
                "dragging": False,
                "colocada": False,
                "celda_actual": None
            },
            {
                "id": 5,
                "nombre": "Diseño Retos",
                "fase": "Retos",
                "semana_correcta": 3,  # Cuarta semana
                "rect": None,
                "dragging": False,
                "colocada": False,
                "celda_actual": None
            }
        ]

        # Definición del panel principal y áreas
        self.panel_width = int(WINDOW_WIDTH * 0.75)
        self.panel_height = int(WINDOW_HEIGHT * 0.85)  # Aumentado para más espacio
        self.panel_x = (WINDOW_WIDTH - self.panel_width) // 2
        self.panel_y = (WINDOW_HEIGHT - self.panel_height) // 2

        # Área del cronograma
        self.cronograma_width = int(self.panel_width * 0.65)
        self.cronograma_height = int(self.panel_height * 0.65)  # Aumentada considerablemente
        self.cronograma_x = self.panel_x + 20
        self.cronograma_y = self.panel_y + 120  # Más separación del título

        # Área de tareas disponibles
        self.tareas_panel_x = self.cronograma_x + self.cronograma_width + 20
        self.tareas_panel_y = self.cronograma_y
        self.tareas_panel_width = self.panel_width - self.cronograma_width - 60
        self.tareas_panel_height = self.cronograma_height

        # Celdas del cronograma (filas: fases, columnas: semanas)
        self.celdas = []
        self.fases = [
            "Diseño",
            "Programación",
            "Retos"
        ]
        
        self._init_celdas()
        self._init_tareas()

    def _init_celdas(self):
        """Inicializa la matriz de celdas para el cronograma."""
        self.celdas = []
        celda_width = self.cronograma_width // len(self.semanas)
        celda_height = self.cronograma_height // len(self.fases)
        
        # Crear matriz de celdas (filas: fases, columnas: semanas)
        for i, fase in enumerate(self.fases):
            fila = []
            for j, semana in enumerate(self.semanas):
                celda = {
                    "rect": pygame.Rect(
                        self.cronograma_x + j * celda_width,
                        self.cronograma_y + i * celda_height,
                        celda_width,
                        celda_height
                    ),
                    "fase": fase,
                    "semana": j,
                    "ocupada": False,
                    "tarea_id": None
                }
                fila.append(celda)
            self.celdas.append(fila)

    def _init_tareas(self):
        """Inicializa las tareas disponibles en el panel lateral."""
        # Dimensiones de las tarjetas de tareas
        card_width = self.tareas_panel_width - 20
        card_height = 45  # Reducido desde 50
        card_margin = 6   # Reducido espacio entre tarjetas
        
        # Posicionar cada tarea en el panel lateral
        for i, tarea in enumerate(self.tareas):
            x = self.tareas_panel_x + 10
            y = self.tareas_panel_y + 40 + i * (card_height + card_margin)
            tarea["rect"] = pygame.Rect(x, y, card_width, card_height)

    def activate(self):
        """Activa la actividad."""
        self.active = True
        self.completed = False
        self.show_result = False
        self.feedback_active = False
        self.error_count = 0  # Reiniciar contador de errores
        self.failed = False   # Reiniciar estado de fallo
        
        # Reiniciar el estado de las tareas
        for tarea in self.tareas:
            tarea["dragging"] = False
            tarea["colocada"] = False
            tarea["celda_actual"] = None
        
        # Reiniciar el estado de las celdas
        for fila in self.celdas:
            for celda in fila:
                celda["ocupada"] = False
                celda["tarea_id"] = None
                
        # Reposicionar las tareas en el panel lateral
        self._init_tareas()

    def deactivate(self):
        """Desactiva la actividad."""
        self.active = False

    def handle_event(self, event):
        """Maneja los eventos de la actividad."""
        if not self.active:
            return

        # Si hay un resultado mostrándose (éxito o error)
        if self.show_result:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Botón de resultado (aceptar)
                if hasattr(self, 'result_button_rect') and self.result_button_rect.collidepoint(mouse_pos):
                    if self.completed:
                        # Si completó exitosamente, cerrar la actividad
                        self.deactivate()
                    elif self.failed:
                        # Si falló definitivamente, no hacer nada (el game over se activará en la actualización)
                        pass
                    else:
                        # Si es un error pero aún tiene intentos, cerrar el mensaje y continuar
                        self.show_result = False
                        
                    return
                    
            return  # Ignorar otros eventos mientras se muestra un resultado

        # Manejar eventos cuando se muestra feedback
        if self.feedback_active and hasattr(self, 'feedback_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.feedback_button_rect.collidepoint(event.pos):
                    self.feedback_active = False
                    return

        # Arrastrar y soltar tareas - MOVIDO ANTES de la detección de botones para dar prioridad
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                mouse_pos = event.pos
                # Verificar primero si se hizo clic en alguna tarea
                for tarea in self.tareas:
                    if tarea["rect"].collidepoint(mouse_pos):
                        tarea["dragging"] = True
                        # Guardar el offset para un arrastre más natural
                        self.drag_offset_x = mouse_pos[0] - tarea["rect"].x
                        self.drag_offset_y = mouse_pos[1] - tarea["rect"].y
                        return  # Importante: salir de la función si se seleccionó una tarea
                
                # Si no se seleccionó ninguna tarea, LUEGO verificar botones
                
                # Si se presiona el botón de cerrar manual
                if hasattr(self, 'manual_close_rect') and self.manual_close_rect.collidepoint(mouse_pos):
                    self.deactivate()
                    return
    
                # Verificar si se presiona el botón de verificación
                if hasattr(self, 'verify_button_rect') and self.verify_button_rect.collidepoint(mouse_pos):
                    self._verificar_cronograma()
                    return
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Liberación de clic izquierdo
                for tarea in self.tareas:
                    if tarea["dragging"]:
                        tarea["dragging"] = False
                        # Verificar si la tarea se soltó sobre una celda del cronograma
                        self._check_drop_on_cell(tarea)
                        return  # Salir después de manejar la liberación de una tarea
                        
        elif event.type == pygame.MOUSEMOTION:
            for tarea in self.tareas:
                if tarea["dragging"]:
                    # Actualizar posición con el offset
                    tarea["rect"].x = event.pos[0] - self.drag_offset_x
                    tarea["rect"].y = event.pos[1] - self.drag_offset_y
                    return  # Salir después de mover una tarea

    def _verificar_cronograma(self):
        """Verifica si el cronograma está completo y correctamente organizado."""
        todas_colocadas = all(tarea["colocada"] for tarea in self.tareas)
        
        if todas_colocadas:
            # Verificar si todas están en la semana correcta
            todas_correctas = True
            for tarea in self.tareas:
                # Obtener objeto celda
                if tarea["celda_actual"] is None:
                    todas_correctas = False
                    break
                    
                # Verificar si la semana es correcta
                if tarea["celda_actual"]["semana"] != tarea["semana_correcta"]:
                    todas_correctas = False
                    break
            
            if todas_correctas:
                # Cronograma correcto, actividad completada
                self.completed = True
                self.show_result = True
                self.result_message = "¡Felicidades! Has completado correctamente el cronograma del proyecto."
                self.result_color = GREEN
            else:
                # Cronograma incorrecto, mostrar mensaje de error
                self.error_count += 1
                self.show_result = True
                
                if self.error_count >= self.max_errors:
                    # Si alcanza el máximo de errores, activar game over
                    self.failed = True
                    self.result_message = f"Has cometido demasiados errores. ¡Game Over!"
                    self.result_color = RED
                else:
                    # Mostrar mensaje de error con intentos restantes
                    remaining = self.max_errors - self.error_count
                    self.result_message = f"El cronograma no es correcto. Revisa la organización temporal de las tareas. Te quedan {remaining} {'intento' if remaining == 1 else 'intentos'}."
                    self.result_color = RED
        else:
            self.show_result = True
            self.result_message = "Debes colocar todas las tareas en el cronograma antes de verificar."
            self.result_color = YELLOW

    def _reset_tarea_position(self, tarea):
        """Devuelve una tarea a su posición original en el panel lateral."""
        card_height = 45  # Actualizado a 40 (antes 50)
        card_margin = 6   # Actualizado a 6 (antes 8)
        idx = next(i for i, t in enumerate(self.tareas) if t["id"] == tarea["id"])
        
        tarea["rect"].x = self.tareas_panel_x + 10
        tarea["rect"].y = self.tareas_panel_y + 40 + idx * (card_height + card_margin)
        tarea["colocada"] = False
        tarea["celda_actual"] = None

    def _get_fase_index(self, fase_nombre):
        """Devuelve el índice de una fase según su nombre."""
        for i, fase in enumerate(self.fases):
            if fase == fase_nombre:
                return i
        return -1  # Si no se encuentra la fase

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
        title_text = self.font_title.render("Planificación del Proyecto", True, WHITE)
        title_rect = title_text.get_rect(center=(self.panel_x + self.panel_width // 2, self.panel_y + 30))
        screen.blit(title_text, title_rect)
        
        # Panel del cronograma
        pygame.draw.rect(screen, CHARCOAL, 
                         (self.cronograma_x, self.cronograma_y, self.cronograma_width, self.cronograma_height))
        pygame.draw.rect(screen, LIGHT_GRAY, 
                         (self.cronograma_x, self.cronograma_y, self.cronograma_width, self.cronograma_height), 2)
        
        # Panel de tareas disponibles
        pygame.draw.rect(screen, CHARCOAL, 
                         (self.tareas_panel_x, self.tareas_panel_y, self.tareas_panel_width, self.tareas_panel_height))
        pygame.draw.rect(screen, LIGHT_GRAY, 
                         (self.tareas_panel_x, self.tareas_panel_y, self.tareas_panel_width, self.tareas_panel_height), 2)
        
        # Título del panel de tareas
        tareas_title = self.font_medium.render("Tareas", True, WHITE)
        tareas_title_rect = tareas_title.get_rect(
            center=(self.tareas_panel_x + self.tareas_panel_width // 2, self.tareas_panel_y + 20))
        screen.blit(tareas_title, tareas_title_rect)
        
        # Dibujar cabeceras de semanas
        celda_width = self.cronograma_width // len(self.semanas)
        for i, semana in enumerate(self.semanas):
            # Fondo para cabecera
            header_rect = pygame.Rect(
                self.cronograma_x + i * celda_width, 
                self.cronograma_y - 25, 
                celda_width, 
                25
            )
            pygame.draw.rect(screen, DARK_BLUE, header_rect)
            pygame.draw.rect(screen, LIGHT_BLUE, header_rect, 1)
            
            # Texto de semana (posiblemente ajustado si es largo)
            semana_font = pygame.font.Font(None, 13)  # Aumentado de 10 a 13
            semana_text = semana_font.render(semana, True, WHITE)
            semana_rect = semana_text.get_rect(center=header_rect.center)
            screen.blit(semana_text, semana_rect)
        
        # Dibujar cabeceras de fases (más pequeñas)
        celda_height = self.cronograma_height // len(self.fases)
        for i, fase in enumerate(self.fases):
            # Fondo para cabecera - ancho reducido a 50
            header_rect = pygame.Rect(
                self.cronograma_x - 50, 
                self.cronograma_y + i * celda_height, 
                50, 
                celda_height
            )
            pygame.draw.rect(screen, DARK_BLUE, header_rect)
            pygame.draw.rect(screen, LIGHT_BLUE, header_rect, 1)
            
            # Texto de fase con fuente más pequeña
            fase_font = pygame.font.Font(None, 13)  # Aumentado de 10 a 13
            fase_text = fase_font.render(fase, True, WHITE)
            fase_rect = fase_text.get_rect(center=header_rect.center)
            screen.blit(fase_text, fase_rect)
        
        # Dibujar celdas del cronograma
        for fila in self.celdas:
            for celda in fila:
                pygame.draw.rect(screen, GRAY, celda["rect"], 1)
                
        # Dibujar tareas
        for tarea in self.tareas:
            # Color de fondo según la fase
            if tarea["fase"] == "Diseño":
                color = (70, 130, 180)  # Azul acero
            elif tarea["fase"] == "Programación":
                color = (60, 179, 113)  # Verde medio
            else:  # Retos
                color = (205, 92, 92)   # Rojo indio
                
            # Dibujar tarjeta de tarea
            pygame.draw.rect(screen, color, tarea["rect"], border_radius=3)  # Reducido radio de borde
            pygame.draw.rect(screen, WHITE, tarea["rect"], 1, border_radius=3)  # Borde más delgado
            
            # Dibujar texto de la tarea con fuente más pequeña
            nombre_font = pygame.font.Font(None, 13)  # Aumentado de 10 a 13
            nombre_text = nombre_font.render(tarea["nombre"], True, WHITE)
            # Ajustar posición para tarjetas más pequeñas
            nombre_rect = nombre_text.get_rect(center=(tarea["rect"].centerx, tarea["rect"].y + 12))
            screen.blit(nombre_text, nombre_rect)
            
            # Dibujar fase de la tarea con fuente más pequeña
            fase_font = pygame.font.Font(None, 11)  # Aumentado de 9 a 11
            fase_text = fase_font.render(tarea["fase"], True, WHITE)
            fase_rect = fase_text.get_rect(center=(tarea["rect"].centerx, tarea["rect"].y + 28))
            screen.blit(fase_text, fase_rect)
            
        # Botón de verificación
        verify_button_width = 150
        verify_button_height = 40
        verify_button_x = self.panel_x + (self.panel_width - verify_button_width) // 2
        verify_button_y = self.panel_y + self.panel_height - 50
        self.verify_button_rect = pygame.Rect(verify_button_x, verify_button_y, verify_button_width, verify_button_height)
        
        pygame.draw.rect(screen, DARK_GREEN, self.verify_button_rect, border_radius=10)
        pygame.draw.rect(screen, GREEN, self.verify_button_rect, 2, border_radius=10)
        
        verify_text = self.font_medium.render("Verificar", True, WHITE)
        verify_text_rect = verify_text.get_rect(center=self.verify_button_rect.center)
        screen.blit(verify_text, verify_text_rect)
        
        # Botón de cerrar
        close_btn_width = 90
        close_btn_height = 30
        close_btn_x = self.panel_x + self.panel_width - 100
        close_btn_y = self.panel_y + 10
        self.manual_close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_width, close_btn_height)
        
        pygame.draw.rect(screen, DARK_GRAY, self.manual_close_rect, border_radius=5)
        pygame.draw.rect(screen, LIGHT_GRAY, self.manual_close_rect, 2, border_radius=5)
        
        close_text = self.font_small.render("Cerrar", True, WHITE)
        close_text_rect = close_text.get_rect(center=self.manual_close_rect.center)
        screen.blit(close_text, close_text_rect)
        
        # Mostrar mensaje de resultado si es necesario
        if self.show_result:
            self._render_result_modal(screen)
            
        # Mostrar feedback si hay error
        if self.feedback_active:
            self._render_feedback_modal(screen)
            
    def _render_result_modal(self, screen):
        """Renderiza el modal de resultado final."""
        # Fondo oscurecido
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Negro semitransparente
        screen.blit(overlay, (0, 0))
        
        # Dimensiones del modal
        modal_width = 400
        modal_height = 200
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Fondo del modal con efecto degradado según resultado
        if self.completed:
            color_top = (20, 60, 20)  # Verde oscuro
            color_bottom = (30, 80, 30)  # Verde un poco más claro
            text_color = (200, 255, 200)  # Verde claro
        elif self.failed:
            color_top = (60, 20, 20)  # Rojo oscuro
            color_bottom = (80, 30, 30)  # Rojo un poco más claro
            text_color = (255, 200, 200)  # Rojo claro
        else:
            color_top = (60, 60, 20)  # Naranja oscuro
            color_bottom = (80, 80, 30)  # Naranja un poco más claro
            text_color = (255, 255, 200)  # Naranja claro
        
        # Dibujar el panel con degradado
        for i in range(modal_height):
            progress = i / modal_height
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * progress)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * progress)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * progress)
            pygame.draw.line(screen, (r, g, b), (modal_x, modal_y + i), (modal_x + modal_width, modal_y + i))
        
        # Borde del modal
        pygame.draw.rect(screen, self.result_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=10)
        
        # Título con efecto de sombra
        title = "¡ÉXITO!" if self.completed else "¡GAME OVER!" if self.failed else "ERROR"
        title_shadow = self.font_title.render(title, True, (0, 0, 0))
        title_text = self.font_title.render(title, True, self.result_color)
        
        # Dibujar sombra y luego texto
        screen.blit(title_shadow, (modal_x + modal_width // 2 - title_shadow.get_width() // 2 + 2, modal_y + 30 + 2))
        screen.blit(title_text, (modal_x + modal_width // 2 - title_text.get_width() // 2, modal_y + 30))
        
        # Mensaje de resultado con wrapping
        wrapped_lines = self._wrap_text(self.result_message, self.font_small, modal_width - 60)
        for i, line in enumerate(wrapped_lines):
            line_text = self.font_small.render(line, True, text_color)
            line_rect = line_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 80 + i * 25))
            screen.blit(line_text, line_rect)
        
        # Botón
        if not self.failed:  # No mostrar botón en caso de Game Over
            button_rect = pygame.Rect(modal_x + modal_width // 2 - 50, modal_y + modal_height - 50, 100, 30)
            pygame.draw.rect(screen, self.result_color, button_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=5)
            
            button_text = self.font_small.render("Aceptar", True, WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, button_text_rect)
            
            # Guardar referencia al rectángulo del botón
            self.result_button_rect = button_rect
        
    def _render_feedback_modal(self, screen):
        """Renderiza el modal de feedback de error."""
        modal_width = 500
        # Calcular altura basada en el texto
        lines = self._wrap_text(self.result_message, self.font_small, modal_width - 60)
        modal_height = 100 + len(lines) * 25
        
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Fondo del modal con estilo de advertencia
        pygame.draw.rect(screen, (50, 20, 20), (modal_x, modal_y, modal_width, modal_height), border_radius=15)
        pygame.draw.rect(screen, RED, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=15)
        
        # Título de error
        title_text = self.font_title.render("¡PLANIFICACIÓN INCORRECTA!", True, RED)
        title_rect = title_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 30))
        screen.blit(title_text, title_rect)
        
        # Mensaje de error
        for i, line in enumerate(lines):
            line_text = self.font_small.render(line, True, (255, 200, 200))
            line_rect = line_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 70 + i * 25))
            screen.blit(line_text, line_rect)
            
        # Botón de cerrar
        button_width = 120
        button_height = 35
        button_x = modal_x + (modal_width - button_width) // 2
        button_y = modal_y + modal_height - 50
        self.feedback_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        pygame.draw.rect(screen, (80, 20, 20), self.feedback_button_rect, border_radius=8)
        pygame.draw.rect(screen, RED, self.feedback_button_rect, 2, border_radius=8)
        
        button_text = self.font_small.render("Entendido", True, WHITE)
        button_rect = button_text.get_rect(center=self.feedback_button_rect.center)
        screen.blit(button_text, button_rect)

    def _check_drop_on_cell(self, tarea):
        """Verifica si una tarea fue soltada sobre una celda válida y la posiciona correctamente."""
        tarea_colocada = False
        
        # Crear un rectángulo ampliado para una detección más generosa
        tarea_center = tarea["rect"].center
        
        for i, fila in enumerate(self.celdas):
            for j, celda in enumerate(fila):
                # Usar un área de detección ligeramente mayor que la celda
                area_celda = celda["rect"].inflate(10, 10)
                
                if area_celda.collidepoint(tarea_center):
                    # Verificar que la fase sea correcta
                    if celda["fase"] == tarea["fase"]:
                        # Liberar celda anterior si existía
                        if tarea["celda_actual"]:
                            tarea["celda_actual"]["ocupada"] = False
                            tarea["celda_actual"]["tarea_id"] = None
                        
                        # Centrar la tarea en la celda perfectamente
                        tarea["rect"].x = celda["rect"].x + (celda["rect"].width - tarea["rect"].width) // 2
                        tarea["rect"].y = celda["rect"].y + (celda["rect"].height - tarea["rect"].height) // 2
                        
                        # Actualizar estado
                        tarea["colocada"] = True
                        tarea["celda_actual"] = celda
                        celda["ocupada"] = True
                        celda["tarea_id"] = tarea["id"]
                        
                        # Registrar la semana en la que se colocó para verificación
                        celda["semana"] = j
                        
                        tarea_colocada = True
                        return
        
        # Si no se colocó en ninguna celda válida, volver a la posición original
        if not tarea_colocada:
            # Devolver a panel lateral si no estaba previamente colocada
            if not tarea["celda_actual"]:
                self._reset_tarea_position(tarea)
            else:
                # Volver a la celda anterior
                celda = tarea["celda_actual"]
                tarea["rect"].x = celda["rect"].x + (celda["rect"].width - tarea["rect"].width) // 2
                tarea["rect"].y = celda["rect"].y + (celda["rect"].height - tarea["rect"].height) // 2 