#!/usr/bin/env python3
"""
Theme Manager for Tic Tac Toe Evolution
Provides easy theme switching and management
"""

from settings import Theme, CURRENT_THEME

class ThemeManager:
    """Manages theme switching and provides easy access to colors"""
    
    def __init__(self, initial_theme=None):
        self.current_theme = initial_theme or CURRENT_THEME
        self._update_legacy_colors()
    
    def switch_theme(self, theme_name):
        """Switch to a different theme"""
        if hasattr(Theme, theme_name.upper()):
            self.current_theme = getattr(Theme, theme_name.upper())
            self._update_legacy_colors()
            print(f"Switched to {theme_name} theme")
            return True
        else:
            print(f"Theme '{theme_name}' not found. Available themes: {self.get_available_themes()}")
            return False
    
    def get_color(self, color_name):
        """Get a color from the current theme"""
        return self.current_theme.get(color_name, (255, 255, 255))
    
    def get_available_themes(self):
        """Get list of available theme names"""
        return [attr.lower() for attr in dir(Theme) if not attr.startswith('_') and isinstance(getattr(Theme, attr), dict)]
    
    def preview_theme(self, theme_name):
        """Preview a theme without switching to it"""
        if hasattr(Theme, theme_name.upper()):
            return getattr(Theme, theme_name.upper())
        return None
    
    def _update_legacy_colors(self):
        """Update legacy color variables for backward compatibility"""
        global WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY, RED, BLUE, GREEN, YELLOW, ORANGE
        
        WHITE = self.get_color('text_primary')
        BLACK = self.get_color('background')
        GRAY = self.get_color('text_muted')
        LIGHT_GRAY = self.get_color('text_secondary')
        DARK_GRAY = self.get_color('ui_background')
        RED = self.get_color('player_x')
        BLUE = self.get_color('player_o')
        GREEN = self.get_color('success')
        YELLOW = self.get_color('highlight')
        ORANGE = self.get_color('warning')
    
    def _get_theme_name(self):
        """Get the name of the current theme"""
        for attr in dir(Theme):
            if not attr.startswith('_') and isinstance(getattr(Theme, attr), dict):
                if getattr(Theme, attr) == self.current_theme:
                    return attr.lower()
        return "unknown"
    
    def print_theme_info(self):
        """Print information about the current theme"""
        print(f"Current theme: {self._get_theme_name()}")
        print("Available colors:")
        for color_name, color_value in self.current_theme.items():
            print(f"  {color_name}: {color_value}")

# Global theme manager instance
theme_manager = ThemeManager()

# Convenience functions
def switch_theme(theme_name):
    """Switch to a different theme"""
    return theme_manager.switch_theme(theme_name)

def get_color(color_name):
    """Get a color from the current theme"""
    return theme_manager.get_color(color_name)

def get_available_themes():
    """Get list of available themes"""
    return theme_manager.get_available_themes()

def print_theme_info():
    """Print current theme information"""
    theme_manager.print_theme_info()

# Example usage:
if __name__ == "__main__":
    print("Theme Manager Demo")
    print("=" * 50)
    
    print_theme_info()
    print(f"\nAvailable themes: {get_available_themes()}")
    
    # Switch to light theme
    print("\nSwitching to light theme...")
    switch_theme('light')
    print_theme_info()
    
    # Switch back to dark theme
    print("\nSwitching back to dark theme...")
    switch_theme('dark')
    print_theme_info()
    
    # Try cyberpunk theme
    print("\nSwitching to cyberpunk theme...")
    switch_theme('cyberpunk')
    print_theme_info() 