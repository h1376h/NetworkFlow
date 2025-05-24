from manim import *
import random
import numpy as np
from wsn.algorithms import FlowNetwork, greedy_max_flow, find_all_paths
from wsn.visualization import FlowNetworkVisualizer, DataPacket
from wsn.utils import create_layered_flow_network

class GreedyMaxFlowScene(Scene):
    def __init__(self):
        super().__init__()
        random.seed(42)  # For reproducibility
        self.sink_flow_label = None # Initialize attribute for sink flow label
        self.sink_flow_value = 0
        
    def construct(self):
        # Add title and explanation
        title = Text("Greedy Maximum Flow Algorithm", font_size=40)
        title.to_edge(UP)
        explanation = VGroup(
            Text("Finding the maximum flow in a network", font_size=28),
            Text("using a simple greedy approach", font_size=28)
        ).arrange(DOWN, buff=0.3)
        explanation.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(explanation))
        self.wait()
        self.play(
            title.animate.scale(0.6).to_corner(UL),
            FadeOut(explanation)
        )

        # Create a layered flow network for demonstration
        nodes_per_layer = [1, 2, 3, 1]  # Source, two middle layers, sink
        nodes, edges = create_layered_flow_network(
            num_layers=4,
            nodes_per_layer=nodes_per_layer,
            min_capacity=2,
            max_capacity=10,
            x_spread=11,
            y_spread=3
        )
        
        network = FlowNetwork(nodes, edges)
        
        # Create a visualizer
        visualizer = FlowNetworkVisualizer(self)
        
        # Visualize the network
        visualizer.create_from_flow_network(network)
        
        # Ensure all edge labels are properly initialized and added to scene
        for idx, edge in enumerate(visualizer.edges):
            if edge.flow_label not in self.mobjects:
                self.add(edge.flow_label)
            visualizer.edge_labels[idx] = edge.flow_label
        
        # Initialize sink flow label
        self.sink_flow_label = Text(f"{self.sink_flow_value}", font_size=24, color=WHITE)
        if visualizer.nodes:
            self.sink_flow_label.move_to(visualizer.nodes[-1].get_center() + UP * 0.5) # Position above sink
            self.add(self.sink_flow_label)
            
        # Explain source and sink
        source_explanation = Text(
            "Source: Starting point of flow",
            font_size=24,
            color=GREEN_A
        ).to_edge(DOWN)
        
        self.play(
            Write(source_explanation),
            Flash(visualizer.nodes[0], color=GREEN, flash_radius=0.8),
            run_time=1.5
        )
        self.wait()
        self.play(FadeOut(source_explanation))
        
        sink_explanation = Text(
            "Sink: Destination of flow",
            font_size=24,
            color=RED_A
        ).to_edge(DOWN)
        
        self.play(
            Write(sink_explanation),
            Flash(visualizer.nodes[-1], color=RED, flash_radius=0.8),
            run_time=1.5
        )
        self.wait()
        self.play(FadeOut(sink_explanation))
        
        # Explain capacities
        capacity_explanation = Text(
            "Edge capacities: Maximum flow allowed through each edge",
            font_size=24,
            color=BLUE_A
        ).to_edge(DOWN)
        
        self.play(Write(capacity_explanation))

        original_char_colors_and_mobjects = [] # Stores (char_mobject, original_color)

        for edge_label in visualizer.edge_labels:
            if isinstance(edge_label, Text) and hasattr(edge_label, 'text') and '/' in edge_label.text:
                text_content = edge_label.text
                slash_char_index = -1
                try:
                    slash_char_index = text_content.index('/')
                except ValueError:
                    self.play(Indicate(edge_label), run_time=0.3)
                    continue

                capacity_anims = []
                other_char_anims = []

                # Ensure submobjects are available and match text length (common for simple Text)
                if hasattr(edge_label, 'submobjects') and len(edge_label.submobjects) == len(text_content):
                    for i in range(len(edge_label.submobjects)):
                        char_mob = edge_label.submobjects[i]
                        # Save original color for restoration
                        original_char_colors_and_mobjects.append((char_mob, char_mob.get_color()))

                        if i > slash_char_index: # Character is part of the capacity
                            capacity_anims.append(char_mob.animate.set_color(YELLOW))
                            # Add a wiggle to the capacity part for emphasis
                            capacity_anims.append(Wiggle(char_mob, scale_value=1.3, rotation_angle=0.02*TAU))
                        else: # Character is part of flow or the slash
                            # Wiggle other parts slightly less
                            other_char_anims.append(Wiggle(char_mob, scale_value=1.1, rotation_angle=0.01*TAU))
                    
                    if capacity_anims or other_char_anims:
                        self.play(*capacity_anims, *other_char_anims, run_time=0.8)
                    else:
                        self.play(Indicate(edge_label), run_time=0.3) # Fallback
                else:
                    self.play(Indicate(edge_label), run_time=0.3) # Fallback if submobject structure is not as expected
            else:
                self.play(Indicate(edge_label), run_time=0.3)
        
        self.wait(0.5) # Hold the view with highlighted capacities

        restore_anims = []
        for mobj, color in original_char_colors_and_mobjects:
            restore_anims.append(mobj.animate.set_color(color))
        
        if restore_anims:
            self.play(AnimationGroup(*restore_anims, lag_ratio=0.05), FadeOut(capacity_explanation), run_time=0.5)
        else:
            self.play(FadeOut(capacity_explanation))
        
        # Find all possible paths from source to sink
        source = 0
        sink = len(network.nodes) - 1
        all_paths = find_all_paths(network, source, sink)
        
        # Sort paths by their initial capacity (greedy approach)
        all_paths.sort(key=lambda p: network.get_path_capacity(p), reverse=True)
        
        # Prepare Mobjects for path description and capacity, update them in loop
        path_desc_mobj = Text("", font_size=24).to_edge(DOWN)
        capacity_text_mobj = Text("", font_size=24).next_to(path_desc_mobj, UP, buff=0.2)
        
        # Process each path
        for path_idx, path in enumerate(all_paths):
            path_capacity = network.get_path_capacity(path)
            if path_capacity <= 0:
                continue  # Skip paths with no remaining capacity
            
            # Show and highlight current path
            path_desc_mobj.become(
                Text(f"Path {path_idx + 1}: {' → '.join(map(str, path))}", font_size=24)
            )
            path_desc_mobj.to_edge(DOWN)
            
            capacity_text_mobj.become(
                Text(f"Path capacity: {path_capacity}", font_size=24)
            )
            capacity_text_mobj.next_to(path_desc_mobj, UP, buff=0.2)
            
            self.play(
                Write(path_desc_mobj),
                Write(capacity_text_mobj)
            )
            
            # Highlight the path
            path_edges = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                for edge_idx, (from_idx, to_idx, _) in enumerate(network.edges):
                    if from_idx == u and to_idx == v:
                        path_edges.append(visualizer.edges[edge_idx])
            
            # Highlight edges in the path
            self.play(*[edge.animate.set_color(YELLOW) for edge in path_edges])
            
            # --- Highlight the bottleneck edge ---
            # Find bottleneck (min residual capacity) edge index
            bottleneck_val = float('inf')
            bottleneck_idxs = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                res_cap = network.get_residual_capacity(u, v)
                if res_cap < bottleneck_val:
                    bottleneck_val = res_cap
                    bottleneck_idxs = [i]
                elif res_cap == bottleneck_val:
                    bottleneck_idxs.append(i)
            bottleneck_edges = [path_edges[i] for i in bottleneck_idxs]
            if bottleneck_edges:
                self.play(*[edge.animate.set_color(ORANGE) for edge in bottleneck_edges], run_time=0.5)
            
            # Create data packet with the flow value
            packet = DataPacket(value=path_capacity, color=YELLOW)
            
            # Create a list of points for the packet to follow
            path_points = [nodes[node_idx] for node_idx in path]
            
            # Add packet to scene at the source node position
            packet.move_to(path_points[0])
            self.add(packet)
            
            # Ensure path_points has at least two points for animation
            if len(path_points) > 1:
                # Animate packet movement along each segment of the path
                for i in range(1, len(path_points)):
                    # Move to next node
                    self.play(
                        packet.animate.move_to(path_points[i]),
                        run_time=0.5
                    )
                    
                    # Flash at node
                    if i < len(path_points) - 1:  # Don't flash at the last node yet
                        self.play(
                            Flash(
                                Circle(radius=0.3, color=BLUE).move_to(path_points[i]),
                                color=YELLOW,
                                flash_radius=0.5
                            ),
                            run_time=0.2
                        )
                
                # Flash at the sink node
                self.play(
                    Flash(
                        Circle(radius=0.3, color=BLUE).move_to(path_points[-1]),
                        color=YELLOW,
                        flash_radius=0.5
                    ),
                    run_time=0.2
                )
            
            # Smoother packet disappearance at sink
            self.play(packet.animate.scale(0.1).set_opacity(0), run_time=0.3)
            self.remove(packet)
            
            # Update flow along the path
            visualizer.update_flow(path, path_capacity)
            
            # Update sink flow label
            current_flow_val = network.get_total_flow(source) # This is the new total flow
            self.sink_flow_value = current_flow_val
            self.sink_flow_label.become(
                Text(f"{self.sink_flow_value}", font_size=24, color=WHITE)
                .move_to(self.sink_flow_label.get_center())
            )
            self.play(Indicate(self.sink_flow_label, color=YELLOW))
            
            # Reset edge colors
            self.play(*[edge.animate.set_color(BLUE) for edge in path_edges])
            
            # Show current total flow
            flow_text = Text(
                f"Current total flow: {current_flow_val}",
                font_size=28,
                color=YELLOW
            ).next_to(title, DOWN, buff=0.5)
            
            self.play(Write(flow_text))
            self.wait()
            self.play(FadeOut(flow_text), FadeOut(path_desc_mobj), FadeOut(capacity_text_mobj))
                    
        # Show final maximum flow
        visualizer.show_max_flow(source=source)
        
        self.wait(2)


if __name__ == "__main__":
    scene = GreedyMaxFlowScene()
    scene.render()