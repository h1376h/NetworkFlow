from manim import *
import numpy as np
from typing import List, Tuple, Optional

class FlowEdge(Arrow):
    """A special arrow class for visualizing flow edges with capacity and flow values"""
    
    def __init__(
        self, 
        start_point: np.ndarray,
        end_point: np.ndarray,
        capacity: int,
        current_flow: int = 0,
        **kwargs
    ):
        # Pass parameters to Arrow constructor
        super().__init__(
            start=start_point,
            end=end_point,
            buff=0.3,
            max_tip_length_to_length_ratio=0.1,
            **kwargs
        )
        
        self.capacity = capacity
        self.current_flow = current_flow
        self.flow_label = None
        self.update_label()
    
    def update_label(self):
        """Update the flow/capacity label on the edge"""
        # Don't try to remove if it doesn't exist yet
        if self.flow_label:
            # Just remove from parent mobject, not from scene
            # (scene removal is handled in animate_flow_update)
            self.flow_label.remove()
        
        # Create label showing flow/capacity
        mid_point = self.get_midpoint()
        # Offset the label perpendicular to the arrow's direction
        direction = normalize(self.get_vector())
        perpendicular = np.array([direction[1], -direction[0], 0])
        
        self.flow_label = Text(
            f"{self.current_flow}/{self.capacity}",
            font_size=20
        ).move_to(mid_point + 0.3 * perpendicular)
        
        return self.flow_label
    
    def set_flow(self, flow_value: int):
        """Set the current flow value and update the label"""
        self.current_flow = flow_value
        return self.update_label()
    
    def animate_flow_update(self, new_flow: int, scene: Scene, run_time: float = 1.0):
        """Animate the edge changing its flow value"""
        self.current_flow = new_flow
        
        # Show flow increase with animation
        old_label = self.flow_label
        
        # First completely remove the old label from the scene
        if old_label in scene.mobjects:
            scene.remove(old_label)
        
        # Create a fresh new label
        new_label = self.update_label()
        
        # Highlight edge briefly
        original_color = self.get_color()
        
        # Add the new label to the scene explicitly
        scene.add(new_label)
        
        # Animate the edge color change only
        scene.play(self.animate(run_time=run_time/2).set_color(YELLOW))
        scene.play(self.animate(run_time=run_time/2).set_color(original_color))
        
        # Make sure the flow_label reference is updated
        self.flow_label = new_label