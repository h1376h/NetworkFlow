from manim import *
import numpy as np
from typing import List, Dict, Optional
import heapq

class PathFinder:
    """Handles path finding within the network"""
    @staticmethod
    def create_adjacency_list(node_positions: List[np.ndarray], 
                            connections: List['NetworkConnection']) -> Dict[int, List[int]]:
        """Create adjacency list representation of the network"""
        adj_list = {i: [] for i in range(len(node_positions) + 1)}  # +1 for sink
        
        for conn in connections:
            start = tuple(conn.get_start())
            end = tuple(conn.get_end())
            
            start_idx = next(i for i, pos in enumerate(node_positions) 
                           if np.allclose(pos, start))
            end_idx = next(i for i, pos in enumerate(node_positions) 
                          if np.allclose(pos, end))
            
            adj_list[start_idx].append(end_idx)
            adj_list[end_idx].append(start_idx)
            
        return adj_list

    @staticmethod
    def find_path(start_idx: int, end_idx: int, adj_list: Dict[int, List[int]], 
                 node_positions: List[np.ndarray]) -> Optional[List[int]]:
        """Find path between two nodes using A* algorithm"""
        def heuristic(node1_idx: int, node2_idx: int) -> float:
            return np.linalg.norm(node_positions[node1_idx] - node_positions[node2_idx])
        
        open_set = [(0 + heuristic(start_idx, end_idx), 0, start_idx, [start_idx])]
        closed_set = set()
        
        while open_set:
            _, cost_so_far, current, path = heapq.heappop(open_set)
            
            if current == end_idx:
                return path
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            for next_idx in adj_list[current]:
                if next_idx not in closed_set:
                    new_cost = cost_so_far + heuristic(current, next_idx)
                    priority = new_cost + heuristic(next_idx, end_idx)
                    heapq.heappush(open_set, (priority, new_cost, next_idx, path + [next_idx]))
        
        return None

    @staticmethod
    def find_path_to_sink(start_pos: np.ndarray, node_positions: List[np.ndarray], 
                         connections: List['NetworkConnection'], sink_pos: np.ndarray) -> Optional[List[int]]:
        """Find path from a node to the sink node"""
        # Find start node index
        start_idx = next(i for i, pos in enumerate(node_positions) 
                        if np.allclose(pos, start_pos))
        
        # Create adjacency list
        adj_list = PathFinder.create_adjacency_list(node_positions, connections)
        
        # Find path to sink (index 0)
        path = PathFinder.find_path(start_idx, 0, adj_list, node_positions)
        
        return path

    @staticmethod
    def find_path_within_cluster(start_idx: int, head_idx: int, 
                               cluster_nodes: List[int], 
                               node_positions: List[np.ndarray],
                               communication_range: float) -> List[int]:
        """Find direct path from cluster member to cluster head"""
        if start_idx not in cluster_nodes or head_idx not in cluster_nodes:
            return []
        
        distance = np.linalg.norm(node_positions[start_idx] - node_positions[head_idx])
        if distance <= communication_range:
            return [start_idx, head_idx]
        
        return []

    @staticmethod
    def find_ch_path(start_idx: int, sink_idx: int, cluster_heads: List[int], 
                     node_positions: List[np.ndarray], comm_range: float) -> List[int]:
        """Find path from cluster head to sink through CH backbone network"""
        if start_idx not in cluster_heads and start_idx != sink_idx:
            return []

        ch_adj_list = {idx: [] for idx in [sink_idx] + cluster_heads}
        
        for ch_idx in cluster_heads:
            if np.linalg.norm(node_positions[ch_idx] - node_positions[sink_idx]) <= comm_range:
                ch_adj_list[ch_idx].append(sink_idx)
                ch_adj_list[sink_idx].append(ch_idx)
            
            for other_ch in cluster_heads:
                if ch_idx != other_ch:
                    if np.linalg.norm(node_positions[ch_idx] - node_positions[other_ch]) <= comm_range:
                        ch_adj_list[ch_idx].append(other_ch)
                        ch_adj_list[other_ch].append(ch_idx)

        def heuristic(node1_idx: int, node2_idx: int) -> float:
            return np.linalg.norm(node_positions[node1_idx] - node_positions[node2_idx])
        
        open_set = [(0 + heuristic(start_idx, sink_idx), 0, start_idx, [start_idx])]
        closed_set = set()
        
        while open_set:
            _, cost_so_far, current, path = heapq.heappop(open_set)
            
            if current == sink_idx:
                return path
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            for next_idx in ch_adj_list[current]:
                if next_idx not in closed_set:
                    new_cost = cost_so_far + heuristic(current, next_idx)
                    priority = new_cost + heuristic(next_idx, sink_idx)
                    heapq.heappush(open_set, (priority, new_cost, next_idx, path + [next_idx]))
        
        return [] 