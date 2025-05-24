import numpy as np
from typing import List, Tuple, Dict, Optional
import random

def create_random_flow_network(num_nodes: int, density: float = 0.3, 
                              min_capacity: int = 1, max_capacity: int = 10,
                              x_range: Tuple[float, float] = (-5, 5), 
                              y_range: Tuple[float, float] = (-3, 3)) -> Tuple[List[np.ndarray], List[Tuple[int, int, int]]]:
    """
    Create a random flow network with given parameters.
    
    Args:
        num_nodes: Number of nodes in the network
        density: Edge density (0-1) controlling how connected the network is
        min_capacity: Minimum edge capacity
        max_capacity: Maximum edge capacity
        x_range: Range of x-coordinates for node positions
        y_range: Range of y-coordinates for node positions
        
    Returns:
        Tuple of (nodes, edges) where:
            - nodes is a list of node positions
            - edges is a list of (from_idx, to_idx, capacity) tuples
    """
    # Create node positions
    nodes = []
    for i in range(num_nodes):
        # Position nodes strategically - source on left, sink on right
        if i == 0:  # Source
            x = x_range[0]
            y = 0
        elif i == num_nodes - 1:  # Sink
            x = x_range[1]
            y = 0
        else:
            # Distribute remaining nodes between source and sink
            x = x_range[0] + (x_range[1] - x_range[0]) * (i / (num_nodes - 1))
            y = random.uniform(y_range[0], y_range[1])
        
        nodes.append(np.array([x, y, 0]))
    
    # Create edges
    edges = []
    for i in range(num_nodes - 1):  # From source to node before sink
        for j in range(i + 1, num_nodes):  # To nodes after current
            if i == 0 or j == num_nodes - 1 or random.random() < density:
                # Always connect source and sink to nearby nodes
                capacity = random.randint(min_capacity, max_capacity)
                edges.append((i, j, capacity))
    
    return nodes, edges

def get_path_description(path: List[int]) -> str:
    """
    Generate a human-readable description of a path.
    
    Args:
        path: List of node indices representing a path
        
    Returns:
        A string describing the path (e.g. "0 → 1 → 3 → 5")
    """
    return " → ".join(map(str, path))

def create_layered_flow_network(num_layers: int, nodes_per_layer: List[int], 
                              min_capacity: int = 1, max_capacity: int = 10,
                              x_spread: float = 10, y_spread: float = 6) -> Tuple[List[np.ndarray], List[Tuple[int, int, int]]]:
    """
    Create a layered flow network with given parameters.
    
    Args:
        num_layers: Number of layers (including source and sink)
        nodes_per_layer: List specifying how many nodes in each layer
        min_capacity: Minimum edge capacity
        max_capacity: Maximum edge capacity
        x_spread: Total width of the network
        y_spread: Total height of the network
        
    Returns:
        Tuple of (nodes, edges) where:
            - nodes is a list of node positions
            - edges is a list of (from_idx, to_idx, capacity) tuples
    """
    assert len(nodes_per_layer) == num_layers, "Must specify nodes for each layer"
    assert nodes_per_layer[0] == 1, "First layer (source) must have exactly 1 node"
    assert nodes_per_layer[-1] == 1, "Last layer (sink) must have exactly 1 node"
    
    # Create node positions
    nodes = []
    node_indices = {}  # Maps (layer, position) to node index
    node_idx = 0
    
    for layer in range(num_layers):
        layer_nodes = nodes_per_layer[layer]
        x = (layer / (num_layers - 1)) * x_spread - (x_spread / 2)
        
        for pos in range(layer_nodes):
            if layer_nodes == 1:
                y = 0
            else:
                y = (pos / (layer_nodes - 1)) * y_spread - (y_spread / 2)
            
            nodes.append(np.array([x, y, 0]))
            node_indices[(layer, pos)] = node_idx
            node_idx += 1
    
    # Create edges
    edges = []
    for layer in range(num_layers - 1):
        current_layer_nodes = nodes_per_layer[layer]
        next_layer_nodes = nodes_per_layer[layer + 1]
        
        for pos in range(current_layer_nodes):
            current_idx = node_indices[(layer, pos)]
            
            # Connect to all nodes in next layer
            for next_pos in range(next_layer_nodes):
                next_idx = node_indices[(layer + 1, next_pos)]
                capacity = random.randint(min_capacity, max_capacity)
                edges.append((current_idx, next_idx, capacity))
    
    return nodes, edges 