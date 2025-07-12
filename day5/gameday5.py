"""
Scaffolding for platform-fighter game with extensible procedural stage generation.
"""

import pygame
from pygame import Rect
from typing import List

# --- StageData ---
class StageData:
    """
    Holds the data for a stage, such as platforms and main platform.
    """
    def __init__(self, platforms: List[Rect], main_platform: Rect):
        self.platforms = platforms
        self.main = main_platform

# --- BaseStageGenerator ---
class BaseStageGenerator:
    """
    Abstract base class for procedural stage generators.
    """
    def generate(self) -> StageData:
        """
        Generate and return a StageData instance.
        """
        raise NotImplementedError

# --- DefaultStageGenerator ---
class DefaultStageGenerator(BaseStageGenerator):
    """
    Default procedural stage generator using standard rules/settings.
    """
    def generate(self) -> StageData:
        """
        Implement procedural generation logic here and return StageData.
        """
        pass  # To be implemented

# --- Stage ---
class Stage:
    """
    Handles stage logic and rendering, using StageData for structure.
    """
    def __init__(self, stage_data: StageData):
        self.platforms = stage_data.platforms
        self.main = stage_data.main

    def draw(self, surf: pygame.Surface):
        """
        Draw the stage platforms to the given surface.
        """
        pass  # To be implemented
