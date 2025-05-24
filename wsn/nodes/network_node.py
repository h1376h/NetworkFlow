from manim import *
import numpy as np

class NetworkNode(VGroup):
    """Represents a node in the wireless sensor network"""
    def __init__(self, position: np.ndarray, node_id: int, 
                 is_sink: bool = False, is_cluster_head: bool = False,
                 is_malicious: bool = False, has_hardware_failure: bool = False):
        super().__init__()
        
        # Store node properties
        self.node_id = node_id
        self.position = position
        self.is_sink = is_sink
        self.is_cluster_head = is_cluster_head
        self.is_malicious = is_malicious
        self.has_hardware_failure = has_hardware_failure
        
        # Determine node color
        if is_malicious:
            color = PURPLE
        elif has_hardware_failure:
            color = GRAY
        elif is_sink:
            color = RED
        elif is_cluster_head:
            color = GREEN_B
        else:
            color = BLUE_C
            
        # Create main circle
        radius = 0.4 if (is_sink or is_cluster_head) else 0.3
        circle = Circle(
            radius=radius,
            fill_color=color,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=2
        )
        self.add(circle)
        
        # Add special visual elements
        if is_malicious:
            outer_circle = Circle(
                radius=radius + 0.05,
                stroke_color=RED,
                stroke_width=3,
                fill_opacity=0
            )
            self.add(outer_circle)
        elif has_hardware_failure:
            # Add hardware failure indicator (just a cross, no gear)
            cross = VGroup(
                Line(UL/2, DR/2, color=RED_E, stroke_width=3),
                Line(UR/2, DL/2, color=RED_E, stroke_width=3)
            ).scale(radius)
            self.add(cross)
        elif is_cluster_head:
            outer_ring = Circle(
                radius=radius + 0.1,
                fill_opacity=0,
                stroke_color=GREEN,
                stroke_width=3
            )
            self.add(outer_ring)
            
        self.move_to(position) 