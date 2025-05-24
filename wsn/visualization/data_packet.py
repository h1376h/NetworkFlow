from manim import *
import numpy as np
from typing import Optional, Union, Tuple

class DataPacket(VGroup):
    """
    A visual representation of data/flow packets moving through a network.
    """
    
    def __init__(
        self,
        value: int = 1,
        radius: float = 0.2, 
        color: str = YELLOW,
        position: Optional[np.ndarray] = None,
        with_value_label: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Create the circle
        self.circle = Circle(radius=radius, color=color, fill_opacity=0.8)
        self.add(self.circle)
        
        self.value = value
        self.with_value_label = with_value_label
        
        # Add the value label if requested
        if with_value_label:
            self.value_label = Text(str(value), font_size=16, color=BLACK)
            self.add(self.value_label)
        
        # Set position if provided
        if position is not None:
            self.move_to(position)
    
    def set_value(self, new_value: int):
        """Update the packet's value"""
        self.value = new_value
        if self.with_value_label:
            # Remove old label and create new one
            self.remove(self.value_label)
            self.value_label = Text(str(new_value), font_size=16, color=BLACK)
            self.add(self.value_label)
    
    def split(
        self, 
        scene: Scene, 
        positions: list, 
        values: Optional[list] = None, 
        run_time: float = 1.0
    ) -> list:
        """
        Split this packet into multiple packets.
        
        Args:
            scene: The manim scene
            positions: List of positions for the new packets
            values: Optional list of values for the new packets
                    (if None, the original value is split evenly)
            run_time: Animation run time
            
        Returns:
            List of new DataPacket objects
        """
        if values is None:
            # Split the value evenly
            value_per_packet = max(1, self.value // len(positions))
            values = [value_per_packet] * len(positions)
        
        # Create new packets
        new_packets = []
        for pos, val in zip(positions, values):
            packet = DataPacket(
                value=val, 
                color=self.circle.get_color(),
                with_value_label=self.with_value_label
            ).move_to(self.get_center())
            new_packets.append(packet)
        
        # Animate the split
        scene.remove(self)
        scene.add(*new_packets)
        
        animations = []
        for packet, pos in zip(new_packets, positions):
            animations.append(packet.animate.move_to(pos))
        
        scene.play(*animations, run_time=run_time)
        
        return new_packets