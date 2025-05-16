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
BEIGE = (245, 245, 220)  # Color para las notas de papel

class PMBOKClosingActivity:
    """
    Actividad educativa para la sala de Cierre PMBOK.
    El jugador debe responder preguntas de múltiple opción sobre gestión de proyectos.
    """
    def __init__(self, game_instance=None):
        self.active = False
        self.completed = False
        self.show_result = False
        self.result_message = ""
        self.result_color = GREEN
        self.feedback_active = False
        self.feedback_button_rect = None
        self.current_question = 0
        self.correct_answers = 0
        self.errors_count = 0
        self.max_errors = 3  # Número máximo de errores antes del game over
        self.failed = False  # Flag para indicar si la actividad ha fallado (game over)
        self.game = game_instance  # Referencia al juego para poder cambiar el estado

        # Fuentes (tamaño reducido pero legible)
        self.font_title = pygame.font.Font(None, 22)
        self.font_medium = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)

        # Preguntas y respuestas (basadas en las imágenes mostradas)
        self.questions = [
            {
                "text": "Tenemos un retraso en el desarrollo del backend debido a complejidad técnica, ¿Qué hacemos?",
                "options": [
                    "Realizar pruebas de usabilidad y recopilar feedback de los usuarios para más mejoras",
                    "Usar servidores con redundancia y monitoreo constante",
                    "Establecer hitos claros, realizar revisiones constantes y asignar recursos adicionales si es necesario"
                ],
                "correct": 2,  # Índice de la respuesta correcta (0-indexed)
                "answered": False,
                "selected": None
            },
            {
                "text": "Tenemos un fallo en los servidores que afectan a la disponibilidad del sistema, ¿Qué hacemos?",
                "options": [
                    "Realizar pruebas de usabilidad y recopilar feedback de los usuarios para más mejoras",
                    "Usar servidores con redundancia y monitoreo constante",
                    "Establecer hitos claros, realizar revisiones constantes y asignar recursos adicionales si es necesario"
                ],
                "correct": 1,  # Índice de la respuesta correcta
                "answered": False,
                "selected": None
            },
            {
                "text": "Nos hemos excedido de presupuesto, ¿Qué hacemos?",
                "options": [
                    "Hacer seguimiento financiero periódico y ajustar costos según sea necesario",
                    "Usar servidores con redundancia y monitoreo constante",
                    "Establecer hitos claros, realizar revisiones constantes y asignar recursos adicionales si es necesario"
                ],
                "correct": 0,  # Índice de la respuesta correcta
                "answered": False,
                "selected": None
            }
        ]

        # Definición del panel principal y áreas
        self.panel_width = int(WINDOW_WIDTH * 0.8)
        self.panel_height = int(WINDOW_HEIGHT * 0.85)
        self.panel_x = (WINDOW_WIDTH - self.panel_width) // 2
        self.panel_y = (WINDOW_HEIGHT - self.panel_height) // 2

        # Área de la pregunta
        self.question_panel_width = int(self.panel_width * 0.8)
        self.question_panel_height = 120
        self.question_panel_x = self.panel_x + (self.panel_width - self.question_panel_width) // 2
        self.question_panel_y = self.panel_y + 60

        # Área de opciones
        self.options_area_width = self.panel_width - 80
        self.options_area_height = self.panel_height - self.question_panel_height - 150
        self.options_area_x = self.panel_x + 40
        self.options_area_y = self.question_panel_y + self.question_panel_height + 20

        # Dimensiones de cada opción
        self.option_width = int(self.options_area_width * 0.9)
        self.option_height = int(self.options_area_height / 3) - 20
        
        # Inicializar los rectángulos de las opciones
        self.option_rects = []

    def _init_options(self):
        """Inicializa los rectángulos para las opciones de respuesta."""
        self.option_rects = []
        
        # Crear rectángulos para cada opción
        for i in range(3):
            option_x = self.options_area_x + (self.options_area_width - self.option_width) // 2
            option_y = self.options_area_y + i * (self.option_height + 20)
            
            rect = pygame.Rect(option_x, option_y, self.option_width, self.option_height)
            self.option_rects.append(rect)

    def activate(self):
        """Activa la actividad."""
        self.active = True
        self.completed = False
        self.show_result = False
        self.feedback_active = False
        self.current_question = 0
        self.correct_answers = 0
        self.errors_count = 0
        self.failed = False  # Reiniciar el estado de fallo
        
        # Reiniciar el estado de las preguntas
        for question in self.questions:
            question["answered"] = False
            question["selected"] = None
            
        # Inicializar las opciones
        self._init_options()

    def deactivate(self):
        """Desactiva la actividad."""
        self.active = False

    def _next_question(self):
        """Avanza a la siguiente pregunta."""
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            return True
        else:
            # No hay más preguntas, la actividad está completa
            self.completed = True
            self.show_result = True
            
            # Mensaje según el número de respuestas correctas
            if self.correct_answers == len(self.questions):
                self.result_message = "¡Excelente! Has respondido correctamente todas las preguntas. Has completado el juego con éxito."
                self.result_color = GREEN
            else:
                self.result_message = f"Has completado la actividad con {self.correct_answers} de {len(self.questions)} respuestas correctas. Has completado el juego con éxito."
                self.result_color = YELLOW
                
            return False

    def handle_event(self, event):
        """Maneja los eventos de la actividad."""
        if not self.active:
            return

        # Manejar eventos cuando se muestra el resultado
        if self.show_result and hasattr(self, 'result_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.result_button_rect.collidepoint(event.pos):
                    if self.completed:
                        # Activar directamente la pantalla de victoria si tenemos referencia al juego
                        if self.game:
                            # Calcular puntuación final
                            self.game.completed_rooms += 1
                            time_left = self.game.timer.get_time_left()
                            self.game.time_bonus = int(time_left * 10)  # 10 puntos por segundo restante
                            self.game.total_score = (self.game.completed_rooms * 1000) + self.game.time_bonus
                            self.game.high_score = max(self.game.high_score, self.game.total_score)
                            # Cambiar estado a victoria
                            self.game.state = STATE_VICTORY
                            print("¡Juego completado! Victoria activada directamente.")
                        # También desactivar la actividad por si acaso
                        self.deactivate()
                        return
                    elif self.failed:
                        # Si ha fallado, activar game over
                        if self.game:
                            self.game.state = STATE_GAME_OVER
                            print("¡Game Over activado directamente!")
                        return
                    else:
                        self.show_result = False
                    return
            # También permitir cerrar con la tecla ESPACIO cuando se muestra el resultado
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.completed:
                    # Activar directamente la pantalla de victoria si tenemos referencia al juego
                    if self.game:
                        # Calcular puntuación final
                        self.game.completed_rooms += 1
                        time_left = self.game.timer.get_time_left()
                        self.game.time_bonus = int(time_left * 10)  # 10 puntos por segundo restante
                        self.game.total_score = (self.game.completed_rooms * 1000) + self.game.time_bonus
                        self.game.high_score = max(self.game.high_score, self.game.total_score)
                        # Cambiar estado a victoria
                        self.game.state = STATE_VICTORY
                        print("¡Juego completado! Victoria activada directamente con ESPACIO.")
                    self.deactivate()
                    return
                elif self.failed:
                    # Si ha fallado, activar game over
                    if self.game:
                        self.game.state = STATE_GAME_OVER
                        print("¡Game Over activado directamente con ESPACIO!")
                    return
                else:
                    self.show_result = False
                return

        # Manejar eventos cuando se muestra feedback
        if self.feedback_active and hasattr(self, 'feedback_button_rect'):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.feedback_button_rect.collidepoint(event.pos):
                    self.feedback_active = False
                    # Si la pregunta ya fue respondida y tiene feedback, avanzar a la siguiente
                    if self.questions[self.current_question]["answered"]:
                        self._next_question()
                    return
            # También permitir cerrar el feedback con ESPACIO
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.feedback_active = False
                if self.questions[self.current_question]["answered"]:
                    self._next_question()
                return

        # Si se presiona el botón de cerrar manual
        if hasattr(self, 'manual_close_rect') and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.manual_close_rect.collidepoint(event.pos):
                self.deactivate()
                return

        # Manejo de clic en opciones
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Verificar si se hizo clic en alguna opción
            current_q = self.questions[self.current_question]
            
            if not current_q["answered"]:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        # Guardar la opción seleccionada
                        current_q["selected"] = i
                        current_q["answered"] = True
                        
                        # Verificar si es correcta
                        if i == current_q["correct"]:
                            # Respuesta correcta
                            self.correct_answers += 1
                            self.feedback_active = True
                            self.result_message = f"¡Correcto! Esta es la mejor opción para esta situación."
                            self.result_color = GREEN
                        else:
                            # Respuesta incorrecta
                            self.errors_count += 1
                            self.feedback_active = True
                            
                            # Verificar si se ha llegado al límite de errores
                            if self.errors_count >= self.max_errors:
                                self.failed = True
                                self.result_message = f"Respuesta incorrecta. Has cometido demasiados errores. ¡Game Over!"
                            else:
                                # Mostrar cuántos intentos quedan
                                remaining = self.max_errors - self.errors_count
                                self.result_message = f"Respuesta incorrecta. La opción correcta era: {self.questions[self.current_question]['options'][current_q['correct']]}. Te quedan {remaining} {'intento' if remaining == 1 else 'intentos'}."
                            
                            self.result_color = RED
                        
                        return

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
        title_text = self.font_title.render("Situaciones de Gestión de Proyectos", True, WHITE)
        title_rect = title_text.get_rect(center=(self.panel_x + self.panel_width // 2, self.panel_y + 30))
        screen.blit(title_text, title_rect)
        
        # Mostrar progreso
        progress_text = self.font_small.render(f"Pregunta {self.current_question + 1} de {len(self.questions)} | Correctas: {self.correct_answers}", True, LIGHT_GRAY)
        progress_rect = progress_text.get_rect(topleft=(self.panel_x + 20, self.panel_y + 20))
        screen.blit(progress_text, progress_rect)
        
        # Panel de la pregunta actual
        current_q = self.questions[self.current_question]
        
        # Dibujar fondo del panel de pregunta (bocadillo de diálogo)
        pygame.draw.rect(screen, WHITE, 
                        (self.question_panel_x, self.question_panel_y, 
                         self.question_panel_width, self.question_panel_height),
                        border_radius=20)
        
        # Dibujar borde del panel de pregunta
        pygame.draw.rect(screen, BLACK, 
                        (self.question_panel_x, self.question_panel_y, 
                         self.question_panel_width, self.question_panel_height),
                        2, border_radius=20)
        
        # Dibujar icono de persona (círculo para cabeza)
        head_radius = 15
        head_x = self.question_panel_x - head_radius
        head_y = self.question_panel_y + self.question_panel_height // 2
        pygame.draw.circle(screen, BLACK, (head_x, head_y), head_radius, 2)
        
        # Texto de la pregunta
        question_lines = self._wrap_text(current_q["text"], self.font_medium, self.question_panel_width - 40)
        for i, line in enumerate(question_lines):
            line_text = self.font_medium.render(line, True, BLACK)
            line_rect = line_text.get_rect(center=(self.question_panel_x + self.question_panel_width // 2, 
                                                  self.question_panel_y + 30 + i * 25))
            screen.blit(line_text, line_rect)
        
        # Dibujar opciones
        for i, rect in enumerate(self.option_rects):
            # Determinar color de fondo según estado
            bg_color = BEIGE
            border_color = BLACK
            
            if current_q["answered"] and i == current_q["selected"]:
                if i == current_q["correct"]:
                    border_color = GREEN
                else:
                    border_color = RED
            
            # Dibujar fondo de nota de papel
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)
            
            # Dibujar borde
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)
            
            # Dibujar texto de opción
            option_lines = self._wrap_text(current_q["options"][i], self.font_small, rect.width - 40)
            for j, line in enumerate(option_lines):
                line_text = self.font_small.render(line, True, BLACK)
                line_rect = line_text.get_rect(
                    x=rect.x + 20,
                    y=rect.y + 20 + j * 20
                )
                screen.blit(line_text, line_rect)
                
            # Si la pregunta ya fue respondida, mostrar indicador visual
            if current_q["answered"]:
                if i == current_q["correct"]:
                    # Dibujar un check verde
                    check_x = rect.right - 30
                    check_y = rect.bottom - 30
                    
                    # Círculo verde
                    pygame.draw.circle(screen, GREEN, (check_x, check_y), 15)
                    
                    # Dibujar un check (✓)
                    check_text = pygame.font.Font(None, 25).render("✓", True, WHITE)
                    check_rect = check_text.get_rect(center=(check_x, check_y))
                    screen.blit(check_text, check_rect)
                    
                elif i == current_q["selected"] and i != current_q["correct"]:
                    # Dibujar una X roja
                    x_x = rect.right - 30
                    x_y = rect.bottom - 30
                    
                    # Círculo rojo
                    pygame.draw.circle(screen, RED, (x_x, x_y), 15)
                    
                    # Dibujar una X
                    x_text = pygame.font.Font(None, 25).render("✗", True, WHITE)
                    x_rect = x_text.get_rect(center=(x_x, x_y))
                    screen.blit(x_text, x_rect)
        
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
        
        close_text = pygame.font.Font(None, 14).render("Cerrar", True, WHITE)
        close_text_rect = close_text.get_rect(center=self.manual_close_rect.center)
        screen.blit(close_text, close_text_rect)
        
        # Mostrar mensaje de resultado si es necesario
        if self.show_result:
            self._render_result_modal(screen)
            
        # Mostrar feedback si hay error o acierto
        if self.feedback_active:
            self._render_feedback_modal(screen)
    
    def _render_result_modal(self, screen):
        """Renderiza el modal de resultado (éxito o advertencia)."""
        modal_width = 400
        modal_height = 200
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Fondo del modal
        pygame.draw.rect(screen, DARK_GRAY, (modal_x, modal_y, modal_width, modal_height), border_radius=15)
        pygame.draw.rect(screen, self.result_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=15)
        
        # Título según resultado
        title = "¡ÉXITO!" if self.completed and self.correct_answers > 0 else "GAME OVER"
        title_text = self.font_title.render(title, True, self.result_color)
        title_rect = title_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 30))
        screen.blit(title_text, title_rect)
        
        # Mensaje
        lines = self._wrap_text(self.result_message, self.font_small, modal_width - 40)
        for i, line in enumerate(lines):
            line_text = self.font_small.render(line, True, WHITE)
            line_rect = line_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 70 + i * 25))
            screen.blit(line_text, line_rect)
            
        # Botón de cerrar
        button_width = 70
        button_height = 25
        button_x = modal_x + (modal_width - button_width) // 2
        button_y = modal_y + modal_height - 60
        self.result_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        pygame.draw.rect(screen, DARK_GRAY, self.result_button_rect, border_radius=8)
        pygame.draw.rect(screen, self.result_color, self.result_button_rect, 2, border_radius=8)
        
        button_text = pygame.font.Font(None, 14).render("Aceptar", True, WHITE)
        button_rect = button_text.get_rect(center=self.result_button_rect.center)
        screen.blit(button_text, button_rect)
        
        # Agregar texto de ayuda para indicar que pueden usar la tecla ESPACIO
        if self.completed:
            help_text = pygame.font.Font(None, 14).render("Presiona ESPACIO o haz clic para finalizar el juego", True, LIGHT_GRAY)
            help_rect = help_text.get_rect(center=(modal_x + modal_width // 2, modal_y + modal_height - 30))
            screen.blit(help_text, help_rect)
            
            # Si la actividad está completada y tenemos la referencia al juego, activar la victoria directamente
            if self.game and hasattr(self.game, 'state'):
                # Esperar 3 segundos y activar la victoria automáticamente
                current_time = pygame.time.get_ticks()
                
                # Verificar si hemos iniciado el temporizador
                if not hasattr(self, 'completion_time'):
                    self.completion_time = current_time
                
                # Si han pasado 5 segundos desde que se completó
                if current_time - self.completion_time > 5000:  # 5 segundos en milisegundos
                    # Calcular puntuación final
                    self.game.completed_rooms += 1
                    time_left = self.game.timer.get_time_left()
                    self.game.time_bonus = int(time_left * 10)  # 10 puntos por segundo restante
                    self.game.total_score = (self.game.completed_rooms * 1000) + self.game.time_bonus
                    self.game.high_score = max(self.game.high_score, self.game.total_score)
                    # Cambiar estado a victoria
                    self.game.state = STATE_VICTORY
                    print("¡Juego completado! Victoria activada automáticamente después de 5 segundos.")
                    # Limpiar el temporizador
                    del self.completion_time
                    self.deactivate()
    
    def _render_feedback_modal(self, screen):
        """Renderiza el modal de feedback de error o acierto."""
        modal_width = 400
        modal_height = 200  # Aumentado de 150 a 200 para más espacio
        modal_x = (WINDOW_WIDTH - modal_width) // 2
        modal_y = (WINDOW_HEIGHT - modal_height) // 2
        
        # Fondo del modal con estilo según tipo de feedback
        bg_color = (20, 60, 20) if self.result_color == GREEN else (50, 20, 20)
        pygame.draw.rect(screen, bg_color, (modal_x, modal_y, modal_width, modal_height), border_radius=15)
        pygame.draw.rect(screen, self.result_color, (modal_x, modal_y, modal_width, modal_height), 3, border_radius=15)
        
        # Título de feedback
        title = "¡Correcto!" if self.result_color == GREEN else "Incorrecto"
        if self.failed:
            title = "¡Game Over!"
            
        title_text = self.font_title.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 30))
        screen.blit(title_text, title_rect)
        
        # Mensaje de feedback
        wrapped_lines = self._wrap_text(self.result_message, self.font_medium, modal_width - 60)
        for i, line in enumerate(wrapped_lines):
            message_text = self.font_medium.render(line, True, WHITE)
            message_rect = message_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 70 + i * 25))
            screen.blit(message_text, message_rect)
        
        # Botón para cerrar el feedback
        button_rect = pygame.Rect(modal_x + modal_width // 2 - 50, modal_y + modal_height - 40, 100, 30)
        pygame.draw.rect(screen, self.result_color, button_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=10)
        
        # No mostrar el botón de continuar si ha fallado, ya que pasará al Game Over
        button_text = self.font_medium.render("Continuar" if not self.failed else "Aceptar", True, WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        # Guardar referencia al rectángulo del botón para detectar clics
        self.feedback_button_rect = button_rect 