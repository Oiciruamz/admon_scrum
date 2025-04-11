"""
Timer class for the Escape Room game.
"""
import pygame

class Timer:
    """
    Timer for tracking time limits in rooms.
    """
    def __init__(self, time_limit):
        """
        Initialize the timer.
        
        Args:
            time_limit: Time limit in seconds
        """
        self.time_limit = time_limit
        self.time_left = time_limit
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        """
        Update the timer.
        """
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.last_update) / 1000  # Convert to seconds
        
        # Update time left
        self.time_left = max(0, self.time_left - elapsed_seconds)
        
        # Update last update time
        self.last_update = current_time
    
    def reset(self):
        """
        Reset the timer to the time limit.
        """
        self.time_left = self.time_limit
        self.last_update = pygame.time.get_ticks()
    
    def get_time_left(self):
        """
        Get the time left.
        
        Returns:
            Time left in seconds
        """
        return self.time_left
    
    def is_time_up(self):
        """
        Check if time is up.
        
        Returns:
            Boolean indicating if time is up
        """
        return self.time_left <= 0
