from typing import List, Tuple, Dict

class FlowNetwork:
    """Represents a flow network with nodes and edges"""
    def __init__(self, nodes: List, edges: List[Tuple[int, int, int]]):
        self.nodes = nodes  # List of node positions
        self.edges = edges  # List of (from_idx, to_idx, capacity) tuples
        self.flow = {(u, v): 0 for (u, v, _) in edges}  # Current flow on each edge
    
    def get_residual_capacity(self, u: int, v: int) -> int:
        """Get remaining capacity on edge (u, v)"""
        for edge in self.edges:
            if edge[0] == u and edge[1] == v:
                return edge[2] - self.flow.get((u, v), 0)
        return 0
    
    def get_outgoing_edges(self, node_idx: int) -> List[Tuple[int, int, int]]:
        """Get all edges going out from node_idx"""
        return [(u, v, c) for (u, v, c) in self.edges if u == node_idx]
    
    def get_path_capacity(self, path: List[int]) -> int:
        """Get the minimum residual capacity along a path"""
        if len(path) < 2: # If path has less than 2 nodes, it's not a valid path for flow
            return 0
        
        min_capacity = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            min_capacity = min(min_capacity, self.get_residual_capacity(u, v))
        return min_capacity
    
    def augment_flow(self, path: List[int], flow_value: int) -> None:
        """Augment flow along a path by flow_value"""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            self.flow[(u, v)] = self.flow.get((u, v), 0) + flow_value
            
    def get_total_flow(self, source: int) -> int:
        """Calculate the total flow out of the source node"""
        return sum(self.flow.get((source, v), 0) for v in range(len(self.nodes)))