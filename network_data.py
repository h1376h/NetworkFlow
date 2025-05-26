import collections
from typing import List, Tuple, Dict, Any

class NetworkData:
    """Data structure for network flow graph"""
    
    def __init__(self, vertices: List[int], edges: List[Tuple[int, int, int]], 
                 source: int, sink: int, layout: Dict[int, List[float]] = None):
        self.vertices = vertices
        self.edges = edges  # (u, v, capacity)
        self.source = source
        self.sink = sink
        self.layout = layout or self._generate_default_layout()
        
        # Build adjacency list and capacity dict
        self.capacities = collections.defaultdict(int)
        self.adj = collections.defaultdict(list)
        self.flow = collections.defaultdict(int)
        
        for u, v, cap in edges:
            self.capacities[(u, v)] = cap
            self.adj[u].append(v)
    
    def _generate_default_layout(self) -> Dict[int, List[float]]:
        """Generate a simple default layout if none provided"""
        layout = {}
        n = len(self.vertices)
        for i, v in enumerate(self.vertices):
            x = (i % 5) * 2 - 4  # Arrange in rows of 5
            y = (i // 5) * 2 - 2
            layout[v] = [x, y, 0]
        return layout
    
    def get_residual_capacity(self, u: int, v: int) -> int:
        """Get residual capacity of edge (u, v)"""
        return self.capacities[(u, v)] - self.flow.get((u, v), 0)
    
    def update_flow(self, u: int, v: int, flow_delta: int):
        """Update flow on edge (u, v)"""
        self.flow[(u, v)] += flow_delta
    
    def reset_flow(self):
        """Reset all flows to zero"""
        self.flow.clear()

# Example network configurations
class NetworkConfigs:
    @staticmethod
    def get_default_network() -> NetworkData:
        vertices = list(range(1, 11))
        edges = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        layout = {
            1: [-3,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }
        return NetworkData(vertices, edges, source=1, sink=10, layout=layout)