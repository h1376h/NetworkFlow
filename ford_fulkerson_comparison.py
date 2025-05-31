"""
Ford-Fulkerson Method Comparison

This module provides a visualization comparing different implementations of the Ford-Fulkerson method
for solving maximum flow problems. It demonstrates why Ford-Fulkerson is considered a method
rather than a specific algorithm by comparing several variants:

1. Basic Ford-Fulkerson with DFS path finding
2. Edmonds-Karp (Ford-Fulkerson with BFS path finding)
3. Capacity Scaling approach

The visualization is created using Manim (Mathematical Animation Engine) in the style of 3Blue1Brown.
"""

from manim import *
import numpy as np

# Utility function to lighten colors for visualization
def lighten_color(color, factor=0.5):
    """
    Lightens the given color by mixing it with white.
    
    Parameters:
    color : str or array-like
        Color to lighten in any format accepted by manim
    factor : float
        Factor to lighten by (0.0 to 1.0, where 0.0 is no change and 1.0 is white)
    
    Returns:
    str : Lightened color in hex format
    """
    if isinstance(color, str):
        # Convert hex or named color to RGB
        rgb = color_to_rgb(color)
    else:
        rgb = color
    
    # Mix with white (1, 1, 1)
    lightened = [c + (1 - c) * factor for c in rgb]
    
    # Convert back to hex
    return rgb_to_hex(lightened)

# Utility function to rotate a vector by an angle
def rotate_vector_2d(vector, angle):
    """
    Rotates a 2D vector by the given angle.
    
    Parameters:
    vector : np.ndarray
        The 2D vector to rotate
    angle : float
        The angle in radians to rotate by
    
    Returns:
    np.ndarray : The rotated vector
    """
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    
    x, y = vector[0], vector[1]
    return np.array([
        x * cos_theta - y * sin_theta,
        x * sin_theta + y * cos_theta,
        0  # Preserve z-coordinate if present
    ])

class FordFulkersonComparison(Scene):
    """Explains why Ford-Fulkerson is a method and not an algorithm, by comparing different implementations."""
    
    def construct(self):
        # Using 3Blue1Brown style with darker background and more vibrant colors
        self.camera.background_color = "#1C1C1C"  # Darker background like 3b1b
        
        # Create title with animation
        title = Text("Ford-Fulkerson: A Method, Not an Algorithm", font_size=40)
        title.to_edge(UP, buff=0.7)
        
        # Animate title with fancy reveal
        self.play(
            Write(title, run_time=1.5)
        )
        self.wait(0.5)
        
        # Underline for title (3b1b style)
        underline = Line(
            start=title.get_corner(DL) + LEFT * 0.1,
            end=title.get_corner(DR) + RIGHT * 0.1,
            color=YELLOW_C,
            stroke_width=3
        )
        self.play(Create(underline))
        self.wait(0.5)
        
        # Main explanation with stepwise revealing
        explanation_text = [
            "Ford-Fulkerson provides a framework for finding maximum flow",
            "by repeatedly finding augmenting paths until no more exist.",
            "Different path-finding strategies lead to distinct algorithms",
            "with varying performance characteristics."
        ]
        
        explanation_group = VGroup()
        for i, line in enumerate(explanation_text):
            text = Text(line, font_size=24, color=LIGHT_GRAY)
            explanation_group.add(text)
        
        explanation_group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation_group.next_to(underline, DOWN, buff=0.5)
        
        # Reveal explanation line by line
        for line in explanation_group:
            self.play(FadeIn(line, shift=UP*0.3), run_time=0.7)
            self.wait(0.3)
        
        self.wait(1)
        
        # Create a simple network example (3b1b style visualization)
        network_example, nodes = self.create_network_example()
        network_example.scale(0.9)  # Slightly smaller
        
        # Position the network example below the explanation text
        network_example.next_to(explanation_group, DOWN, buff=0.8)
        
        # Animate the network appearance
        self.play(
            FadeIn(network_example, scale=1.1),
            run_time=1.2
        )
        self.wait(0.8)
        
        # Animate an augmenting path to illustrate the concept
        self.animate_augmenting_path(network_example, nodes)
        self.wait(0.5)
        
        # Fade out everything including title and underline before showing the tree structure
        self.play(
            FadeOut(explanation_group),
            FadeOut(network_example),
            FadeOut(title),
            FadeOut(underline),
            run_time=1.0
        )
        
        # Core concept graphic
        ff_core_concept = VGroup()
        
        # Central box for core concept
        core_box = RoundedRectangle(
            width=6,
            height=1.5,
            corner_radius=0.2,
            fill_color=BLUE_E,
            fill_opacity=0.6,
            stroke_color=BLUE_C,
            stroke_width=2
        )
        
        # Core text
        core_text = Text("Find augmenting paths & push flow until no more paths exist", 
                         font_size=18, color=WHITE).move_to(core_box)
        core_text.scale_to_fit_width(core_box.width - 0.4)
        
        ff_core_concept.add(core_box, core_text)
        ff_core_concept.move_to(ORIGIN).shift(UP * 1.5)
        
        self.play(
            FadeIn(ff_core_concept, scale=1.1),
            run_time=1.2
        )
        self.wait(0.5)
        
        # Create tree structure showing the three algorithm variants
        algorithms = [
            {
                "name": "Basic Ford-Fulkerson (DFS)",
                "description": "Uses depth-first search\nto find augmenting paths",
                "key_points": ["Simple implementation", "O(|E|·f) time complexity", "May be slow on large networks"],
                "color": RED_D
            },
            {
                "name": "Edmonds-Karp (BFS)",
                "description": "Uses breadth-first search\nfor shortest augmenting paths",
                "key_points": ["Finds shortest paths first", "O(|V|·|E|²) time complexity", "More efficient on typical graphs"],
                "color": GREEN_D
            },
            {
                "name": "Capacity Scaling",
                "description": "Prioritizes paths with\nlarge residual capacities",
                "key_points": ["Considers high-capacity edges first", "O(|E|²·log(U)) time complexity", "Efficient on networks with large capacities"],
                "color": BLUE_D
            }
        ]
        
        algo_boxes = VGroup()
        algo_descriptions = VGroup()
        arrows = VGroup()
        
        # Layout calculations
        box_width = 3.8
        box_height = 1.0
        box_spacing = 4.2
        start_x = -(box_spacing) * (len(algorithms) - 1) / 2
        
        for i, algo in enumerate(algorithms):
            # Algorithm box
            x_pos = start_x + i * box_spacing
            algo_box = RoundedRectangle(
                width=box_width,
                height=box_height,
                corner_radius=0.2,
                fill_color=algo["color"],
                fill_opacity=0.6,
                stroke_color=lighten_color(algo["color"], 0.3),
                stroke_width=2
            )
            algo_box.move_to([x_pos, -0.5, 0])
            
            algo_name = Text(algo["name"], font_size=20, color=WHITE)
            algo_name.scale_to_fit_width(box_width - 0.3)
            algo_name.move_to(algo_box)
            
            # Description below box
            description = Text(algo["description"], font_size=18, color=LIGHT_GRAY)
            description.scale_to_fit_width(box_width)
            description.next_to(algo_box, DOWN, buff=0.3)
            
            # Arrow from core concept to algorithm
            arrow = Arrow(
                core_box.get_edge_center(DOWN) + DOWN * 0.1,
                algo_box.get_edge_center(UP) + UP * 0.1,
                color=lighten_color(algo["color"], 0.3),
                buff=0.1,
                stroke_width=2,
                tip_length=0.2
            )
            
            algo_boxes.add(VGroup(algo_box, algo_name))
            algo_descriptions.add(description)
            arrows.add(arrow)
        
        # Animate the arrows from core concept to algorithms
        self.play(
            *[Create(arrow) for arrow in arrows],
            run_time=1.5
        )
        
        # Animate the algorithm boxes
        self.play(
            *[FadeIn(box, scale=1.1) for box in algo_boxes],
            run_time=1.0
        )
        
        # Animate descriptions
        self.play(
            *[FadeIn(desc, shift=UP*0.2) for desc in algo_descriptions],
            run_time=0.8
        )
        
        self.wait(1.5)
        
        # Store all tree elements for later reuse
        algorithm_tree = VGroup(ff_core_concept, algo_boxes, algo_descriptions, arrows)
        
        # Fade out tree structure to prepare for detailed demonstrations
        self.play(
            FadeOut(algorithm_tree),
            run_time=1.0
        )
        
        # Demonstrate each algorithm in detail (one by one)
        self.demonstrate_dfs_algorithm()
        self.demonstrate_bfs_algorithm()
        self.demonstrate_capacity_scaling()
        
        # After individual demonstrations, bring back the algorithm tree with detailed comparison
        # First show the core concept again
        self.play(
            FadeIn(ff_core_concept, scale=1.1),
            run_time=1.2
        )
        
        # Create detailed algorithm comparison with key points and diagrams
        algo_key_points = VGroup()
        
        # Animate arrows and algorithm boxes
        self.play(
            *[Create(arrow) for arrow in arrows],
            run_time=1.5
        )
        
        self.play(
            *[FadeIn(box, scale=1.1) for box in algo_boxes],
            run_time=1.0
        )
        
        # Animate descriptions
        self.play(
            *[FadeIn(desc, shift=UP*0.2) for desc in algo_descriptions],
            run_time=0.8
        )
        
        # Improved layout for key points
        for i, algo in enumerate(algorithms):
            # Key points below description
            key_points_group = VGroup()
            for j, point in enumerate(algo["key_points"]):
                bullet = Text("•", font_size=16, color=lighten_color(algo["color"], 0.3))
                point_text = Text(point, font_size=16, color=LIGHT_GRAY)
                point_group = VGroup(bullet, point_text).arrange(RIGHT, buff=0.1, aligned_edge=UP)
                key_points_group.add(point_group)
            
            key_points_group.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            
            # Position key points directly below the description using relative positioning
            key_points_group.next_to(algo_descriptions[i], DOWN, buff=0.3)
            
            algo_key_points.add(key_points_group)
        
        # Animate key points for each algorithm with improved animation
        self.play(
            *[FadeIn(points, shift=RIGHT*0.3) for points in algo_key_points],
            run_time=1.2
        )
        
        self.wait(1.0)
        
        # Group all elements of the tree for easier fade out
        algorithm_tree = VGroup(
            ff_core_concept, algo_boxes, algo_descriptions, 
            arrows, algo_key_points
        )
        
        # Fade out the tree to show algorithm diagrams separately
        self.play(
            FadeOut(algorithm_tree),
            run_time=1.5
        )
        
        # Now show algorithm comparisons in fullscreen
        # Create a title for the algorithm visualizations
        compare_title = Text("Algorithm Comparison", font_size=36, color=YELLOW_C)  # Increased font size
        compare_title.to_edge(UP, buff=0.5)
        
        self.play(
            FadeIn(compare_title, shift=UP*0.3),
            run_time=0.8
        )
        
        # Reposition diagrams for fullscreen display with better spacing
        fullscreen_diagrams = VGroup()
        diagram_titles = VGroup()
        
        # Use relative positioning for consistent spacing
        algorithm_names = ["DFS Approach", "BFS (Edmonds-Karp)", "Capacity Scaling"]
        algorithm_colors = [RED_D, GREEN_D, BLUE_D]
        
        # Calculate horizontal positions with wider spacing
        # Use wider spacing to prevent overlapping
        width = config.frame_width - 0.5
        positions = [LEFT * (width/3), ORIGIN, RIGHT * (width/3)]
        
        # Create and position each diagram
        for i in range(3):
            # Create a new copy of the diagram at a better size
            if i == 0:
                new_diagram = self.create_dfs_diagram()
            elif i == 1:
                new_diagram = self.create_bfs_diagram()
            else:
                new_diagram = self.create_scaling_diagram()
            
            # Scale appropriately for fullscreen - make larger
            new_diagram.scale(0.8)  # Increased from 0.7
            
            # Position in a row across the screen with more space between them
            new_diagram.move_to(positions[i] + DOWN * 0.5)
            
            # Create title for each diagram with larger font
            diagram_title = Text(algorithm_names[i], font_size=28, color=algorithm_colors[i])  # Increased font
            # Always position title directly above its diagram
            diagram_title.next_to(new_diagram, UP, buff=0.3)
            
            fullscreen_diagrams.add(new_diagram)
            diagram_titles.add(diagram_title)
        
        # Animate algorithm diagrams one by one with emphasizing effects
        for i in range(len(fullscreen_diagrams)):
            self.play(
                FadeIn(diagram_titles[i], shift=UP*0.3),
                run_time=0.6
            )
            
            diagram_copy = fullscreen_diagrams[i].copy()
            # Start with diagram at slightly larger scale
            diagram_copy.scale(1.2)
            diagram_copy.set_opacity(0.5)
            
            # Animate appearance with fancy effect
            self.play(
                Transform(diagram_copy, fullscreen_diagrams[i]),
                run_time=0.8
            )
            self.remove(diagram_copy)
            self.add(fullscreen_diagrams[i])
            
            self.wait(0.3)
        
        self.wait(1.5)
        
        # Group all elements for easier fade out
        comparison_elements = VGroup(
            compare_title, fullscreen_diagrams, diagram_titles
        )
        
        # Fade out the comparison view
        self.play(
            FadeOut(comparison_elements),
            run_time=1.5
        )
        
        # Performance comparison chart (3b1b style)
        perf_chart = self.create_performance_chart()
        
        self.play(
            FadeIn(perf_chart),
            run_time=1.5
        )
        
        self.wait(2.0)
        
        # Fade out performance chart
        self.play(
            FadeOut(perf_chart),
            run_time=1.0
        )
        
        # Conclusion banner at bottom
        conclusion_banner = RoundedRectangle(
            width=12,
            height=0.8,
            corner_radius=0.2,
            fill_color="#2C2C2C",
            fill_opacity=1,
            stroke_color=YELLOW_C,
            stroke_width=2
        ).to_edge(DOWN, buff=0.4)
        
        conclusion_text = Text(
            "All variants guarantee optimal max flow, but with different efficiency characteristics",
            font_size=20,
            color=YELLOW_C
        )
        conclusion_text.scale_to_fit_width(conclusion_banner.width - 0.5)
        conclusion_text.move_to(conclusion_banner)
        
        self.play(
            FadeIn(conclusion_banner),
            Write(conclusion_text),
            run_time=1.5
        )
        
        self.wait(1.5)
        
        # Final fade out - explicitly fade out everything to ensure no elements remain
        final_elements = VGroup(conclusion_banner, conclusion_text, title, underline)
        
        self.play(
            FadeOut(final_elements),
            run_time=1.5
        )
        
        self.wait(1)

    def create_network_example(self, title_text="Network Example", scale_factor=1.0, custom_position=None):
        """Create a simple network visualization example in 3b1b style."""
        network = VGroup()
        
        # Create nodes
        node_radius = 0.25
        node_positions = {
            "s": LEFT * 2,
            "a": UP + LEFT * 0.5,
            "b": UP + RIGHT * 0.5,
            "c": DOWN + LEFT * 0.5,
            "d": DOWN + RIGHT * 0.5,
            "t": RIGHT * 2
        }
        
        nodes = {}
        for label, pos in node_positions.items():
            circle = Circle(radius=node_radius, fill_color=BLUE_E, fill_opacity=0.8, stroke_color=BLUE_B)
            text = Text(label, font_size=20, color=WHITE)
            node = VGroup(circle, text)
            node.move_to(pos)
            nodes[label] = node
            network.add(node)
        
        # Create edges with capacities
        edges = [
            ("s", "a", "10"),
            ("s", "c", "10"),
            ("a", "b", "4"),
            ("a", "c", "2"),
            ("a", "d", "8"),
            ("b", "t", "10"),
            ("c", "d", "9"),
            ("d", "b", "6"),
            ("d", "t", "10")
        ]
        
        for u, v, cap in edges:
            start = nodes[u].get_center()
            end = nodes[v].get_center()
            
            # Create arrow
            arrow = Arrow(
                start=start, 
                end=end,
                buff=node_radius,
                stroke_width=2,
                color=GRAY,
                tip_length=0.15
            )
            
            # Use rotate_vector_2d instead of .rotate()
            direction = normalize(end - start)
            offset = rotate_vector_2d(direction, PI/2) * 0.15
            cap_text = Text(cap, font_size=16, color=LIGHT_GRAY)
            cap_text.move_to((start + end) / 2 + offset)
            
            network.add(arrow, cap_text)
        
        # Add title label
        label = Text(title_text, font_size=28, color=YELLOW_C)
        label.next_to(network, UP, buff=0.5)
        network.add(label)
        
        # Scale if needed
        if scale_factor != 1.0:
            network.scale(scale_factor)
        
        # Position if specified
        if custom_position is not None:
            network.move_to(custom_position)
        else:
            # Center the network by default
            network.move_to(ORIGIN)
        
        return network, nodes
    
    def animate_augmenting_path(self, network, nodes):
        """Animate an augmenting path in the network example."""
        # Create a simple path highlight animation
        path_edges = [("s", "a"), ("a", "b"), ("b", "t")]
        
        # Create path highlight
        path_arrows = VGroup()
        for u, v in path_edges:
            if u in nodes and v in nodes:
                start = nodes[u].get_center()
                end = nodes[v].get_center()
                
                arrow = Arrow(
                    start=start, 
                    end=end,
                    buff=0.25,  # node radius
                    stroke_width=4,
                    color=YELLOW,
                    tip_length=0.15
                )
                path_arrows.add(arrow)
        
        # Animate path highlighting
        self.play(
            LaggedStart(*[GrowArrow(arrow) for arrow in path_arrows], lag_ratio=0.3),
            run_time=1.5
        )
        
        # Animate flow
        flow_pulses = []
        for arrow in path_arrows:
            pulse = arrow.copy().set_color(BLUE_A).set_stroke(width=6)
            flow_pulses.append(ShowPassingFlash(pulse, time_width=0.5, run_time=1.5))
        
        self.play(LaggedStart(*flow_pulses, lag_ratio=0.2), run_time=2)
        
        # Clean up
        self.play(FadeOut(path_arrows), run_time=0.8)

    def create_dfs_diagram(self):
        """Create a DFS visualization in 3b1b style with enhanced visuals."""
        diagram = VGroup()
        
        # Create a small tree to illustrate DFS
        tree_levels = 3
        node_radius = 0.25  # Increased from 0.2
        level_height = 0.8  # Increased from 0.7
        node_width = 0.7    # Increased from 0.6
        
        nodes = []
        edges = []
        
        # Create nodes in a tree structure
        for level in range(tree_levels):
            level_nodes = []
            nodes_in_level = min(2**level, 4)  # Cap width for visibility
            
            for i in range(nodes_in_level):
                x_pos = (i - (nodes_in_level - 1) / 2) * node_width
                y_pos = -level * level_height
                
                # Create node with glow effect (3b1b style)
                node = Circle(
                    radius=node_radius, 
                    fill_color=RED_E, 
                    fill_opacity=0.7, 
                    stroke_color=RED_A,
                    stroke_width=2
                )
                node.move_to([x_pos, y_pos, 0])
                
                # Add subtle glow (3b1b style)
                glow = node.copy().set_fill(opacity=0).set_stroke(RED_A, width=5, opacity=0.3)
                glow.scale(1.2)
                
                node_group = VGroup(glow, node)
                level_nodes.append(node_group)
                
                # Connect to parent if not root
                if level > 0:
                    parent_idx = min(i // 2, len(nodes[level-1]) - 1)
                    parent = nodes[level-1][parent_idx]
                    
                    edge = Line(
                        parent[1].get_center(),  # Use the actual node, not the glow
                        node.get_center(),
                        stroke_width=2,
                        stroke_opacity=0.7,
                        color=GRAY_C
                    )
                    edges.append(edge)
            
            nodes.append(level_nodes)
        
        # Add edges first (for proper z-ordering)
        for edge in edges:
            diagram.add(edge)
        
        # Add nodes
        for level_nodes in nodes:
            for node in level_nodes:
                diagram.add(node)
        
        # Highlight DFS path - this creates the depth-first traversal effect
        dfs_path = VGroup()
        # Path goes straight down to showcase depth-first nature
        for i in range(tree_levels-1):
            if i < len(nodes) - 1 and nodes[i] and nodes[i+1]:
                start_node = nodes[i][0][1]  # Get the actual node, not the glow
                end_node = nodes[i+1][0][1]
                
                path_edge = Line(
                    start_node.get_center(),
                    end_node.get_center(),
                    stroke_width=4,
                    color=RED_A
                )
                dfs_path.add(path_edge)
        
        diagram.add(dfs_path)
        
        # Add label
        label = Text("DFS: Depth-First Search", font_size=26, color=RED_C)  # Increased from 22
        label.next_to(diagram, UP, buff=0.3)
        diagram.add(label)
        
        # Add small explanation text
        explanation = Text("Explores as deep as possible before backtracking", 
                           font_size=18, color=LIGHT_GRAY)  # Increased from 16
        explanation.next_to(label, UP, buff=0.2)
        diagram.add(explanation)
        
        # Center the diagram
        diagram.move_to(ORIGIN)
        
        return diagram

    def create_bfs_diagram(self):
        """Create a BFS visualization in enhanced 3b1b style."""
        diagram = VGroup()
        
        # Create a small tree to illustrate BFS
        tree_levels = 3
        node_radius = 0.25  # Increased from 0.2
        level_height = 0.8  # Increased from 0.7
        node_width = 0.7    # Increased from 0.6
        
        nodes = []
        edges = []
        level_groups = []
        
        # Create nodes in a tree structure
        for level in range(tree_levels):
            level_nodes = []
            level_group = VGroup()
            nodes_in_level = min(2**level, 4)  # Cap width for visibility
            
            for i in range(nodes_in_level):
                x_pos = (i - (nodes_in_level - 1) / 2) * node_width
                y_pos = -level * level_height
                
                # Create node with glow effect (3b1b style)
                node = Circle(
                    radius=node_radius, 
                    fill_color=GREEN_E, 
                    fill_opacity=0.7, 
                    stroke_color=GREEN_A,
                    stroke_width=2
                )
                node.move_to([x_pos, y_pos, 0])
                
                # Add subtle glow (3b1b style)
                glow = node.copy().set_fill(opacity=0).set_stroke(GREEN_A, width=5, opacity=0.3)
                glow.scale(1.2)
                
                node_group = VGroup(glow, node)
                level_nodes.append(node_group)
                level_group.add(node_group)
                
                # Connect to parent if not root
                if level > 0:
                    parent_idx = min(i // 2, len(nodes[level-1]) - 1)
                    parent = nodes[level-1][parent_idx]
                    
                    edge = Line(
                        parent[1].get_center(),  # Use the actual node, not the glow
                        node.get_center(),
                        stroke_width=2,
                        stroke_opacity=0.7,
                        color=GRAY_C
                    )
                    edges.append(edge)
            
            nodes.append(level_nodes)
            level_groups.append(level_group)
        
        # Add edges first (for proper z-ordering)
        for edge in edges:
            diagram.add(edge)
        
        # Add nodes
        for level_nodes in nodes:
            for node in level_nodes:
                diagram.add(node)
        
        # Highlight BFS path - level by level highlighting
        # First connect root to all level 1 nodes
        bfs_path = VGroup()
        if nodes[0] and len(nodes) > 1 and nodes[1]:
            root = nodes[0][0][1]
            for node in nodes[1]:
                actual_node = node[1]  # Get the actual node, not the glow
                path_edge = Line(
                    root.get_center(),
                    actual_node.get_center(),
                    stroke_width=3,
                    color=GREEN_A
                )
                bfs_path.add(path_edge)
        
        diagram.add(bfs_path)
        
        # Add label
        label = Text("BFS: Breadth-First Search", font_size=26, color=GREEN_C)  # Increased from 22
        label.next_to(diagram, UP, buff=0.3)
        diagram.add(label)
        
        # Add small explanation text
        explanation = Text("Explores all neighbors before moving to next level", 
                           font_size=18, color=LIGHT_GRAY)  # Increased from 16
        explanation.next_to(label, UP, buff=0.2)
        diagram.add(explanation)
        
        # Add level indicators (0, 1, 2) on the left side
        for i, level_group in enumerate(level_groups):
            level_text = Text(f"Level {i}", font_size=20, color=GREEN_C)  # Increased from 16
            # Position to the left of the first node in each level
            if level_group:
                level_text.next_to(level_group, LEFT, buff=0.3)
                diagram.add(level_text)
        
        # Center the diagram
        diagram.move_to(ORIGIN)
        
        return diagram

    def create_scaling_diagram(self):
        """Create a capacity scaling visualization in enhanced 3b1b style."""
        diagram = VGroup()
        
        # Create a small network to illustrate capacity scaling
        node_radius = 0.25  # Increased from 0.2
        node_positions = {
            "s": LEFT * 1.5,
            "a": UP * 0.7,
            "b": DOWN * 0.7,
            "t": RIGHT * 1.5
        }
        
        # Define edge capacities for the network
        edge_capacities = {
            ("s", "a"): "16",
            ("s", "b"): "4", 
            ("a", "t"): "12",
            ("b", "t"): "8",
            ("a", "b"): "10"
        }
        
        # Calculate the maximum capacity for delta
        max_capacity = max([int(cap) for cap in edge_capacities.values()])
        # Find the largest power of 2 that is < max_capacity (not <=)
        delta_value = 1
        while delta_value * 2 < max_capacity:
            delta_value *= 2
        
        nodes = {}
        for label, pos in node_positions.items():
            # Create node with glow effect (3b1b style)
            circle = Circle(
                radius=node_radius, 
                fill_color=BLUE_E, 
                fill_opacity=0.7, 
                stroke_color=BLUE_A,
                stroke_width=2
            )
            
            # Add subtle glow (3b1b style)
            glow = circle.copy().set_fill(opacity=0).set_stroke(BLUE_A, width=5, opacity=0.3)
            glow.scale(1.2)
            
            text = Text(label, font_size=20, color=WHITE)  # Increased from 16
            node = VGroup(glow, circle, text)
            node.move_to(pos)
            nodes[label] = node
            diagram.add(node)
        
        # Create edges with capacities
        edges = [(u, v, cap) for (u, v), cap in edge_capacities.items()]
        
        edge_objects = {}
        capacity_labels = {}
        
        for u, v, cap in edges:
            start = nodes[u][1].get_center()  # Use the circle, not the glow
            end = nodes[v][1].get_center()
            
            # Create arrow with improved styling
            arrow = Arrow(
                start=start, 
                end=end,
                buff=node_radius,
                stroke_width=2,
                stroke_opacity=0.7,
                color=GRAY,
                tip_length=0.15
            )
            
            # Add capacity label with improved styling
            direction = normalize(end - start)
            offset = rotate_vector_2d(direction, PI/2) * 0.15
            cap_text = Text(cap, font_size=22, color=WHITE)  # Increased from 18
            cap_text.move_to((start + end) / 2 + offset)
            
            # Add background bubble for capacity text (3b1b style)
            cap_bubble = Circle(
                radius=0.2,  # Increased from 0.17
                fill_color=DARK_GRAY,
                fill_opacity=0.7,
                stroke_color=GRAY_C,
                stroke_width=1
            ).move_to(cap_text.get_center())
            
            capacity_group = VGroup(cap_bubble, cap_text)
            
            diagram.add(arrow, capacity_group)
            edge_objects[(u, v)] = arrow
            capacity_labels[(u, v)] = capacity_group
        
        # Highlight highest capacity path
        high_cap_path = VGroup()
        high_cap_edges = [("s", "a"), ("a", "t")]
        
        for u, v in high_cap_edges:
            if (u, v) in edge_objects:
                highlight = edge_objects[(u, v)].copy()
                highlight.set_color(BLUE_A).set_stroke(width=4)
                high_cap_path.add(highlight)
        
        diagram.add(high_cap_path)
        
        # Add delta indicator - moved to bottom of the diagram
        delta_box = RoundedRectangle(
            width=1.3,  # Increased from 1.2
            height=0.6,  # Increased from 0.5
            corner_radius=0.1,
            fill_color=BLUE_E,
            fill_opacity=0.7,
            stroke_color=BLUE_A,
            stroke_width=2
        )
        delta_text = Text(f"Δ = {delta_value}", font_size=24, color=WHITE)  # Increased from 20
        delta_text.move_to(delta_box)
        delta_group = VGroup(delta_box, delta_text)
        
        # Position delta box below the network (centered)
        delta_group.next_to(diagram, DOWN, buff=0.3)
        
        diagram.add(delta_group)
        
        # Add label
        label = Text("Capacity Scaling", font_size=26, color=BLUE_C)  # Increased from 22
        label.next_to(diagram, UP, buff=0.3)
        diagram.add(label)
        
        # Add small explanation text
        explanation = Text("Prioritizes high-capacity paths first", 
                        font_size=18, color=LIGHT_GRAY)  # Increased from 16
        explanation.next_to(label, UP, buff=0.2)
        diagram.add(explanation)
        
        # Center the diagram
        diagram.move_to(ORIGIN)
        
        return diagram

    def create_performance_chart(self):
        """Create a performance comparison chart in 3b1b style."""
        chart = VGroup()
        
        # Create chart title
        title = Text("Performance Comparison", font_size=28, color=YELLOW_C)
        title.to_edge(UP, buff=0.5)
        chart.add(title)
        
        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_tip": False, "include_numbers": False},
            x_length=8,
            y_length=5
        )
        
        # Add axes labels
        x_label = Text("Network Size", font_size=20, color=LIGHT_GRAY)
        x_label.next_to(axes.x_axis, DOWN, buff=0.3)
        
        y_label = Text("Runtime", font_size=20, color=LIGHT_GRAY)
        y_label.next_to(axes.y_axis, LEFT, buff=0.3)
        
        chart.add(axes, x_label, y_label)
        
        # Create performance curves
        dfs_points = [(0, 0), (2, 1), (4, 3), (6, 5.5), (8, 8.5)]
        bfs_points = [(0, 0), (2, 0.8), (4, 2), (6, 3.5), (8, 5.5)]
        scaling_points = [(0, 0), (2, 1.2), (4, 2.2), (6, 3.2), (8, 4.2)]
        
        # Convert to axes coordinates
        dfs_coords = [axes.coords_to_point(x, y) for x, y in dfs_points]
        bfs_coords = [axes.coords_to_point(x, y) for x, y in bfs_points]
        scaling_coords = [axes.coords_to_point(x, y) for x, y in scaling_points]
        
        # Create curves
        dfs_curve = VMobject(color=RED_C, stroke_width=3)
        dfs_curve.set_points_smoothly(dfs_coords)
        
        bfs_curve = VMobject(color=GREEN_C, stroke_width=3)
        bfs_curve.set_points_smoothly(bfs_coords)
        
        scaling_curve = VMobject(color=BLUE_C, stroke_width=3)
        scaling_curve.set_points_smoothly(scaling_coords)
        
        chart.add(dfs_curve, bfs_curve, scaling_curve)
        
        # Add curve labels
        dfs_label = Text("DFS", font_size=18, color=RED_C)
        dfs_label.next_to(dfs_curve.points[-1], RIGHT, buff=0.2)
        
        bfs_label = Text("BFS", font_size=18, color=GREEN_C)
        bfs_label.next_to(bfs_curve.points[-1], RIGHT, buff=0.2)
        
        scaling_label = Text("Scaling", font_size=18, color=BLUE_C)
        scaling_label.next_to(scaling_curve.points[-1], RIGHT, buff=0.2)
        
        chart.add(dfs_label, bfs_label, scaling_label)
        
        # Position the chart
        chart.scale(0.85).move_to(ORIGIN)
        
        return chart

    def demonstrate_dfs_algorithm(self):
        """Create a detailed demonstration of the DFS algorithm for Ford-Fulkerson."""
        # Title for this section
        title = Text("Basic Ford-Fulkerson with DFS", font_size=32, color=RED_C)
        title.to_edge(UP, buff=0.7)
        
        self.play(FadeIn(title), run_time=1.0)
        
        # Description text positioned below the title with appropriate spacing
        description = Text(
            "DFS explores as far as possible along each branch before backtracking",
            font_size=24, color=LIGHT_GRAY
        )
        description.next_to(title, DOWN, buff=0.6)  # Increased buffer
        
        self.play(FadeIn(description), run_time=1.0)
        self.wait(0.5)
        
        # Create a small network example specifically for DFS
        dfs_network, nodes = self.create_network_example(
            title_text="", # Remove title text to avoid overlapping
            scale_factor=1.1,
            custom_position=ORIGIN + DOWN * 0.5  # Position slightly lower to avoid overlapping
        )
        
        # Animate network after description
        self.play(FadeIn(dfs_network, scale=1.1), run_time=1.2)
        self.wait(0.8)
        
        # Demonstrate DFS traversal with valid paths from s to t
        # Each sublist represents one complete path from s to t
        valid_paths = [
            [("s", "a"), ("a", "b"), ("b", "t")],         # First path: s->a->b->t
            [("s", "a"), ("a", "d"), ("d", "t")],         # Second path: s->a->d->t
            [("s", "c"), ("c", "d"), ("d", "t")]          # Third path: s->c->d->t
        ]
        
        # Show DFS path finding step by step
        path_visualizations = []
        
        for path_idx, path in enumerate(valid_paths):
            # Create arrows for this path
            path_arrows = VGroup()
            for u, v in path:
                if u in nodes and v in nodes:
                    start = nodes[u].get_center()
                    end = nodes[v].get_center()
                    
                    arrow = Arrow(
                        start=start, 
                        end=end,
                        buff=0.25,  # node radius
                        stroke_width=4,
                        color=RED_B,
                        tip_length=0.15
                    )
                    path_arrows.add(arrow)
            
            path_visualizations.append(path_arrows)
            
            # Animate path highlighting
            self.play(
                LaggedStart(*[GrowArrow(arrow) for arrow in path_arrows], lag_ratio=0.3),
                run_time=1.5
            )
            
            # Add path index
            path_index = Text(f"Path {path_idx+1}", font_size=20, color=RED_C)
            path_index.to_corner(DR, buff=0.5)
            self.play(FadeIn(path_index), run_time=0.5)
            
            # Animate flow if this is a complete path
            flow_pulses = []
            for arrow in path_arrows:
                pulse = arrow.copy().set_color(RED_A).set_stroke(width=6)
                flow_pulses.append(ShowPassingFlash(pulse, time_width=0.5, run_time=1.2))
            
            self.play(LaggedStart(*flow_pulses, lag_ratio=0.2), run_time=1.8)
            self.wait(0.7)
            
            # Clean up after each path demonstration
            self.play(
                FadeOut(path_index),
                FadeOut(path_arrows),
                run_time=0.8
            )
        
        # Add key characteristics
        characteristics = VGroup()
        char_items = [
            "• Simple implementation",
            "• Time complexity: O(|E|·f)",
            "• May not find shortest paths",
            "• Can be slow on large networks"
        ]
        
        for item in char_items:
            text = Text(item, font_size=22, color=LIGHT_GRAY)
            characteristics.add(text)
        
        characteristics.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        characteristics.to_edge(LEFT, buff=1.0).shift(DOWN * 2.5)  # Shifted down more
        
        self.play(
            FadeIn(characteristics, shift=RIGHT*0.3),
            run_time=1.2
        )
        
        self.wait(2.0)
        
        # Ensure complete cleanup - explicitly check and remove any remaining path arrows
        remaining_objects = VGroup()
        
        for arrows in path_visualizations:
            # Check if this object is still in the scene
            if arrows in self.mobjects:
                remaining_objects.add(arrows)
        
        # Add main elements to cleanup group
        all_elements = VGroup(dfs_network, characteristics, description, title)
        
        # Fade out everything
        self.play(
            FadeOut(all_elements),
            FadeOut(remaining_objects),
            run_time=1.0
        )
        
        self.wait(0.5)

    def demonstrate_bfs_algorithm(self):
        """Create a detailed demonstration of the BFS algorithm for Ford-Fulkerson (Edmonds-Karp)."""
        # Title for this section
        title = Text("Edmonds-Karp Algorithm (BFS)", font_size=32, color=GREEN_C)
        title.to_edge(UP, buff=0.7)
        
        self.play(FadeIn(title), run_time=1.0)
        
        # Description text positioned below the title with appropriate spacing
        description = Text(
            "BFS finds shortest augmenting paths (in terms of number of edges)",
            font_size=24, color=LIGHT_GRAY
        )
        description.next_to(title, DOWN, buff=0.6)  # Increased buffer
        
        self.play(FadeIn(description), run_time=1.0)
        self.wait(0.5)
        
        # Create a small network example specifically for BFS
        bfs_network, nodes = self.create_network_example(
            title_text="", # Remove title text to avoid overlapping
            scale_factor=1.1,
            custom_position=ORIGIN + DOWN * 0.5  # Position slightly lower to avoid overlapping
        )
        
        # Animate network after description
        self.play(FadeIn(bfs_network, scale=1.1), run_time=1.2)
        self.wait(0.8)
        
        # Simulate BFS exploration level by level
        levels = [
            ["s"],                 # Level 0 (source)
            ["a", "c"],            # Level 1
            ["b", "d"],            # Level 2
            ["t"]                  # Level 3 (sink)
        ]
        
        level_texts = []
        level_highlights = []
        
        for i, level in enumerate(levels):
            # Highlight nodes at this level
            nodes_highlight = VGroup()
            for node_id in level:
                if node_id in nodes:
                    node_circle = Circle(
                        radius=0.3, 
                        color=GREEN_B, 
                        stroke_width=3,
                        fill_opacity=0
                    ).move_to(nodes[node_id].get_center())
                    nodes_highlight.add(node_circle)
            
            level_highlights.append(nodes_highlight)
            
            # Add level indicator
            level_text = Text(f"Level {i}", font_size=22, color=GREEN_B)
            level_text.to_corner(UL, buff=0.8).shift(DOWN * (0.6 + i * 0.5))  # Adjusted positioning
            level_texts.append(level_text)
            
            self.play(
                FadeIn(nodes_highlight, scale=1.2),
                FadeIn(level_text),
                run_time=0.8
            )
            self.wait(0.5)
        
        self.wait(1.0)
        
        # Fade out level indicators
        self.play(
            *[FadeOut(text) for text in level_texts],
            *[FadeOut(highlight) for highlight in level_highlights],
            run_time=0.8
        )
        
        # Demonstrate BFS path finding
        path_sequence = [
            ["s", "a"], ["a", "b"], ["b", "t"],  # First path s->a->b->t (shortest path)
            ["s", "c"], ["c", "d"], ["d", "t"],  # Second path s->c->d->t (also shortest)
            ["s", "a"], ["a", "d"], ["d", "b"], ["b", "t"]  # Third path s->a->d->b->t (longer)
        ]
        
        # Show BFS paths in order of increasing length
        path_visualizations = []
        
        # First two paths are 3 edges long (shortest)
        for i in range(0, 6, 3):
            path_group = path_sequence[i:i+3]
            
            # Create arrows for this path
            path_arrows = VGroup()
            for u, v in path_group:
                if u in nodes and v in nodes:
                    start = nodes[u].get_center()
                    end = nodes[v].get_center()
                    
                    arrow = Arrow(
                        start=start, 
                        end=end,
                        buff=0.25,
                        stroke_width=4,
                        color=GREEN_B,
                        tip_length=0.15
                    )
                    path_arrows.add(arrow)
            
            path_visualizations.append(path_arrows)
            
            # Animate path highlighting
            self.play(
                LaggedStart(*[GrowArrow(arrow) for arrow in path_arrows], lag_ratio=0.3),
                run_time=1.5
            )
            
            # Show path length
            path_length = Text(f"Path length: {len(path_group)} edges", font_size=20, color=GREEN_C)
            path_length.to_corner(DR, buff=0.5)
            self.play(FadeIn(path_length), run_time=0.5)
            
            # Animate flow
            flow_pulses = []
            for arrow in path_arrows:
                pulse = arrow.copy().set_color(GREEN_A).set_stroke(width=6)
                flow_pulses.append(ShowPassingFlash(pulse, time_width=0.5, run_time=1.2))
            
            self.play(LaggedStart(*flow_pulses, lag_ratio=0.2), run_time=1.8)
            self.wait(0.5)
            
            # Fade out current path elements before showing next
            self.play(
                FadeOut(path_arrows),
                FadeOut(path_length),
                run_time=0.8
            )
        
        # The final path is 4 edges long
        path_group = path_sequence[6:10]
        path_arrows = VGroup()
        for u, v in path_group:
            if u in nodes and v in nodes:
                start = nodes[u].get_center()
                end = nodes[v].get_center()
                
                arrow = Arrow(
                    start=start, 
                    end=end,
                    buff=0.25,
                    stroke_width=4,
                    color=GREEN_B,
                    tip_length=0.15
                )
                path_arrows.add(arrow)
        
        path_visualizations.append(path_arrows)
        
        # Animate longer path highlighting
        self.play(
            LaggedStart(*[GrowArrow(arrow) for arrow in path_arrows], lag_ratio=0.3),
            run_time=1.5
        )
        
        # Show longer path length
        path_length = Text(f"Path length: {len(path_group)} edges (longer path)", font_size=20, color=GREEN_C)
        path_length.to_corner(DR, buff=0.5)
        self.play(FadeIn(path_length), run_time=0.5)
        
        # Animate flow for longer path
        flow_pulses = []
        for arrow in path_arrows:
            pulse = arrow.copy().set_color(GREEN_A).set_stroke(width=6)
            flow_pulses.append(ShowPassingFlash(pulse, time_width=0.5, run_time=1.2))
        
        self.play(LaggedStart(*flow_pulses, lag_ratio=0.2), run_time=1.8)
        self.wait(1.0)
        
        # Fade out path elements
        self.play(
            FadeOut(path_arrows),
            FadeOut(path_length),
            run_time=0.8
        )
        
        # Add key characteristics
        characteristics = VGroup()
        char_items = [
            "• Finds shortest augmenting paths first",
            "• Time complexity: O(|V|·|E|²)",
            "• More efficient on typical graphs",
            "• Guarantees polynomial time"
        ]
        
        for item in char_items:
            text = Text(item, font_size=22, color=LIGHT_GRAY)
            characteristics.add(text)
        
        characteristics.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        characteristics.to_edge(LEFT, buff=1.0).shift(DOWN * 2.5)  # Shifted down more
        
        self.play(
            FadeIn(characteristics, shift=RIGHT*0.3),
            run_time=1.2
        )
        
        self.wait(2.0)
        
        # Ensure complete cleanup - explicitly check and remove any remaining path arrows
        remaining_objects = VGroup()
        
        for arrows in path_visualizations:
            # Check if this object is still in the scene
            if arrows in self.mobjects:
                remaining_objects.add(arrows)
        
        # Add main elements to cleanup group
        all_elements = VGroup(bfs_network, characteristics, description, title)
        
        # Fade out everything
        self.play(
            FadeOut(all_elements),
            FadeOut(remaining_objects),
            run_time=1.0
        )
        
        self.wait(0.5)

    def demonstrate_capacity_scaling(self):
        """Create a detailed demonstration of the Capacity Scaling algorithm for Ford-Fulkerson."""
        # Title for this section
        title = Text("Capacity Scaling Approach", font_size=32, color=BLUE_C)
        title.to_edge(UP, buff=0.7)
        
        self.play(FadeIn(title), run_time=1.0)
        
        # Description text positioned below the title with appropriate spacing
        description = Text(
            "Prioritizes paths with large residual capacities",
            font_size=24, color=LIGHT_GRAY
        )
        description.next_to(title, DOWN, buff=0.6)  # Increased buffer
        
        self.play(FadeIn(description), run_time=1.0)
        self.wait(0.5)
        
        # Create a small network example specifically for capacity scaling
        scaling_network, nodes = self.create_network_example(
            title_text="", # Remove title text to avoid overlapping
            scale_factor=1.1,
            custom_position=ORIGIN + DOWN * 0.5  # Position slightly lower to avoid overlapping
        )
        
        # Animate network after description
        self.play(FadeIn(scaling_network, scale=1.1), run_time=1.2)
        self.wait(0.8)
        
        # Show capacity scaling phases with different delta values
        delta_values = [8, 4, 2, 1]  # Powers of 2, decreasing
        
        # Define valid paths for each delta value (all from s to t)
        delta_paths = {
            8: [("s", "a"), ("a", "b"), ("b", "t")],  # Path with highest capacity edges
            4: [("s", "a"), ("a", "d"), ("d", "t")],  # Another valid path
            2: [("s", "c"), ("c", "d"), ("d", "t")],  # Path with medium capacity
            1: [("s", "c"), ("c", "d"), ("d", "t")]   # Smallest capacity path that's still valid
        }
        
        # Store all highlighted edges for proper cleanup
        all_highlighted_edges = []
        
        for delta in delta_values:
            # Show delta value
            delta_text = Text(f"Delta = {delta}", font_size=26, color=BLUE_B)
            delta_text.to_corner(UL, buff=0.8)  # Increased buffer
            self.play(FadeIn(delta_text), run_time=0.8)
            
            # Get valid path for this delta value
            edge_pairs = delta_paths[delta]
            
            high_capacity_edges = VGroup()
            for u, v in edge_pairs:
                if u in nodes and v in nodes:
                    start = nodes[u].get_center()
                    end = nodes[v].get_center()
                    
                    edge = Arrow(
                        start=start, 
                        end=end,
                        buff=0.25,
                        stroke_width=4,
                        color=BLUE_B,
                        tip_length=0.15
                    )
                    high_capacity_edges.add(edge)
            
            all_highlighted_edges.append(high_capacity_edges)
            
            # Animate highlighting of high-capacity edges
            self.play(
                LaggedStart(*[GrowArrow(edge) for edge in high_capacity_edges], lag_ratio=0.2),
                run_time=1.2
            )
            
            # Add explanation for this phase
            phase_explanation = Text(
                f"Consider only edges with capacity ≥ {delta}",
                font_size=20, color=LIGHT_GRAY
            )
            phase_explanation.to_corner(DR, buff=0.5)
            self.play(FadeIn(phase_explanation), run_time=0.5)
            
            # Pulse effect for augmenting flow
            flow_pulses = []
            for edge in high_capacity_edges:
                pulse = edge.copy().set_color(BLUE_A).set_stroke(width=6)
                flow_pulses.append(ShowPassingFlash(pulse, time_width=0.5, run_time=1.2))
            
            self.play(LaggedStart(*flow_pulses, lag_ratio=0.2), run_time=1.8)
            
            self.wait(1.0)
            
            # Clean up before next delta - important to explicitly fade out edges
            self.play(
                FadeOut(delta_text),
                FadeOut(phase_explanation),
                FadeOut(high_capacity_edges),
                run_time=0.8
            )
        
        # Add key characteristics
        characteristics = VGroup()
        char_items = [
            "• Considers high-capacity edges first",
            "• Time complexity: O(|E|²·log(U))",
            "• U is the maximum capacity in the network",
            "• Efficient on networks with large capacities"
        ]
        
        for item in char_items:
            text = Text(item, font_size=22, color=LIGHT_GRAY)
            characteristics.add(text)
        
        characteristics.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        characteristics.to_edge(LEFT, buff=1.0).shift(DOWN * 2.5)  # Shifted down more
        
        self.play(
            FadeIn(characteristics, shift=RIGHT*0.3),
            run_time=1.2
        )
        
        self.wait(2.0)
        
        # Ensure complete cleanup - explicitly check and remove any remaining highlighted edges
        remaining_objects = VGroup()
        
        for edges in all_highlighted_edges:
            # Check if this object is still in the scene
            if edges in self.mobjects:
                remaining_objects.add(edges)
        
        # Add main elements to cleanup group
        all_elements = VGroup(scaling_network, characteristics, description, title)
        
        # Fade out everything
        self.play(
            FadeOut(all_elements),
            FadeOut(remaining_objects),
            run_time=1.0
        )
        
        self.wait(0.5) 