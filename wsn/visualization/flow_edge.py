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
    
    def set_flow(self, new_flow: int):
        """Set the flow value and update the label"""
        self.current_flow = new_flow
        self.update_label()
    
    def update_label(self):
        """Update the flow/capacity label on the edge"""
        # Remove old label completely if it exists
        if self.flow_label is not None:
            self.flow_label.clear_updaters()
            # Don't call remove() here as it might not exist
        
        # Create label showing flow/capacity
        mid_point = self.get_midpoint()
        # Offset the label perpendicular to the arrow's direction
        direction = normalize(self.get_vector())
        perpendicular = np.array([direction[1], -direction[0], 0])
        
        self.flow_label = Text(
            f"{self.current_flow}/{self.capacity}",
            font_size=18  # Slightly smaller font
        ).move_to(mid_point + 0.25 * perpendicular)  # Closer to edge
        
        return self.flow_label
    
    def animate_flow_update(self, new_flow: int, scene: Scene, run_time: float = 1.0):
        """Animate the edge changing its flow value"""
        # Store old label reference
        old_label = self.flow_label
        
        # Update flow value
        self.current_flow = new_flow
        
        # Remove old label from scene completely
        if old_label is not None:
            if old_label in scene.mobjects:
                scene.remove(old_label)
            old_label.clear_updaters()
        
        # Create new label
        new_label = self.update_label()
        
        # Highlight edge briefly
        original_color = self.get_color()
        
        # Add the new label to the scene
        scene.add(new_label)
        
        # Animate the edge color change
        scene.play(
            self.animate(run_time=run_time/2).set_color(YELLOW),
            run_time=run_time/2
        )
        scene.play(
            self.animate(run_time=run_time/2).set_color(original_color),
            run_time=run_time/2
        )
        
        # Update the flow_label reference
        self.flow_label = new_label