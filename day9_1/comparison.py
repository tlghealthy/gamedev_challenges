#!/usr/bin/env python3
"""
Comparison script to show the code reduction achieved
"""

import os

def count_lines_in_file(filepath):
    """Count lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except FileNotFoundError:
        return 0

def count_lines_in_directory(directory):
    """Count lines in all Python files in a directory"""
    total_lines = 0
    file_count = 0
    
    if not os.path.exists(directory):
        return 0, 0
        
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            filepath = os.path.join(directory, filename)
            lines = count_lines_in_file(filepath)
            total_lines += lines
            file_count += 1
            print(f"  {filename}: {lines} lines")
    
    return total_lines, file_count

def main():
    print("Code Reduction Comparison")
    print("=" * 50)
    
    # Count original version
    print("\nOriginal Version (day9/):")
    original_lines, original_files = count_lines_in_directory("../day9")
    print(f"\nTotal: {original_lines} lines across {original_files} files")
    
    # Count simplified version
    print("\nSimplified Version (day9_1/):")
    simplified_lines, simplified_files = count_lines_in_directory(".")
    print(f"\nTotal: {simplified_lines} lines across {simplified_files} files")
    
    # Calculate reduction
    reduction_lines = original_lines - simplified_lines
    reduction_percent = (reduction_lines / original_lines) * 100 if original_lines > 0 else 0
    file_reduction = original_files - simplified_files
    
    print("\n" + "=" * 50)
    print("REDUCTION SUMMARY:")
    print(f"Lines reduced: {reduction_lines} ({reduction_percent:.1f}%)")
    print(f"Files reduced: {file_reduction} ({file_reduction/original_files*100:.1f}%)")
    print(f"Code density: {simplified_lines/original_lines:.2f}x more concise")
    
    print("\nKey Files in Original:")
    original_key_files = [
        "game.py", "board.py", "game_state.py", "modifier_system.py", 
        "ui_manager.py", "settings.py", "theme_manager.py", "theme_switcher.py"
    ]
    
    for filename in original_key_files:
        filepath = os.path.join("../day9", filename)
        lines = count_lines_in_file(filepath)
        if lines > 0:
            print(f"  {filename}: {lines} lines")
    
    print(f"\nSimplified to single file: game.py ({simplified_lines} lines)")

if __name__ == "__main__":
    main() 