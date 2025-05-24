from manim import *
import numpy as np

class NetworkConnection(Line):
    """Represents a connection between two nodes"""
    def __init__(self, start_pos: np.ndarray, end_pos: np.ndarray, 
                 is_route: bool = False, color: str = YELLOW_A):
        super().__init__(
            start=start_pos,
            end=end_pos,
            stroke_color=color if is_route else GRAY,
            stroke_width=4 if is_route else 2,
            stroke_opacity=0.8 if is_route else 0.6
        ) 