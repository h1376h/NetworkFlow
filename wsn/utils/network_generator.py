from manim import *
import numpy as np
import random
from typing import List, Tuple
from ..nodes.network_node import NetworkNode
from ..nodes.network_connection import NetworkConnection

class NetworkGenerator:
    """Handles network topology generation"""
    @staticmethod
    def generate_random_position(width: float, height: float) -> np.ndarray:
        """Generate a random position within the given dimensions"""
        return np.array([
            random.uniform(-width/2, width/2),
            random.uniform(-height/2, height/2),
            0
        ])

    @staticmethod
    def is_valid_position(pos: np.ndarray, existing_positions: List[np.ndarray], 
                         min_distance: float) -> bool:
        """Check if a position is valid (maintains minimum distance from existing nodes)"""
        return all(np.linalg.norm(pos - existing_pos) >= min_distance 
                  for existing_pos in existing_positions)

    @staticmethod
    def find_valid_position(width: float, height: float, min_distance: float, 
                          existing_positions: List[np.ndarray], max_attempts: int = 50) -> np.ndarray:
        """Find a valid position for a new node"""
        for _ in range(max_attempts):
            pos = NetworkGenerator.generate_random_position(width, height)
            if NetworkGenerator.is_valid_position(pos, existing_positions, min_distance):
                return pos
        return NetworkGenerator.generate_random_position(width, height)

    @staticmethod
    def generate_cluster_positions(num_clusters: int, radius: float = 3.0) -> List[np.ndarray]:
        """Generate evenly spaced cluster center positions"""
        positions = []
        for i in range(num_clusters):
            angle = (i * TAU / num_clusters) + PI/6  # Offset for better visualization
            pos = np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0
            ])
            positions.append(pos)
        return positions

    @staticmethod
    def create_connections(node_positions: List[np.ndarray], 
                         communication_range: float) -> List[NetworkConnection]:
        """Create connections between nodes within communication range"""
        connections = []
        for i, pos1 in enumerate(node_positions):
            for j, pos2 in enumerate(node_positions[i+1:], i+1):
                if np.linalg.norm(pos1 - pos2) <= communication_range:
                    connections.append(NetworkConnection(pos1, pos2))
        return connections

    @staticmethod
    def generate_network(width: float, height: float, num_nodes: int, 
                        min_distance: float, communication_range: float) -> Tuple[List[NetworkNode], List[NetworkConnection]]:
        """Generate a network with randomly placed nodes and connections"""
        # Create sink node at center
        sink_pos = ORIGIN
        sink_node = NetworkNode(sink_pos, 0, is_sink=True)
        node_positions = [sink_pos]
        nodes = [sink_node]

        # Generate sensor nodes
        for i in range(num_nodes - 1):  # -1 because we already have sink node
            pos = NetworkGenerator.find_valid_position(
                width, height, min_distance, node_positions
            )
            node = NetworkNode(pos, len(nodes))
            nodes.append(node)
            node_positions.append(pos)

        # Create connections
        connections = NetworkGenerator.create_connections(
            node_positions, communication_range
        )

        return nodes, connections 