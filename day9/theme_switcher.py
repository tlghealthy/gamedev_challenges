#!/usr/bin/env python3
"""
Theme Switcher for Tic Tac Toe Evolution
Simple script to switch between themes
"""

from theme_manager import switch_theme, get_available_themes, print_theme_info
import sys

def main():
    if len(sys.argv) < 2:
        print("Theme Switcher")
        print("=" * 30)
        print("Usage: python theme_switcher.py <theme_name>")
        print(f"Available themes: {get_available_themes()}")
        print("\nCurrent theme:")
        print_theme_info()
        return
    
    theme_name = sys.argv[1].lower()
    if switch_theme(theme_name):
        print(f"\nSuccessfully switched to {theme_name} theme!")
        print("Restart the game to see the changes.")
    else:
        print(f"Failed to switch to {theme_name} theme.")

if __name__ == "__main__":
    main() 