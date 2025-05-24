from typing import List, Dict, Tuple, Optional
from wsn.algorithms.flow_network import FlowNetwork
from collections import deque

def find_augmenting_path_bfs(network: FlowNetwork, source: int, sink: int) -> Optional[List[int]]:
    """
    Find an augmenting path from source to sink using Breadth-First Search.
    
    Args:
        network: Flow network
        source: Source node index
        sink: Sink node index
        
    Returns:
        A path from source to sink or None if no path exists
    """
    # Initialize BFS
    visited = [False] * len(network.nodes)
    queue = deque([source])
    visited[source] = True
    
    # Store parent nodes to reconstruct path
    parent = [-1] * len(network.nodes)
    
    # BFS loop
    while queue and not visited[sink]:
        current = queue.popleft()
        
        # Try all possible edges from current node
        for u, v, _ in network.edges:
            if u == current and not visited[v] and network.get_residual_capacity(u, v) > 0:
                queue.append(v)
                visited[v] = True
                parent[v] = current
    
    # Check if we reached the sink
    if not visited[sink]:
        return None
    
    # Reconstruct path
    path = []
    current = sink
    while current != source:
        path.append(current)
        current = parent[current]
    path.append(source)
    path.reverse()
    
    return path

def ford_fulkerson(network: FlowNetwork, source: int, sink: int) -> int:
    """
    Implements the Ford-Fulkerson algorithm for maximum flow.
    
    Args:
        network: The flow network
        source: Source node index
        sink: Sink node index
        
    Returns:
        The maximum flow value
    """
    # Initialize all flows to 0 (already done in network initialization)
    
    # While there is an augmenting path
    path = find_augmenting_path_bfs(network, source, sink)
    while path:
        # Find the minimum residual capacity along the path
        path_capacity = network.get_path_capacity(path)
        
        # Augment flow along the path
        network.augment_flow(path, path_capacity)
        
        # Find next augmenting path
        path = find_augmenting_path_bfs(network, source, sink)
    
    # Return the total flow
    return network.get_total_flow(source)

def ford_fulkerson_with_paths(network: FlowNetwork, source: int, sink: int) -> Tuple[int, List[Tuple[List[int], int]]]:
    """
    Implements the Ford-Fulkerson algorithm for maximum flow with path tracking.
    
    Args:
        network: The flow network
        source: Source node index
        sink: Sink node index
        
    Returns:
        Tuple of (max_flow, paths) where paths is a list of (path, capacity) tuples
    """
    # Initialize all flows to 0 (already done in network initialization)
    paths = []
    
    # While there is an augmenting path
    path = find_augmenting_path_bfs(network, source, sink)
    while path:
        # Find the minimum residual capacity along the path
        path_capacity = network.get_path_capacity(path)
        
        # Record this path and its capacity
        paths.append((path.copy(), path_capacity))
        
        # Augment flow along the path
        network.augment_flow(path, path_capacity)
        
        # Find next augmenting path
        path = find_augmenting_path_bfs(network, source, sink)
    
    # Return the total flow and paths
    return network.get_total_flow(source), paths 