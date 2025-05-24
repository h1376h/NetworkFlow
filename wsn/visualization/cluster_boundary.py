from manim import *
import numpy as np
from typing import List

class ClusterBoundary(VMobject):
    """Creates a boundary around cluster nodes with configurable padding styles"""
    def __init__(self, positions: List[np.ndarray], head_position: np.ndarray, 
                 padding: float = 0.3, color: str = GREEN_A,
                 node_sizes: dict = None):
        super().__init__()
        
        # Include head position in boundary calculation
        all_positions = positions + [head_position]
        
        self._create_boundary(all_positions, padding)
        
        # Set visual properties
        self.set_stroke(color=color, width=2)
        self.set_fill(color=color, opacity=0.1)

    def _create_boundary(self, all_positions: List[np.ndarray], padding: float):
        """Creates boundary using simple padding method"""
        if len(all_positions) == 1:
            # Single node - create a circle
            circle = Circle(radius=padding)
            circle.move_to(all_positions[0])
            self.append_points(circle.get_points())
            
        elif len(all_positions) == 2:
            # Two nodes - create elongated oval/capsule shape
            p1, p2 = all_positions
            center = (p1 + p2) / 2
            distance = np.linalg.norm(p2 - p1)
            
            # Create base circle points
            circle = Circle(radius=padding)
            # Scale to create oval
            circle.stretch_to_fit_width(distance + 2*padding)
            # Rotate to align with nodes
            angle = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
            circle.rotate(angle)
            # Move to center
            circle.move_to(center)
            self.append_points(circle.get_points())
            
        else:
            # Three or more nodes - use convex hull
            points_2d = np.array([[p[0], p[1]] for p in all_positions])
            hull = self._compute_convex_hull(points_2d)
            
            # Add padding to hull points
            center = np.mean(hull, axis=0)
            padded_hull = []
            for point in hull:
                vector = point - center
                if np.any(vector):  # Avoid division by zero
                    vector = vector / np.linalg.norm(vector)
                    padded_point = point + vector * padding
                    padded_hull.append(padded_point)
            
            # Convert hull points to 3D and set as vertices
            vertices = [np.array([x, y, 0]) for x, y in padded_hull]
            self.set_points_as_corners([*vertices, vertices[0]])  # Close the shape

    def _compute_convex_hull(self, points: np.ndarray) -> np.ndarray:
        """Compute convex hull using Graham Scan algorithm"""
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0
            return 1 if val > 0 else 2

        # Find bottom-most point (and leftmost if tied)
        start = min(points, key=lambda p: (p[1], p[0]))
        
        # Sort points by polar angle and distance from start
        sorted_points = sorted(
            points,
            key=lambda p: (
                np.arctan2(p[1] - start[1], p[0] - start[0]),
                np.linalg.norm(p - start)
            )
        )
        
        # Build convex hull
        stack = [start]
        for point in sorted_points[1:]:
            while len(stack) > 1 and orientation(stack[-2], stack[-1], point) != 2:
                stack.pop()
            stack.append(point)
        
        return np.array(stack) 