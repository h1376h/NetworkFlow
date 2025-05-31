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
        network_example = self.create_network_example()
        network_example.scale(0.8).to_edge(LEFT, buff=1.0)
        
        # Fade out explanation text completely (fixed overlap issue)
        self.play(
            FadeOut(explanation_group),
            FadeIn(network_example),
            run_time=1.2
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
            network_example.animate.to_edge(LEFT, buff=1.0),
            run_time=1.2
        )
        self.wait(0.5)
        
        # Augmenting path animation
        self.animate_augmenting_path(network_example)
        
        # Create three algorithm boxes with arrows from core concept
        algorithms = [
            {
                "name": "Basic Ford-Fulkerson (DFS)",
                "description": "Uses depth-first search\nto find augmenting paths",
                "key_points": ["Simple implementation", "O(|E|·f) time complexity", "May be slow on large networks"],
                "color": RED_D,
                "diagram": self.create_dfs_diagram()
            },
            {
                "name": "Edmonds-Karp (BFS)",
                "description": "Uses breadth-first search\nfor shortest augmenting paths",
                "key_points": ["Finds shortest paths first", "O(|V|·|E|²) time complexity", "More efficient on typical graphs"],
                "color": GREEN_D,
                "diagram": self.create_bfs_diagram()
            },
            {
                "name": "Capacity Scaling",
                "description": "Prioritizes paths with\nlarge residual capacities",
                "key_points": ["Considers high-capacity edges first", "O(|E|²·log(U)) time complexity", "Efficient on networks with large capacities"],
                "color": BLUE_D,
                "diagram": self.create_scaling_diagram()
            }
        ]
        
        algo_boxes = VGroup()
        algo_descriptions = VGroup()
        algo_key_points = VGroup()
        algo_diagrams = VGroup()
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
            
            # Key points below description
            key_points_group = VGroup()
            for j, point in enumerate(algo["key_points"]):
                bullet = Text("•", font_size=16, color=lighten_color(algo["color"], 0.3))
                point_text = Text(point, font_size=16, color=LIGHT_GRAY)
                point_group = VGroup(bullet, point_text).arrange(RIGHT, buff=0.1, aligned_edge=UP)
                key_points_group.add(point_group)
            
            key_points_group.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            key_points_group.next_to(description, DOWN, buff=0.3)
            
            # Add algorithm visualization diagram
            diagram = algo["diagram"]
            diagram.scale(0.45)
            diagram.next_to(key_points_group, DOWN, buff=0.3)
            
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
            algo_key_points.add(key_points_group)
            algo_diagrams.add(diagram)
            arrows.add(arrow)
        
        # Animate the arrows from core concept to algorithms
        self.play(
            *[Create(arrow) for arrow in arrows],
            FadeOut(network_example),
            run_time=1.5
        )
        
        # Animate the algorithm boxes
        self.play(
            *[FadeIn(box, scale=1.1) for box in algo_boxes],
            run_time=1
        )
        
        # Animate descriptions
        self.play(
            *[FadeIn(desc, shift=UP*0.2) for desc in algo_descriptions],
            run_time=0.8
        )
        
        # Animate key points for each algorithm
        for points in algo_key_points:
            self.play(
                LaggedStart(*[FadeIn(point, shift=RIGHT*0.3) for point in points], lag_ratio=0.2),
                run_time=1.2
            )
        
        # Animate algorithm diagrams
        self.play(
            *[FadeIn(diagram, scale=1.1) for diagram in algo_diagrams],
            run_time=1.2
        )
        
        self.wait(1)
        
        # Performance comparison chart (3b1b style)
        perf_chart = self.create_performance_chart()
        
        self.play(
            *[FadeOut(diagram) for diagram in algo_diagrams],
            *[FadeOut(points) for points in algo_key_points],
            *[FadeOut(desc) for desc in algo_descriptions],
            FadeIn(perf_chart),
            run_time=1.5
        )
        
        self.wait(1.5)
        
        # Fade out performance chart
        self.play(
            FadeOut(perf_chart),
            run_time=1
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
        
        self.wait(1)
        
        # Final fade out
        self.play(
            FadeOut(conclusion_banner),
            FadeOut(conclusion_text),
            FadeOut(algo_boxes),
            FadeOut(arrows),
            FadeOut(ff_core_concept),
            FadeOut(title),
            FadeOut(underline),
            run_time=1.5
        )
        
        self.wait(1)

    def create_network_example(self):
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
            
            # Add capacity label
            # Use rotate_vector_2d instead of .rotate()
            direction = normalize(end - start)
            offset = rotate_vector_2d(direction, PI/2) * 0.15
            cap_text = Text(cap, font_size=16, color=LIGHT_GRAY)
            cap_text.move_to((start + end) / 2 + offset)
            
            network.add(arrow, cap_text)
        
        # Add "Network Example" label
        label = Text("Network Example", font_size=24, color=YELLOW_C)
        label.next_to(network, UP, buff=0.3)
        network.add(label)
        
        return network
    
    def animate_augmenting_path(self, network):
        """Animate an augmenting path in the network example."""
        # Create a simple path highlight animation
        path_edges = [("s", "a"), ("a", "b"), ("b", "t")]
        
        # Extract node positions from the network
        nodes = {}
        for i in range(len(network) - 1):  # Skip the last element which is the label
            if isinstance(network[i][0], Circle):
                node_label = network[i][1].text
                nodes[node_label] = network[i].get_center()
        
        # Create path highlight
        path_arrows = VGroup()
        for u, v in path_edges:
            if u in nodes and v in nodes:
                start = nodes[u]
                end = nodes[v]
                
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
        """Create a DFS visualization."""
        diagram = VGroup()
        
        # Create a small tree to illustrate DFS
        tree_levels = 3
        node_radius = 0.2
        level_height = 0.7
        node_width = 0.6
        
        nodes = []
        edges = []
        
        # Create nodes in a tree structure
        for level in range(tree_levels):
            level_nodes = []
            nodes_in_level = min(2**level, 4)  # Cap width for visibility
            
            for i in range(nodes_in_level):
                x_pos = (i - (nodes_in_level - 1) / 2) * node_width
                y_pos = -level * level_height
                
                node = Circle(radius=node_radius, fill_color=RED_E, fill_opacity=0.7, stroke_color=RED_A)
                node.move_to([x_pos, y_pos, 0])
                level_nodes.append(node)
                
                # Connect to parent if not root
                if level > 0:
                    parent_idx = min(i // 2, len(nodes[level-1]) - 1)
                    parent = nodes[level-1][parent_idx]
                    
                    edge = Line(
                        parent.get_center(),
                        node.get_center(),
                        stroke_width=2,
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
        
        # Highlight DFS path
        dfs_path = VGroup()
        for i in range(tree_levels-1):
            if i < len(nodes) - 1 and nodes[i] and nodes[i+1]:
                start_node = nodes[i][0]
                end_node = nodes[i+1][0]
                
                path_edge = Line(
                    start_node.get_center(),
                    end_node.get_center(),
                    stroke_width=4,
                    color=RED_A
                )
                dfs_path.add(path_edge)
        
        diagram.add(dfs_path)
        
        # Add label
        label = Text("DFS: Deep First", font_size=20, color=RED_C)
        label.next_to(diagram, UP, buff=0.3)
        diagram.add(label)
        
        return diagram

    def create_bfs_diagram(self):
        """Create a BFS visualization."""
        diagram = VGroup()
        
        # Create a small tree to illustrate BFS
        tree_levels = 3
        node_radius = 0.2
        level_height = 0.7
        node_width = 0.6
        
        nodes = []
        edges = []
        
        # Create nodes in a tree structure
        for level in range(tree_levels):
            level_nodes = []
            nodes_in_level = min(2**level, 4)  # Cap width for visibility
            
            for i in range(nodes_in_level):
                x_pos = (i - (nodes_in_level - 1) / 2) * node_width
                y_pos = -level * level_height
                
                node = Circle(radius=node_radius, fill_color=GREEN_E, fill_opacity=0.7, stroke_color=GREEN_A)
                node.move_to([x_pos, y_pos, 0])
                level_nodes.append(node)
                
                # Connect to parent if not root
                if level > 0:
                    parent_idx = min(i // 2, len(nodes[level-1]) - 1)
                    parent = nodes[level-1][parent_idx]
                    
                    edge = Line(
                        parent.get_center(),
                        node.get_center(),
                        stroke_width=2,
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
        
        # Highlight BFS path - breadth first traversal
        bfs_path = VGroup()
        
        # Level 0 to 1
        if nodes[0] and nodes[1] and len(nodes[1]) >= 2:
            for i in range(min(2, len(nodes[1]))):
                path_edge = Line(
                    nodes[0][0].get_center(),
                    nodes[1][i].get_center(),
                    stroke_width=4,
                    color=GREEN_A
                )
                bfs_path.add(path_edge)
        
        diagram.add(bfs_path)
        
        # Add label
        label = Text("BFS: Breadth First", font_size=20, color=GREEN_C)
        label.next_to(diagram, UP, buff=0.3)
        diagram.add(label)
        
        return diagram

    def create_scaling_diagram(self):
        """Create a capacity scaling visualization."""
        diagram = VGroup()
        
        # Create a small network to illustrate capacity scaling
        node_radius = 0.2
        node_positions = {
            "s": LEFT * 1.5,
            "a": UP * 0.7,
            "b": DOWN * 0.7,
            "t": RIGHT * 1.5
        }
        
        nodes = {}
        for label, pos in node_positions.items():
            circle = Circle(radius=node_radius, fill_color=BLUE_E, fill_opacity=0.7, stroke_color=BLUE_A)
            text = Text(label, font_size=16, color=WHITE)
            node = VGroup(circle, text)
            node.move_to(pos)
            nodes[label] = node
            diagram.add(node)
        
        # Create edges with capacities
        edges = [
            ("s", "a", "16"),
            ("s", "b", "4"),
            ("a", "t", "12"),
            ("b", "t", "8"),
            ("a", "b", "10")
        ]
        
        edge_objects = {}
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
            
            # Add capacity label
            # Use rotate_vector_2d instead of .rotate()
            direction = normalize(end - start)
            offset = rotate_vector_2d(direction, PI/2) * 0.15
            cap_text = Text(cap, font_size=14, color=LIGHT_GRAY)
            cap_text.move_to((start + end) / 2 + offset)
            
            diagram.add(arrow, cap_text)
            edge_objects[(u, v)] = arrow
        
        # Highlight highest capacity path
        high_cap_path = VGroup()
        high_cap_edges = [("s", "a"), ("a", "t")]
        
        for u, v in high_cap_edges:
            if (u, v) in edge_objects:
                highlight = edge_objects[(u, v)].copy()
                highlight.set_color(BLUE_A).set_stroke(width=4)
                high_cap_path.add(highlight)
        
        diagram.add(high_cap_path)
        
        # Add label
        label = Text("Scaling: Highest Capacity First", font_size=20, color=BLUE_C)
        label.next_to(diagram, UP, buff=0.3)
        diagram.add(label)
        
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