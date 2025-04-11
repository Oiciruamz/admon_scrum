"""
Room management for the Escape Room game.
"""
import math
import random
import pygame
from settings import *
from educational_content import get_pmbok_content, get_scrum_content
from assets import assets
from utils import draw_text, draw_panel, draw_progress_bar, draw_tooltip, create_particle_effect, update_particles, render_particles

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
        self.objects = []
        self.decorations = []
        self.particles = []
        self.completed = False
        self.completion_time = 0
        self.completion_particles = []

        # Visual effects
        self.ambient_light = 1.0  # 0.0 to 1.0
        self.light_flicker = False
        self.light_flicker_intensity = 0.1
        self.light_flicker_speed = 0.05
        self.light_flicker_time = 0

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

    def add_object(self, obj):
        """
        Add an interactive object to the room.

        Args:
            obj: Object to add
        """
        self.objects.append(obj)

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
        Update room state and objects.
        """
        # Update objects
        for obj in self.objects:
            obj.update()

        # Update decorations
        self._update_decorations()

        # Update particles
        self.particles = update_particles(self.particles)
        self.completion_particles = update_particles(self.completion_particles)

        # Update light flicker effect
        if self.light_flicker:
            self.light_flicker_time += self.light_flicker_speed
            flicker = math.sin(self.light_flicker_time) * self.light_flicker_intensity
            self.ambient_light = max(0.7, min(1.0, 1.0 + flicker))

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
        Handle events for the room and its objects.

        Args:
            event: Pygame event
        """
        for obj in self.objects:
            obj.handle_event(event)

    def render(self, screen):
        """
        Render the room and its objects.

        Args:
            screen: Pygame surface to render on
        """
        # Fill background with dark color
        screen.fill(self.background_color)

        # Draw room background
        self._render_room_background(screen)

        # Draw decorations
        self._render_decorations(screen)

        # Render objects
        for obj in self.objects:
            obj.render(screen)

        # Render particles
        render_particles(screen, self.particles)
        render_particles(screen, self.completion_particles)

        # Render room info
        self._render_room_info(screen)

        # Render completion effect
        if self.completed:
            self._render_completion_effect(screen)

    def _render_room_background(self, screen):
        """
        Render the room background.

        Args:
            screen: Pygame surface to render on
        """
        # Get room background image based on theme
        room_bg = assets.get_image(f"room_{self.theme}")

        # Apply ambient light effect
        if self.ambient_light < 1.0:
            # Create a darkening overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            darkness = int(255 * (1.0 - self.ambient_light))
            overlay.fill((0, 0, 0, darkness))

            # Apply overlay to room background
            temp_surface = room_bg.copy()
            temp_surface.blit(overlay, (0, 0))
            screen.blit(temp_surface, (self.x, self.y))
        else:
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

    def _render_room_info(self, screen):
        """
        Render room information (name, description, etc.).

        Args:
            screen: Pygame surface to render on
        """
        # Draw room name
        draw_text(
            screen,
            self.name,
            self.font_medium,
            WHITE,
            self.x + 20,
            self.y + 20,
            "left"
        )

        # Draw room description
        draw_text(
            screen,
            self.description,
            self.font_small,
            SILVER,
            self.x + 20,
            self.y + 60,
            "left"
        )

    def _render_completion_effect(self, screen):
        """
        Render completion effect when room is completed.

        Args:
            screen: Pygame surface to render on
        """
        # Create completion particles if just completed
        if self.completion_time == 1:
            for _ in range(3):
                particles = create_particle_effect(
                    WINDOW_WIDTH // 2,
                    WINDOW_HEIGHT // 2,
                    count=20,
                    colors=[YELLOW, WHITE, ORANGE],
                    min_speed=1,
                    max_speed=3,
                    min_size=3,
                    max_size=8,
                    min_lifetime=30,
                    max_lifetime=60
                )
                self.completion_particles.extend(particles)

        # Draw completion message
        if self.completion_time < 120:  # Show for 2 seconds (60 FPS)
            alpha = min(255, self.completion_time * 8)  # Fade in
            if self.completion_time > 60:
                alpha = max(0, 255 - (self.completion_time - 60) * 8)  # Fade out

            # Create a temporary surface for the message with transparency
            message_surface = pygame.Surface((400, 100), pygame.SRCALPHA)

            # Draw panel background
            draw_panel(
                message_surface,
                0, 0, 400, 100,
                CHARCOAL,
                WHITE,
                2,
                10,
                alpha
            )

            # Draw completion text
            draw_text(
                message_surface,
                "Room Completed!",
                self.font_large,
                (*GREEN, alpha),
                200, 30,
                "center"
            )

            draw_text(
                message_surface,
                "Proceed to the next room",
                self.font_small,
                (*WHITE, alpha),
                200, 70,
                "center"
            )

            # Draw the message in the center of the screen
            screen.blit(
                message_surface,
                (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 50)
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

        # Room 4: Monitoring and Control
        room4 = PMBOKMonitoringRoom(pmbok_content[3])
        self.rooms.append(room4)

        # Room 5: Closing
        room5 = PMBOKClosingRoom(pmbok_content[4])
        self.rooms.append(room5)

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

        # Room 4: Scrum Values
        room4 = ScrumValuesRoom(scrum_content[3])
        self.rooms.append(room4)


# PMBOK Room Classes
class PMBOKInitiationRoom(Room):
    """
    Room for the Initiation phase of PMBOK.
    """
    def __init__(self, content):
        """
        Initialize the Initiation room.

        Args:
            content: Educational content for this room
        """
        super().__init__("PMBOK: Initiation Phase", "Learn about project initiation", GRAY, "gray")
        self.content = content
        self.total_score = 0

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add a project charter object with puzzle
        charter = InteractiveObject("Project Charter", 250, 200, 150, 100, RED, "square")
        charter.set_description("Create a project charter by selecting the correct components")
        charter.set_content(self.content, difficulty=1)
        self.add_object(charter)

        # Add stakeholder register with puzzle
        stakeholders = InteractiveObject("Stakeholder Register", 600, 200, 150, 100, GREEN, "circle")
        stakeholders.set_description("Identify key stakeholders for the project")
        stakeholders.set_content(self.content, difficulty=2)
        self.add_object(stakeholders)

        # Add business case with puzzle
        business_case = InteractiveObject("Business Case", 425, 350, 150, 100, BLUE, "diamond")
        business_case.set_description("Develop a business case to justify the project")
        business_case.set_content(self.content, difficulty=3)
        self.add_object(business_case)

    def update(self):
        """
        Update room state and objects.
        """
        super().update()

        # Update total score
        self.total_score = sum(obj.score for obj in self.objects)

    def _check_completion(self):
        """
        Check if the initiation phase challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class PMBOKPlanningRoom(Room):
    """
    Room for the Planning phase of PMBOK.
    """
    def __init__(self, content):
        """
        Initialize the Planning room.

        Args:
            content: Educational content for this room
        """
        super().__init__("PMBOK: Planning Phase", "Learn about project planning", LIGHT_BLUE)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add a WBS object
        wbs = InteractiveObject("Work Breakdown Structure", 100, 200, 150, 100, YELLOW)
        wbs.set_description("Create a WBS by organizing project deliverables")
        self.add_object(wbs)

        # Add schedule object
        schedule = InteractiveObject("Project Schedule", 500, 200, 150, 100, WHITE)
        schedule.set_description("Develop a project schedule with correct dependencies")
        self.add_object(schedule)

    def _check_completion(self):
        """
        Check if the planning phase challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class PMBOKExecutionRoom(Room):
    """
    Room for the Execution phase of PMBOK.
    """
    def __init__(self, content):
        """
        Initialize the Execution room.

        Args:
            content: Educational content for this room
        """
        super().__init__("PMBOK: Execution Phase", "Learn about project execution", GREEN)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add team management object
        team = InteractiveObject("Team Management", 100, 200, 150, 100, BLUE)
        team.set_description("Manage the project team effectively")
        self.add_object(team)

        # Add quality assurance object
        quality = InteractiveObject("Quality Assurance", 500, 200, 150, 100, RED)
        quality.set_description("Implement quality assurance processes")
        self.add_object(quality)

    def _check_completion(self):
        """
        Check if the execution phase challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class PMBOKMonitoringRoom(Room):
    """
    Room for the Monitoring and Control phase of PMBOK.
    """
    def __init__(self, content):
        """
        Initialize the Monitoring and Control room.

        Args:
            content: Educational content for this room
        """
        super().__init__("PMBOK: Monitoring & Control", "Learn about project monitoring", YELLOW)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add performance tracking object
        performance = InteractiveObject("Performance Tracking", 100, 200, 150, 100, GREEN)
        performance.set_description("Track project performance using earned value management")
        self.add_object(performance)

        # Add change control object
        changes = InteractiveObject("Change Control", 500, 200, 150, 100, BLUE)
        changes.set_description("Manage project changes through proper control processes")
        self.add_object(changes)

    def _check_completion(self):
        """
        Check if the monitoring phase challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class PMBOKClosingRoom(Room):
    """
    Room for the Closing phase of PMBOK.
    """
    def __init__(self, content):
        """
        Initialize the Closing room.

        Args:
            content: Educational content for this room
        """
        super().__init__("PMBOK: Closing Phase", "Learn about project closure", RED)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add final deliverable object
        deliverable = InteractiveObject("Final Deliverables", 100, 200, 150, 100, GREEN)
        deliverable.set_description("Verify all deliverables are complete and accepted")
        self.add_object(deliverable)

        # Add lessons learned object
        lessons = InteractiveObject("Lessons Learned", 500, 200, 150, 100, BLUE)
        lessons.set_description("Document lessons learned for future projects")
        self.add_object(lessons)

    def _check_completion(self):
        """
        Check if the closing phase challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


# Scrum Room Classes
class ScrumRolesRoom(Room):
    """
    Room for learning about Scrum roles.
    """
    def __init__(self, content):
        """
        Initialize the Scrum Roles room.

        Args:
            content: Educational content for this room
        """
        super().__init__("Scrum: Roles", "Learn about Scrum roles", BLUE)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add Product Owner object
        po = InteractiveObject("Product Owner", 100, 200, 150, 100, RED)
        po.set_description("Learn about the Product Owner role and responsibilities")
        self.add_object(po)

        # Add Scrum Master object
        sm = InteractiveObject("Scrum Master", 300, 200, 150, 100, GREEN)
        sm.set_description("Learn about the Scrum Master role and responsibilities")
        self.add_object(sm)

        # Add Development Team object
        team = InteractiveObject("Development Team", 500, 200, 150, 100, YELLOW)
        team.set_description("Learn about the Development Team role and responsibilities")
        self.add_object(team)

    def _check_completion(self):
        """
        Check if the Scrum roles challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class ScrumArtifactsRoom(Room):
    """
    Room for learning about Scrum artifacts.
    """
    def __init__(self, content):
        """
        Initialize the Scrum Artifacts room.

        Args:
            content: Educational content for this room
        """
        super().__init__("Scrum: Artifacts", "Learn about Scrum artifacts", GREEN)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add Product Backlog object
        backlog = InteractiveObject("Product Backlog", 100, 200, 150, 100, BLUE)
        backlog.set_description("Learn about the Product Backlog and how to manage it")
        self.add_object(backlog)

        # Add Sprint Backlog object
        sprint_backlog = InteractiveObject("Sprint Backlog", 300, 200, 150, 100, RED)
        sprint_backlog.set_description("Learn about the Sprint Backlog and how to create it")
        self.add_object(sprint_backlog)

        # Add Increment object
        increment = InteractiveObject("Increment", 500, 200, 150, 100, YELLOW)
        increment.set_description("Learn about the Increment and Definition of Done")
        self.add_object(increment)

    def _check_completion(self):
        """
        Check if the Scrum artifacts challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class ScrumEventsRoom(Room):
    """
    Room for learning about Scrum events.
    """
    def __init__(self, content):
        """
        Initialize the Scrum Events room.

        Args:
            content: Educational content for this room
        """
        super().__init__("Scrum: Events", "Learn about Scrum events", YELLOW)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add Sprint Planning object
        planning = InteractiveObject("Sprint Planning", 100, 150, 150, 100, RED)
        planning.set_description("Learn about Sprint Planning and how to conduct it")
        self.add_object(planning)

        # Add Daily Scrum object
        daily = InteractiveObject("Daily Scrum", 300, 150, 150, 100, GREEN)
        daily.set_description("Learn about the Daily Scrum and its purpose")
        self.add_object(daily)

        # Add Sprint Review object
        review = InteractiveObject("Sprint Review", 100, 300, 150, 100, BLUE)
        review.set_description("Learn about the Sprint Review and how to conduct it")
        self.add_object(review)

        # Add Sprint Retrospective object
        retro = InteractiveObject("Sprint Retrospective", 300, 300, 150, 100, WHITE)
        retro.set_description("Learn about the Sprint Retrospective and its importance")
        self.add_object(retro)

    def _check_completion(self):
        """
        Check if the Scrum events challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class ScrumValuesRoom(Room):
    """
    Room for learning about Scrum values.
    """
    def __init__(self, content):
        """
        Initialize the Scrum Values room.

        Args:
            content: Educational content for this room
        """
        super().__init__("Scrum: Values", "Learn about Scrum values", RED)
        self.content = content

        # Add objects specific to this room
        self._setup_room()

    def _setup_room(self):
        """
        Set up room-specific objects and challenges.
        """
        # Add Commitment object
        commitment = InteractiveObject("Commitment", 100, 150, 120, 80, BLUE)
        commitment.set_description("Learn about the Scrum value of Commitment")
        self.add_object(commitment)

        # Add Courage object
        courage = InteractiveObject("Courage", 250, 150, 120, 80, GREEN)
        courage.set_description("Learn about the Scrum value of Courage")
        self.add_object(courage)

        # Add Focus object
        focus = InteractiveObject("Focus", 400, 150, 120, 80, YELLOW)
        focus.set_description("Learn about the Scrum value of Focus")
        self.add_object(focus)

        # Add Openness object
        openness = InteractiveObject("Openness", 175, 300, 120, 80, WHITE)
        openness.set_description("Learn about the Scrum value of Openness")
        self.add_object(openness)

        # Add Respect object
        respect = InteractiveObject("Respect", 325, 300, 120, 80, RED)
        respect.set_description("Learn about the Scrum value of Respect")
        self.add_object(respect)

    def _check_completion(self):
        """
        Check if the Scrum values challenges are completed.
        """
        # Check if all objects are in the correct state
        all_completed = all(obj.is_completed() for obj in self.objects)
        if all_completed:
            self.completed = True


class InteractiveObject:
    """
    Interactive object that can be placed in rooms.
    """
    def __init__(self, name, x, y, width, height, color, shape="square"):
        """
        Initialize an interactive object.

        Args:
            name: Object name
            x: X position
            y: Y position
            width: Object width
            height: Object height
            color: Object color
            shape: Object shape ("square", "circle", "triangle", "diamond", "hexagon")
        """
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.shape = shape
        self.rect = pygame.Rect(x, y, width, height)
        self.description = ""
        self.completed = False
        self.active = False
        self.hover = False

        # Visual effects
        self.pulse_time = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.03, 0.06)
        self.pulse_amount = 0.1  # 10% size pulsing
        self.glow_amount = 0
        self.particles = []

        # Animation
        self.animation_offset = 0
        self.animation_speed = 0.05
        self.animation_time = 0

        # Interaction
        self.interaction_time = 0
        self.interaction_duration = 60  # frames

        # Fonts
        self.font_name = assets.get_font("small")
        self.font_desc = assets.get_font("tiny")

        # Puzzle
        self.puzzle = None
        self.content_item = None
        self.score = 0

    def update(self):
        """
        Update object state.
        """
        # Update pulse animation
        self.pulse_time += self.pulse_speed

        # Update hover animation
        if self.hover:
            self.glow_amount = min(1.0, self.glow_amount + 0.1)
        else:
            self.glow_amount = max(0.0, self.glow_amount - 0.1)

        # Update interaction animation
        if self.interaction_time > 0:
            self.interaction_time -= 1

            # Create particles during interaction
            if self.interaction_time % 5 == 0 and self.interaction_time > 30:
                particle_x = self.x + self.width // 2
                particle_y = self.y + self.height // 2
                new_particles = create_particle_effect(
                    particle_x, particle_y,
                    count=2,
                    colors=[self.color, WHITE],
                    min_speed=0.5, max_speed=1.5,
                    min_size=2, max_size=4,
                    min_lifetime=10, max_lifetime=20
                )
                self.particles.extend(new_particles)

        # Update particles
        self.particles = update_particles(self.particles)

        # Update animation
        self.animation_time += self.animation_speed
        self.animation_offset = math.sin(self.animation_time) * 3

        # Update puzzle if active
        if self.puzzle and self.active:
            self.puzzle.update()

    def handle_event(self, event):
        """
        Handle events for the object.

        Args:
            event: Pygame event
        """
        # Check for mouse hover
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        # If puzzle is active, pass events to it
        if self.puzzle and self.active:
            self.puzzle.handle_event(event)
            return

        # Check for mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.interaction_time = self.interaction_duration

                # If we have a puzzle, activate it
                if self.puzzle and not self.completed:
                    self.active = True
                    screen_rect = pygame.display.get_surface().get_rect()
                    self.puzzle.activate(screen_rect)

                    # Create interaction particles
                    particle_x = self.x + self.width // 2
                    particle_y = self.y + self.height // 2
                    new_particles = create_particle_effect(
                        particle_x, particle_y,
                        count=10,
                        colors=[self.color, WHITE],
                        min_speed=0.5, max_speed=2,
                        min_size=2, max_size=4,
                        min_lifetime=15, max_lifetime=30
                    )
                    self.particles.extend(new_particles)
                else:
                    # Toggle active state for objects without puzzles
                    self.active = not self.active

    def render(self, screen):
        """
        Render the object.

        Args:
            screen: Pygame surface to render on
        """
        # Si el puzzle está activo, solo renderizar el objeto con opacidad reducida
        # El puzzle mismo será renderizado más tarde por la clase Game para asegurar que esté en la capa superior
        if self.puzzle and self.active and self.puzzle.active:
            # Renderizar el objeto en el fondo con opacidad reducida
            self._render_object(screen, alpha=100)
            return

        # Si el objeto está completado, renderizarlo con un efecto especial
        if self.completed:
            # Renderizar el objeto con un efecto de completado (brillo verde)
            self._render_object(screen, completed=True)
        else:
            # De lo contrario, renderizar normalmente
            self._render_object(screen)

    def _render_object(self, screen, alpha=255, completed=False):
        """
        Render the object itself (without puzzle).

        Args:
            screen: Pygame surface to render on
            alpha: Opacity (0-255)
            completed: Whether the object is completed
        """
        # Calculate pulse effect
        pulse = math.sin(self.pulse_time) * self.pulse_amount + 1.0

        # Calculate dimensions with pulse
        width = int(self.width * pulse)
        height = int(self.height * pulse)
        x = self.x + (self.width - width) // 2
        y = self.y + (self.height - height) // 2 + int(self.animation_offset)

        # Draw shadow
        shadow_offset = 5
        shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, width, height)

        if self.shape == "square":
            pygame.draw.rect(screen, (*BLACK, 70), shadow_rect, border_radius=10)
        elif self.shape == "circle":
            pygame.draw.ellipse(screen, (*BLACK, 70), shadow_rect)

        # Si el objeto está completado, dibujar un efecto de brillo alrededor
        if completed:
            glow_rect = pygame.Rect(x - 5, y - 5, width + 10, height + 10)
            if self.shape == "square":
                pygame.draw.rect(screen, (*GREEN, 150), glow_rect, border_radius=12)
            elif self.shape == "circle":
                pygame.draw.ellipse(screen, (*GREEN, 150), glow_rect)

        # Get object image or draw shape
        if self.shape in ["square", "circle", "triangle", "diamond", "hexagon"]:
            # Try to get image from assets
            color_name = self._get_color_name()
            image_name = f"object_{self.shape}_{color_name}"
            obj_image = assets.get_image(image_name)

            # Scale image with pulse effect
            scaled_image = pygame.transform.scale(obj_image, (width, height))

            # Apply alpha if needed
            if alpha < 255:
                scaled_image.set_alpha(alpha)

            screen.blit(scaled_image, (x, y))
        else:
            # Fallback to drawing a rectangle
            rect = pygame.Rect(x, y, width, height)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.rect(screen, color_with_alpha, rect, border_radius=10)
            pygame.draw.rect(screen, (*WHITE, alpha), rect, 2, border_radius=10)

        # Draw glow effect when hovering
        if self.glow_amount > 0:
            glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
            glow_color = (*self.color, int((100 * self.glow_amount * alpha) // 255))
            pygame.draw.rect(glow_surface, glow_color, (0, 0, width + 20, height + 20), border_radius=15)
            screen.blit(glow_surface, (x - 10, y - 10), special_flags=pygame.BLEND_ADD)

        # Draw completion indicator
        if self.completed:
            indicator_x = x + width - 15
            indicator_y = y + 10
            pygame.draw.circle(screen, (*GREEN, alpha), (indicator_x, indicator_y), 8)
            pygame.draw.circle(screen, (*WHITE, alpha), (indicator_x, indicator_y), 8, 1)
            pygame.draw.line(screen, (*WHITE, alpha), (indicator_x - 3, indicator_y), (indicator_x - 1, indicator_y + 3), 2)
            pygame.draw.line(screen, (*WHITE, alpha), (indicator_x - 1, indicator_y + 3), (indicator_x + 3, indicator_y - 2), 2)

            # Draw score if completed
            if self.score > 0:
                score_text = self.font_desc.render(f"{self.score} pts", True, WHITE)
                score_rect = score_text.get_rect(center=(self.x + self.width // 2, self.y + self.height + 40))
                pygame.draw.rect(screen, (*GREEN, 180), score_rect.inflate(10, 6), border_radius=5)
                screen.blit(score_text, score_rect)

        # Draw the name
        name_text = self.font_name.render(self.name, True, WHITE)
        name_rect = name_text.get_rect(center=(self.x + self.width // 2, self.y + self.height + 20))

        # Draw name background for better readability
        bg_rect = name_rect.copy()
        bg_rect.inflate_ip(10, 6)
        pygame.draw.rect(screen, (*CHARCOAL, 180), bg_rect, border_radius=5)

        screen.blit(name_text, name_rect)

        # Draw particles
        render_particles(screen, self.particles)

        # If active but not showing puzzle, draw the description tooltip
        if self.active and (not self.puzzle or self.completed):
            draw_tooltip(
                screen,
                self.description,
                self.font_desc,
                self.x + self.width // 2,
                self.y - 30,
                padding=10,
                bg_color=CHARCOAL,
                text_color=WHITE,
                border_color=self.color,
                border_width=2,
                radius=5,
                max_width=300
            )

    def _get_color_name(self):
        """
        Get the name of the color closest to self.color.

        Returns:
            String name of the color
        """
        colors = {
            "red": RED,
            "green": GREEN,
            "blue": BLUE,
            "yellow": YELLOW,
            "purple": PURPLE,
            "cyan": CYAN,
            "orange": ORANGE,
            "white": WHITE
        }

        # Find the closest color by Euclidean distance
        min_distance = float('inf')
        closest_color = "white"

        for name, rgb in colors.items():
            # Calculate color distance
            r_diff = self.color[0] - rgb[0]
            g_diff = self.color[1] - rgb[1]
            b_diff = self.color[2] - rgb[2]
            distance = math.sqrt(r_diff**2 + g_diff**2 + b_diff**2)

            if distance < min_distance:
                min_distance = distance
                closest_color = name

        return closest_color

    def set_description(self, description):
        """
        Set the object description.

        Args:
            description: Object description
        """
        self.description = description

    def set_content(self, content_item, difficulty=1):
        """
        Set the educational content for this object.

        Args:
            content_item: Dictionary containing educational content
            difficulty: Puzzle difficulty (1-5)
        """
        self.content_item = content_item

        # Import here to avoid circular imports
        from puzzles import create_puzzle_from_content

        # Create a puzzle based on the content
        self.puzzle = create_puzzle_from_content(content_item, difficulty)

        # Set up puzzle completion callback
        self.puzzle.set_success_callback(self._on_puzzle_completed)

    def _on_puzzle_completed(self, score):
        """
        Callback for when the puzzle is completed.

        Args:
            score: Puzzle score
        """
        self.completed = True
        self.score = score
        self.active = False  # Desactivar el objeto interactivo cuando se completa el puzzle

        # Create completion particles
        particle_x = self.x + self.width // 2
        particle_y = self.y + self.height // 2
        new_particles = create_particle_effect(
            particle_x, particle_y,
            count=30,
            colors=[self.color, WHITE, YELLOW, GREEN],
            min_speed=1, max_speed=3,
            min_size=3, max_size=6,
            min_lifetime=30, max_lifetime=60
        )
        self.particles.extend(new_particles)

    def is_completed(self):
        """
        Check if the object's challenge is completed.

        Returns:
            Boolean indicating if the object is completed
        """
        return self.completed
