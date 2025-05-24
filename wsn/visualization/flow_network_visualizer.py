from manim import *
import numpy as np
from typing import List, Tuple, Dict, Optional, Callable
from wsn.algorithms.flow_network import FlowNetwork
from wsn.nodes import NetworkNode
from wsn.visualization.data_packet import DataPacket
from wsn.visualization.flow_edge import FlowEdge
from wsn.algorithms.ford_fulkerson import ford_fulkerson_with_paths
from wsn.algorithms.greedy_max_flow import greedy_max_flow

class FlowNetworkVisualizer:
    """
    Visualizer for network flow algorithms with 3blue1brown-style animations.
    """
    def __init__(self, scene: Scene):
        self.scene = scene
        self.nodes = []
        self.edges = []
        self.node_labels = []
        self.edge_labels = []
        self.flow_network = None
        self.algorithm_history = []
        self.current_step = 0
        self.animation_speed = 1.0
        self.title_text = None
        self.info_text = None
        self.residual_network = None
        self.residual_edges = []
    
    def create_from_flow_network(
        self, 
        flow_network: FlowNetwork, 
        node_colors: Optional[List] = None, 
        node_labels_text: Optional[List[str]] = None,
        node_radius: float = 0.3,
        animation_speed: float = 1.0,
        title: Optional[str] = None
    ) -> Tuple[List[NetworkNode], List[FlowEdge]]:
        """
        Create a visual representation of a flow network.
        
        Args:
            flow_network: The flow network to visualize
            node_colors: Optional list of colors for each node
            node_labels_text: Optional list of labels for each node
            node_radius: Radius of network nodes
            animation_speed: Speed factor for animations
            title: Optional title for the visualization
            
        Returns:
            Tuple of (nodes, edges) manim objects
        """
        self.flow_network = flow_network
        self.animation_speed = animation_speed
        
        # Display title if provided
        if title:
            self.title_text = Text(title, font_size=36).to_edge(UP)
            self.scene.play(Write(self.title_text))
        
        # Set default colors if not provided
        if node_colors is None:
            node_colors = []
            for i in range(len(flow_network.nodes)):
                if i == 0:  # Source
                    node_colors.append(GREEN)
                elif i == len(flow_network.nodes) - 1:  # Sink
                    node_colors.append(RED)
                else:
                    node_colors.append(BLUE)
        
        # Set default labels if not provided
        if node_labels_text is None:
            node_labels_text = []
            for i in range(len(flow_network.nodes)):
                if i == 0:
                    node_labels_text.append("Source")
                elif i == len(flow_network.nodes) - 1:
                    node_labels_text.append("Sink")
                else:
                    node_labels_text.append(f"Node {i}")
        
        # Create nodes
        self.nodes = []
        self.node_labels = []
        for i, pos in enumerate(flow_network.nodes):
            node = NetworkNode(position=pos, node_id=i)
            node.set_color(node_colors[i])
            self.nodes.append(node)
            
            # Add node label
            label = Text(node_labels_text[i], font_size=20).next_to(node, DOWN, buff=0.2)
            self.node_labels.append(label)
            
            self.scene.play(
                Create(node), 
                Write(label), 
                run_time=0.5 / animation_speed
            )
        
        # Create edges
        self.edges = []
        self.edge_labels = []
        for u, v, cap in flow_network.edges:
            start_pos = flow_network.nodes[u]
            end_pos = flow_network.nodes[v]
            
            # Get current flow
            current_flow = flow_network.flow.get((u, v), 0)
            
            # Create flow edge
            edge = FlowEdge(
                start_point=start_pos,
                end_point=end_pos,
                capacity=cap,
                current_flow=current_flow
            )
            
            self.edges.append(edge)
            self.edge_labels.append(edge.flow_label)
            
            self.scene.play(
                Create(edge), 
                FadeIn(edge.flow_label), 
                run_time=0.3 / animation_speed
            )
        
        # Create info text area
        self.info_text = Text("", font_size=24).to_edge(DOWN)
        
        return self.nodes, self.edges
    
    def highlight_path(
        self, 
        path: List[int], 
        color: str = YELLOW, 
        animate_packet: bool = True,
        path_capacity: Optional[int] = None,
        run_time: float = 1.0,
        show_capacity_text: bool = True
    ):
        """
        Highlight a path in the network.
        
        Args:
            path: List of node indices representing a path
            color: Color to highlight the path
            animate_packet: Whether to animate a packet flowing along the path
            path_capacity: Optional capacity to display (if None, will be computed)
            run_time: Animation run time
            show_capacity_text: Whether to show the path capacity text
        """
        # Find edges along the path
        path_edges = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            for idx, (edge_u, edge_v, _) in enumerate(self.flow_network.edges):
                if edge_u == u and edge_v == v:
                    path_edges.append(self.edges[idx])
        
        # Highlight edges
        original_colors = [edge.get_color() for edge in path_edges]
        self.scene.play(
            *[edge.animate.set_color(color) for edge in path_edges],
            run_time=run_time
        )
        
        # Compute path capacity if not provided
        if path_capacity is None and self.flow_network:
            path_capacity = self.flow_network.get_path_capacity(path)
        
        # Show path capacity
        capacity_text = None
        if path_capacity is not None and show_capacity_text:
            capacity_text = Text(
                f"Path capacity: {path_capacity}",
                font_size=24
            ).to_edge(DOWN)
            
            self.scene.play(Write(capacity_text))
            self.scene.wait(0.5)
        
        # Animate packet if requested
        if animate_packet and path_capacity:
            # Get path points
            path_points = [self.flow_network.nodes[node_idx] for node_idx in path]
            
            # Create and animate packet
            packet = DataPacket(
                value=path_capacity, 
                color=color, 
                position=path_points[0]
            )
            self.scene.add(packet)
            
            # Animate packet flow along the path
            # Time per segment
            segment_time = (run_time * 2) / (len(path_points) - 1) if len(path_points) > 1 else (run_time * 2)

            for i in range(1, len(path_points)):
                # Create movement animation
                move_anim = packet.animate.move_to(path_points[i])
                
                # Add pulse effect
                pulse_anim = Succession(
                    packet.circle.animate(run_time=segment_time/4).scale(1.3),
                    packet.circle.animate(run_time=segment_time/4).scale(1/1.3)
                )
                
                # Play the animation
                self.scene.play(move_anim, pulse_anim, run_time=segment_time)
                
                # Flash at node (using node properties from the visualizer)
                node_to_flash = self.nodes[path[i]] # Get the NetworkNode object
                self.scene.play(Flash(
                    Circle(radius=node_to_flash.radius, color=node_to_flash.get_color()).move_to(path_points[i]),
                    color=packet.circle.get_color(), # Packet's color
                    flash_radius=node_to_flash.radius * 1.5,
                    run_time=0.25
                ))
            
            self.scene.remove(packet)
        
        # Reset edge colors
        self.scene.play(
            *[edge.animate.set_color(original_color) for edge, original_color in zip(path_edges, original_colors)],
            run_time=run_time / 2
        )
        
        if capacity_text:
            self.scene.play(FadeOut(capacity_text))
            
        return path_capacity
    
    def update_flow(self, path: List[int], flow_value: int, run_time: float = 1.0):
        """
        Update the flow along a path and visualize the change.
        
        Args:
            path: List of node indices representing a path
            flow_value: Amount of flow to add along the path
            run_time: Animation run time
        """
        if not self.flow_network:
            return
            
        # Update flow in the flow network
        self.flow_network.augment_flow(path, flow_value)
        
        # Update the visual representation
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            
            for idx, (edge_u, edge_v, _) in enumerate(self.flow_network.edges):
                if edge_u == u and edge_v == v:
                    edge = self.edges[idx]
                    new_flow = self.flow_network.flow[(u, v)]
                    
                    # Remove old label from edge_labels list
                    if idx < len(self.edge_labels) and self.edge_labels[idx] == edge.flow_label:
                        old_label = self.edge_labels[idx]
                        if old_label in self.scene.mobjects:
                            self.scene.remove(old_label)
                    
                    # Animate flow update
                    edge.animate_flow_update(
                        new_flow=new_flow,
                        scene=self.scene,
                        run_time=run_time
                    )
                    
                    # Update edge_labels list with new label
                    self.edge_labels[idx] = edge.flow_label
    
    def show_max_flow(self, source: int = 0, sink: int = -1):
        """
        Display the maximum flow value achieved.
        
        Args:
            source: Index of the source node
            sink: Index of the sink node (default: last node)
        """
        if not self.flow_network:
            return
            
        if sink == -1:
            sink = len(self.flow_network.nodes) - 1
            
        # Calculate total flow
        total_flow = self.flow_network.get_total_flow(source)
        
        # Show result
        result_text = Text(
            f"Maximum flow: {total_flow}",
            font_size=36,
            color=YELLOW
        ).to_edge(DOWN)
        
        self.scene.play(Write(result_text))
        self.scene.wait(1)
        
        # Highlight source and sink
        self.scene.play(
            Flash(self.nodes[source], color=GREEN, flash_radius=0.8),
            Flash(self.nodes[sink], color=RED, flash_radius=0.8),
            run_time=1.5
        )
        
        return total_flow
    
    def run_ford_fulkerson(self, source: int = 0, sink: int = -1, step_by_step: bool = True, run_time: float = 1.0):
        """
        Run and visualize the Ford-Fulkerson algorithm.
        
        Args:
            source: Source node index
            sink: Sink node index (default: last node)
            step_by_step: Whether to show each step or just the final result
            run_time: Animation run time per step
            
        Returns:
            The maximum flow value
        """
        if not self.flow_network:
            return 0
            
        if sink == -1:
            sink = len(self.flow_network.nodes) - 1
        
        # Reset flow if needed
        if any(flow > 0 for flow in self.flow_network.flow.values()):
            # Reset flow in the network
            for u, v in self.flow_network.flow:
                self.flow_network.flow[(u, v)] = 0
                
            # Reset flow in the visualization
            for edge in self.edges:
                edge.set_flow(0)
                self.scene.add(edge.flow_label)
        
        # Show algorithm title
        algo_title = Text("Ford-Fulkerson Algorithm", font_size=32, color=YELLOW).to_edge(UP)
        self.scene.play(Write(algo_title))
        
        # Run Ford-Fulkerson with path tracking
        max_flow, paths = ford_fulkerson_with_paths(self.flow_network, source, sink)
        
        if step_by_step:
            # Show each augmenting path
            for i, (path, capacity) in enumerate(paths):
                # Show step information
                step_text = Text(f"Step {i+1}: Find augmenting path", font_size=24).to_edge(DOWN)
                self.scene.play(Write(step_text))
                
                # Highlight the path
                self.highlight_path(path, color=YELLOW, path_capacity=capacity, run_time=run_time, show_capacity_text=False)
                
                # Update step information
                self.scene.play(
                    Transform(
                        step_text,
                        Text(f"Step {i+1}: Augment flow by {capacity}", font_size=24).to_edge(DOWN)
                    )
                )
                
                # Update flow along the path
                self.update_flow(path, capacity, run_time=run_time)
                
                # Wait and remove step text
                self.scene.wait(0.5)
                self.scene.play(FadeOut(step_text))
        else:
            # Just show the final result
            for path, capacity in paths:
                self.update_flow(path, capacity, run_time=run_time/len(paths))
        
        # Show the maximum flow
        self.scene.play(FadeOut(algo_title))
        return self.show_max_flow(source, sink)
    
    def run_greedy_max_flow(self, source: int = 0, sink: int = -1, run_time: float = 1.0):
        """
        Run and visualize the Greedy Maximum Flow algorithm.
        
        Args:
            source: Source node index
            sink: Sink node index (default: last node)
            run_time: Animation run time per step
            
        Returns:
            The maximum flow value
        """
        if not self.flow_network:
            return 0
            
        if sink == -1:
            sink = len(self.flow_network.nodes) - 1
        
        # Reset flow if needed
        if any(flow > 0 for flow in self.flow_network.flow.values()):
            # Reset flow in the network
            for u, v in self.flow_network.flow:
                self.flow_network.flow[(u, v)] = 0
                
            # Reset flow in the visualization
            for edge in self.edges:
                edge.set_flow(0)
                self.scene.add(edge.flow_label)
        
        # Show algorithm title
        algo_title = Text("Greedy Maximum Flow Algorithm", font_size=32, color=YELLOW).to_edge(UP)
        self.scene.play(Write(algo_title))
        
        # Find all paths and sort by capacity (for visualization)
        from wsn.algorithms.greedy_max_flow import find_all_paths
        all_paths = find_all_paths(self.flow_network, source, sink)
        
        # Sort paths by capacity (greedy approach)
        path_with_capacities = [(path, self.flow_network.get_path_capacity(path)) for path in all_paths]
        path_with_capacities.sort(key=lambda x: x[1], reverse=True)
        
        # Show each path in order of capacity
        for i, (path, capacity) in enumerate(path_with_capacities):
            if capacity <= 0:
                continue  # Skip paths with no capacity
                
            # Show step information
            step_text = Text(f"Path {i+1}: Capacity = {capacity}", font_size=24).to_edge(DOWN)
            self.scene.play(Write(step_text))
            
            # Highlight the path
            self.highlight_path(path, color=YELLOW, path_capacity=capacity, run_time=run_time, show_capacity_text=False)
            
            # Update flow along the path
            self.update_flow(path, capacity, run_time=run_time)
            
            # Wait and remove step text
            self.scene.wait(0.5)
            self.scene.play(FadeOut(step_text))
        
        # Show the maximum flow
        self.scene.play(FadeOut(algo_title))
        return self.show_max_flow(source, sink)
    
    def show_residual_network(self, run_time: float = 1.0):
        """
        Visualize the residual network based on current flow.
        
        Args:
            run_time: Animation run time
        """
        if not self.flow_network:
            return
            
        # Create residual network visualization
        residual_title = Text("Residual Network", font_size=32, color=BLUE).to_edge(UP)
        self.scene.play(Write(residual_title))
        
        # Create residual edges
        self.residual_edges = []
        
        for idx, (u, v, cap) in enumerate(self.flow_network.edges):
            # Forward edge (residual capacity)
            current_flow = self.flow_network.flow.get((u, v), 0)
            residual_cap = cap - current_flow
            
            if residual_cap > 0:
                # Create forward residual edge
                forward_edge = DashedArrow(
                    start=self.flow_network.nodes[u],
                    end=self.flow_network.nodes[v],
                    buff=0.3,
                    color=BLUE_D
                )
                
                # Create label
                forward_label = Text(
                    f"{residual_cap}",
                    font_size=16,
                    color=BLUE_D
                ).next_to(forward_edge, UP, buff=0.1)
                
                self.residual_edges.append((forward_edge, forward_label))
                self.scene.play(
                    Create(forward_edge),
                    Write(forward_label),
                    run_time=run_time/2
                )
            
            # Backward edge (flow that can be canceled)
            if current_flow > 0:
                # Create backward residual edge
                backward_edge = DashedArrow(
                    start=self.flow_network.nodes[v],
                    end=self.flow_network.nodes[u],
                    buff=0.3,
                    color=RED_D
                )
                
                # Create label
                backward_label = Text(
                    f"{current_flow}",
                    font_size=16,
                    color=RED_D
                ).next_to(backward_edge, DOWN, buff=0.1)
                
                self.residual_edges.append((backward_edge, backward_label))
                self.scene.play(
                    Create(backward_edge),
                    Write(backward_label),
                    run_time=run_time/2
                )
        
        # Wait and provide option to remove
        self.scene.wait(2)
        
        # Remove residual network
        self.scene.play(FadeOut(residual_title))
        for edge, label in self.residual_edges:
            self.scene.play(
                FadeOut(edge),
                FadeOut(label),
                run_time=run_time/len(self.residual_edges)
            )
        
        self.residual_edges = []
    
    def show_min_cut(self, source: int = 0, sink: int = -1, run_time: float = 1.0):
        """
        Visualize the minimum cut in the network.
        
        Args:
            source: Source node index
            sink: Sink node index (default: last node)
            run_time: Animation run time
        """
        if not self.flow_network:
            return
            
        if sink == -1:
            sink = len(self.flow_network.nodes) - 1
        
        # Find the min cut (nodes reachable from source in residual network)
        from collections import deque
        
        # BFS to find reachable nodes
        visited = [False] * len(self.flow_network.nodes)
        queue = deque([source])
        visited[source] = True
        
        while queue:
            current = queue.popleft()
            
            # Try all possible edges from current node
            for u, v, _ in self.flow_network.edges:
                if u == current and not visited[v] and self.flow_network.get_residual_capacity(u, v) > 0:
                    queue.append(v)
                    visited[v] = True
        
        # Show min cut title
        min_cut_title = Text("Minimum Cut", font_size=32, color=PURPLE).to_edge(UP)
        self.scene.play(Write(min_cut_title))
        
        # Highlight source side nodes
        source_side = [i for i, v in enumerate(visited) if v]
        sink_side = [i for i, v in enumerate(visited) if not v]
        
        # Highlight source side
        self.scene.play(
            *[self.nodes[i].animate.set_color(GREEN_E) for i in source_side],
            run_time=run_time
        )
        
        # Highlight sink side
        self.scene.play(
            *[self.nodes[i].animate.set_color(RED_E) for i in sink_side],
            run_time=run_time
        )
        
        # Find cut edges (edges from source side to sink side)
        cut_edges = []
        cut_capacity = 0
        
        for idx, (u, v, cap) in enumerate(self.flow_network.edges):
            if visited[u] and not visited[v]:
                cut_edges.append(self.edges[idx])
                cut_capacity += cap
        
        # Highlight cut edges
        self.scene.play(
            *[edge.animate.set_color(PURPLE).set_stroke_width(6) for edge in cut_edges],
            run_time=run_time
        )
        
        # Show cut capacity
        cut_text = Text(
            f"Min Cut Capacity: {cut_capacity}",
            font_size=28,
            color=PURPLE
        ).to_edge(DOWN)
        
        self.scene.play(Write(cut_text))
        self.scene.wait(2)
        
        # Reset colors
        self.scene.play(
            *[node.animate.set_color(BLUE) for node in self.nodes],
            *[edge.animate.set_color(WHITE).set_stroke_width(4) for edge in self.edges],
            FadeOut(min_cut_title),
            FadeOut(cut_text),
            run_time=run_time
        )
        
        # Reset source and sink colors
        self.nodes[source].set_color(GREEN)
        self.nodes[sink].set_color(RED)
        
        return cut_capacity
    
    def compare_algorithms(self, source: int = 0, sink: int = -1, run_time: float = 1.0):
        """
        Compare different max flow algorithms on the same network.
        
        Args:
            source: Source node index
            sink: Sink node index (default: last node)
            run_time: Animation run time per step
        """
        if not self.flow_network:
            return
            
        if sink == -1:
            sink = len(self.flow_network.nodes) - 1
        
        # Create a copy of the flow network for each algorithm
        import copy
        ff_network = copy.deepcopy(self.flow_network)
        greedy_network = copy.deepcopy(self.flow_network)
        
        # Save original network
        original_network = self.flow_network
        
        # Show comparison title
        compare_title = Text("Algorithm Comparison", font_size=32, color=YELLOW).to_edge(UP)
        self.scene.play(Write(compare_title))
        
        # Run Ford-Fulkerson
        self.flow_network = ff_network
        ff_title = Text("Ford-Fulkerson Algorithm", font_size=24).to_edge(DOWN)
        self.scene.play(Write(ff_title))
        
        # Reset visualization
        for edge in self.edges:
            edge.set_flow(0)
            self.scene.add(edge.flow_label)
        
        # Run algorithm (simplified visualization)
        max_flow_ff, paths_ff = ford_fulkerson_with_paths(self.flow_network, source, sink)
        
        for path, capacity in paths_ff:
            self.update_flow(path, capacity, run_time=run_time/len(paths_ff))
        
        # Show result
        ff_result = Text(
            f"Ford-Fulkerson Max Flow: {max_flow_ff}",
            font_size=24,
            color=BLUE
        ).to_corner(DL)
        
        self.scene.play(
            Transform(ff_title, ff_result)
        )
        
        # Run Greedy Max Flow
        self.flow_network = greedy_network
        greedy_title = Text("Greedy Max Flow Algorithm", font_size=24).to_edge(DOWN)
        self.scene.play(Write(greedy_title))
        
        # Reset visualization
        for edge in self.edges:
            edge.set_flow(0)
            self.scene.add(edge.flow_label)
        
        # Run algorithm
        max_flow_greedy = greedy_max_flow(self.flow_network, source, sink)
        
        # Update visualization to match final state
        for u, v in self.flow_network.flow:
            flow_value = self.flow_network.flow[(u, v)]
            if flow_value > 0:
                for idx, (edge_u, edge_v, _) in enumerate(self.flow_network.edges):
                    if edge_u == u and edge_v == v:
                        self.edges[idx].set_flow(flow_value)
                        self.scene.add(self.edges[idx].flow_label)
        
        # Show result
        greedy_result = Text(
            f"Greedy Max Flow: {max_flow_greedy}",
            font_size=24,
            color=GREEN
        ).to_corner(DR)
        
        self.scene.play(
            Transform(greedy_title, greedy_result)
        )
        
        # Show comparison
        if max_flow_ff == max_flow_greedy:
            comparison = Text(
                "Both algorithms found the same maximum flow!",
                font_size=28,
                color=YELLOW
            ).to_edge(DOWN)
        else:
            better_algo = "Ford-Fulkerson" if max_flow_ff > max_flow_greedy else "Greedy"
            comparison = Text(
                f"{better_algo} found a better solution!",
                font_size=28,
                color=YELLOW
            ).to_edge(DOWN)
        
        self.scene.play(Write(comparison))
        self.scene.wait(2)
        
        # Clean up
        self.scene.play(
            FadeOut(compare_title),
            FadeOut(ff_title),
            FadeOut(greedy_title),
            FadeOut(comparison)
        )
        
        # Restore original network
        self.flow_network = original_network
        
        # Reset visualization
        for edge in self.edges:
            edge.set_flow(0)
            self.scene.add(edge.flow_label)
        
        return max_flow_ff, max_flow_greedy
    
    def animate_wave_propagation(self, source: int = 0, num_waves: int = 3, wave_speed: float = 0.5):
        """
        Animate wave propagation through the network from source.
        
        Args:
            source: Source node index
            num_waves: Number of waves to propagate
            wave_speed: Speed of wave propagation
        """
        if not self.flow_network:
            return
            
        from wsn.visualization.wave_utils import create_circular_wave
        
        # Show wave title
        wave_title = Text("Network Wave Propagation", font_size=32, color=BLUE).to_edge(UP)
        self.scene.play(Write(wave_title))
        
        # Create and animate waves
        for _ in range(num_waves):
            # Create wave at source
            wave = create_circular_wave(
                center=self.flow_network.nodes[source],
                color=BLUE_A,
                max_radius=10,
                opacity_function=lambda t: 1 - t
            )
            
            self.scene.play(
                Create(wave, run_time=wave_speed)
            )
            self.scene.play(
                FadeOut(wave, run_time=wave_speed/2)
            )
            
            self.scene.wait(0.2)
        
        # Clean up
        self.scene.play(FadeOut(wave_title))