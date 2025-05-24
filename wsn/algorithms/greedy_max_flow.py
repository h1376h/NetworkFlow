from typing import List, Set, Tuple
from wsn.algorithms.flow_network import FlowNetwork

def find_all_paths(network: FlowNetwork, source: int, sink: int, path: List[int] = None, visited: Set[int] = None) -> List[List[int]]:
    """Find all simple paths from source to sink with available capacity"""
    if path is None:
        path = [source]
    if visited is None:
        visited = set([source])
    
    if source == sink:
        return [path]
    
    paths = []
    for u, v, _ in network.get_outgoing_edges(source):
        if v not in visited and network.get_residual_capacity(u, v) > 0:
            visited.add(v)
            new_paths = find_all_paths(network, v, sink, path + [v], visited)
            paths.extend(new_paths)
            visited.remove(v)
    
    return paths

def greedy_max_flow(network: FlowNetwork, source: int, sink: int) -> int:
    """
    Implements a greedy maximum flow algorithm.
    
    Args:
        network: The flow network
        source: Source node index
        sink: Sink node index
        
    Returns:
        The maximum flow value achieved
    """
    # Find all possible paths from source to sink
    all_paths = find_all_paths(network, source, sink)
    
    # Sort paths by their initial capacity (greedy approach)
    all_paths.sort(key=lambda p: network.get_path_capacity(p), reverse=True)
    
    # Process each path
    for path in all_paths:
        path_capacity = network.get_path_capacity(path)
        if path_capacity <= 0:
            continue  # Skip paths with no remaining capacity
            
        # Augment flow along the path
        network.augment_flow(path, path_capacity)
    
    # Calculate and return the total flow
    return network.get_total_flow(source) 