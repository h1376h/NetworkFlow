from manim import *
import math
from collections import deque

# Define phi (golden ratio conjugate)
PHI = (math.sqrt(5) - 1) / 2 # ~0.618034

# Global constants for styling
NODE_COLOR = BLUE_B
NODE_FILL_OPACITY = 0.6
NODE_RADIUS = 0.25
EDGE_COLOR = GREY_B
EDGE_STROKE_WIDTH = 2
HIGHLIGHT_COLOR = RED_C # Stronger red for path
HIGHLIGHT_STROKE_WIDTH = 5
LABEL_SCALE = 0.45 # Smaller text for edge labels
LABEL_COLOR = WHITE
TITLE_COLOR = WHITE
TOTAL_FLOW_COLOR = YELLOW_B
DEFAULT_REVERSE_COLOR = GREY_A # Even lighter for reverse paths
FLOW_ANIMATION_COLOR = YELLOW_D # Color for the "packet"
FLOAT_PRECISION = 5 # Decimal places for display
EPSILON = 1e-9 # For floating point comparisons to zero

class FordFulkersonIrrationalFlow(Scene):
    # Class attributes for constants
    NODE_COLOR = BLUE_B
    NODE_FILL_OPACITY = 0.6
    NODE_RADIUS = 0.25
    EDGE_COLOR = GREY_B
    EDGE_STROKE_WIDTH = 2
    HIGHLIGHT_COLOR = RED_C
    HIGHLIGHT_STROKE_WIDTH = 5
    LABEL_SCALE = 0.45
    LABEL_COLOR = WHITE
    TITLE_COLOR = WHITE
    TOTAL_FLOW_COLOR = YELLOW_B
    DEFAULT_REVERSE_COLOR = GREY_A
    FLOW_ANIMATION_COLOR = YELLOW_D
    FLOAT_PRECISION = 5
    EPSILON = 1e-9

    def construct(self):
        # --- 1. Setup Graph Elements ---
        node_coords = {
            "s": [-6, 0, 0],
            "x1": [-2, 2, 0],
            "x2": [-2, -2, 0],
            "t": [6, 0, 0],
        }

        self.node_mobs = {}
        for key, coord in node_coords.items():
            color = self.NODE_COLOR if key == 's' else RED_B if key == 't' else self.NODE_COLOR
            node_dot = Circle(radius=self.NODE_RADIUS, color=color, fill_opacity=self.NODE_FILL_OPACITY).move_to(coord)
            node_text = Text(key).scale(0.8).move_to(node_dot.get_center())
            self.node_mobs[key] = VGroup(node_dot, node_text)
            self.add(self.node_mobs[key])

        self.M_val = 100
        self.original_capacities = {
            ("s", "x1"): 1.0, ("s", "x2"): self.M_val,
            ("x1", "x2"): 1.0, ("x1", "t"): self.M_val,
            ("x2", "t"): PHI
        }
        self.original_capacities_tex = {
            ("s", "x1"): "1", ("s", "x2"): "M",
            ("x1", "x2"): "1", ("x1", "t"): "M",
            ("x2", "t"): "\\phi"
        }

        self.current_flows = {edge: 0.0 for edge in self.original_capacities}
        self.residual_capacities = self.original_capacities.copy()
        for (u, v) in self.original_capacities:
            self.residual_capacities[(v, u)] = 0.0

        self.total_flow = 0.0

        self.edge_group = VGroup()
        
        # --- Helper function for creating/updating edge Mobjects ---
        def create_arrow_and_labels(u_key, v_key, is_reverse=False):
            start_mob = self.node_mobs[u_key][0]
            end_mob = self.node_mobs[v_key][0]

            vec = end_mob.get_center() - start_mob.get_center()
            unit_vec = normalize(vec)
            arrow_start = start_mob.get_center() + unit_vec * self.NODE_RADIUS
            arrow_end = end_mob.get_center() - unit_vec * self.NODE_RADIUS

            offset_amount = 0.15
            perp_vec = np.array([-unit_vec[1], unit_vec[0], 0])
            
            if is_reverse:
                arrow_start += perp_vec * offset_amount
                arrow_end += perp_vec * offset_amount # Corrected: used perp_vec * offset_amount
                arrow = Arrow(arrow_start, arrow_end, buff=0, stroke_width=self.EDGE_STROKE_WIDTH, color=self.DEFAULT_REVERSE_COLOR, tip_length=0.2)
                arrow.set_stroke(dash_arg=[0.1, 0.1]) # Correct way to set dashing
            else:
                if (v_key, u_key) in self.original_capacities:
                    arrow_start -= perp_vec * offset_amount
                    arrow_end -= perp_vec * offset_amount
                arrow = Arrow(arrow_start, arrow_end, buff=0, stroke_width=self.EDGE_STROKE_WIDTH, color=self.EDGE_COLOR, tip_length=0.2)
            
            return arrow

        def create_label_mobject(flow_val, original_cap_tex, res_cap_val, is_reverse=False):
            if is_reverse:
                label_text = MathTex(f"({res_cap_val:.{self.FLOAT_PRECISION}f})").scale(self.LABEL_SCALE).set_color(self.LABEL_COLOR)
            else:
                label_text = MathTex(f"{flow_val:.{self.FLOAT_PRECISION}f}/{original_cap_tex} ({res_cap_val:.{self.FLOAT_PRECISION}f})").scale(self.LABEL_SCALE).set_color(self.LABEL_COLOR)
            return label_text

        def get_label_position(arrow, is_reverse=False):
            label_offset_scalar = 0.5
            arrow_direction = normalize(arrow.get_end() - arrow.get_start())
            perp_direction = np.array([-arrow_direction[1], arrow_direction[0], 0])

            if is_reverse:
                return arrow.point_from_proportion(0.5) + perp_direction * -label_offset_scalar
            else:
                return arrow.point_from_proportion(0.5) + perp_direction * label_offset_scalar

        def update_graph_mobjects(highlight_path=None):
            current_edge_group = VGroup()

            for (u, v), original_cap in self.original_capacities.items():
                current_flow_val = self.current_flows.get((u, v), 0.0)
                res_cap_val = self.residual_capacities.get((u, v), 0.0)
                original_cap_tex = self.original_capacities_tex[(u,v)]

                if current_flow_val > self.EPSILON or res_cap_val > self.EPSILON:
                    arrow = create_arrow_and_labels(u, v, is_reverse=False)
                    label_mob = create_label_mobject(current_flow_val, original_cap_tex, res_cap_val, is_reverse=False)
                    label_mob.move_to(get_label_position(arrow, is_reverse=False))
                    
                    if highlight_path and (u, v) in highlight_path:
                        arrow.set_color(self.HIGHLIGHT_COLOR).set_stroke(width=self.HIGHLIGHT_STROKE_WIDTH)
                    
                    current_edge_group.add(VGroup(arrow, label_mob))

            for (u, v) in self.original_capacities:
                res_cap_reverse_val = self.residual_capacities.get((v, u), 0.0)
                if res_cap_reverse_val > self.EPSILON:
                    arrow = create_arrow_and_labels(v, u, is_reverse=True)
                    label_mob = create_label_mobject(0, "", res_cap_reverse_val, is_reverse=True)
                    label_mob.move_to(get_label_position(arrow, is_reverse=True))

                    if highlight_path and (v, u) in highlight_path:
                        arrow.set_color(self.HIGHLIGHT_COLOR).set_stroke(width=self.HIGHLIGHT_STROKE_WIDTH)
                    
                    current_edge_group.add(VGroup(arrow, label_mob))
            
            # Animate the transition between the old and new edge_group
            # This makes updates smooth rather than instant jumps
            if self.edge_group.is_empty():
                self.play(Create(current_edge_group), run_time=1)
            else:
                self.play(Transform(self.edge_group, current_edge_group), run_time=1)
            self.edge_group = current_edge_group # Update reference

        # --- BFS for finding augmenting path (Edmonds-Karp flavor) ---
        def find_augmenting_path():
            parent = {}
            queue = deque([("s", None)]) # (node, parent_node_key)
            visited = {"s"}

            while queue:
                current_node, p_node = queue.popleft()
                # Store parent for path reconstruction. No need to store if current_node is 's'
                if p_node is not None:
                    parent[current_node] = p_node

                if current_node == "t":
                    # Path found, reconstruct it
                    path = []
                    curr = "t"
                    while parent.get(curr) is not None: # Use .get() for robustness, though should always exist if path found
                        prev = parent[curr]
                        path.insert(0, (prev, curr))
                        curr = prev
                    return path

                # Explore neighbors in residual graph
                # Check original edges (forward flow in residual graph)
                for (u, v) in self.original_capacities:
                    if u == current_node and self.residual_capacities[(u, v)] > self.EPSILON and v not in visited:
                        visited.add(v)
                        queue.append((v, u)) # Store (node_to_visit, parent_node)
                # Check reverse edges (backward flow in residual graph)
                for (u, v) in self.original_capacities:
                    if v == current_node and self.residual_capacities[(v, u)] > self.EPSILON and u not in visited:
                        visited.add(u)
                        queue.append((u, v)) # Store (node_to_visit, parent_node)

            return None # No path found

        # --- Scene Introduction ---
        main_title = Text("Ford-Fulkerson Algorithm").to_edge(UP, buff=0.5).set_color(self.TITLE_COLOR)
        sub_title = Text("The Irrational Capacity Problem").next_to(main_title, DOWN).scale(0.8).set_color(self.TITLE_COLOR) # Corrected: next_to
        self.play(Write(main_title), Write(sub_title))
        self.wait(1)

        total_flow_display = Text(f"Total Flow: {self.total_flow:.{self.FLOAT_PRECISION}f}", color=self.TOTAL_FLOW_COLOR).to_corner(DR).shift(LEFT*0.5)
        self.play(FadeIn(total_flow_display))
        self.wait(0.5)

        # Initial graph state
        update_graph_mobjects() # Draw initial zero flow graph
        step_text = Text("Step 0: Initial State (All flows are zero)").next_to(main_title, DOWN, buff=0.5).set_color(self.TITLE_COLOR)
        self.play(Write(step_text))
        self.wait(1.5)
        self.play(FadeOut(step_text))

        # --- Ford-Fulkerson Algorithm Loop ---
        step_count = 1
        MAX_STEPS = 10 # Limit steps for animation length
        
        while step_count <= MAX_STEPS:
            path = find_augmenting_path()
            
            if not path:
                step_description = Text("No augmenting path found. Max Flow Reached (Theoretically).", color=self.TITLE_COLOR).next_to(main_title, DOWN, buff=0.5)
                self.play(Write(step_description))
                self.wait(2)
                break # Algorithm terminates

            # Calculate bottleneck
            bottleneck = float('inf')
            for u, v in path:
                # Check if (u,v) is an original edge or a reverse edge from original_capacities (v,u)
                if (u,v) in self.original_capacities: # Forward edge in residual graph
                    bottleneck = min(bottleneck, self.residual_capacities[(u, v)])
                else: # Reverse edge in residual graph, corresponds to original (v,u)
                    bottleneck = min(bottleneck, self.residual_capacities[(u, v)]) # Capacity of reverse edge is flow on original (v,u)

            if bottleneck < self.EPSILON:
                # Due to floating point errors, bottleneck might be tiny but not exactly zero
                step_description = Text(f"Bottleneck too small ({bottleneck:.{self.FLOAT_PRECISION+2}f}). Algorithm effectively terminates due to precision.", color=self.TITLE_COLOR).next_to(main_title, DOWN, buff=0.5).scale(0.8)
                self.play(Write(step_description))
                self.wait(2)
                break # Algorithm effectively terminates due to precision limit

            step_description = Text(f"Step {step_count}: Augment by {bottleneck:.{self.FLOAT_PRECISION}f} (Bottleneck: φ^{step_count if step_count > 1 else ''})", color=self.TITLE_COLOR).next_to(main_title, DOWN, buff=0.5)
            self.play(Write(step_description))
            self.wait(0.5)

            # Animate flow packet
            flow_packet = Circle(radius=0.1, color=self.FLOW_ANIMATION_COLOR, fill_opacity=1)
            # Start packet at source node
            self.add(flow_packet.move_to(self.node_mobs["s"][0].get_center())) 

            animations = []
            packet_run_time_per_edge = 0.5 # Adjust for speed of packet animation

            # Update flows and animate packet moving
            current_packet_start_mob = self.node_mobs["s"][0] # Start at source

            for u, v in path:
                # Get the actual arrow Mobject for animation
                arrow_mob = None
                is_reverse_path_segment = False
                if (u,v) in self.original_capacities: # Forward edge in residual graph
                    # Find the specific arrow for (u,v)
                    for group_item in self.edge_group:
                        if isinstance(group_item, VGroup) and isinstance(group_item[0], Arrow):
                            # Compare start/end points to identify the specific arrow Mobject
                            if np.allclose(group_item[0].get_start(), create_arrow_and_labels(u,v,is_reverse=False).get_start()) and \
                               np.allclose(group_item[0].get_end(), create_arrow_and_labels(u,v,is_reverse=False).get_end()):
                                arrow_mob = group_item[0]
                                break
                else: # Reverse edge in residual graph (v,u)
                    is_reverse_path_segment = True
                    # Find the specific arrow for (u,v) which is drawn as (u,v) but represents original (v,u)
                    for group_item in self.edge_group:
                        if isinstance(group_item, VGroup) and isinstance(group_item[0], Arrow):
                            if np.allclose(group_item[0].get_start(), create_arrow_and_labels(u,v,is_reverse=True).get_start()) and \
                               np.allclose(group_item[0].get_end(), create_arrow_and_labels(u,v,is_reverse=True).get_end()):
                                arrow_mob = group_item[0]
                                break
                
                # Apply flow update *before* animation part
                if not is_reverse_path_segment: # Forward original edge
                    self.current_flows[(u, v)] += bottleneck
                    self.residual_capacities[(u, v)] -= bottleneck
                    self.residual_capacities[(v, u)] += bottleneck # Increase reverse residual capacity
                else: # Reverse edge in residual graph, corresponds to original (v,u)
                    original_forward_edge = (v, u)
                    self.current_flows[original_forward_edge] -= bottleneck
                    self.residual_capacities[(u, v)] -= bottleneck # Residual of reverse edge (u,v) decreases
                    self.residual_capacities[original_forward_edge] += bottleneck # Residual of original forward edge (v,u) increases
                
                if arrow_mob:
                    # Move packet along the path segment
                    animations.append(MoveAlongPath(flow_packet, arrow_mob, run_time=packet_run_time_per_edge))
                    # Optionally fade out and reappear at the node center for distinct segments
                    animations.append(flow_packet.animate.move_to(self.node_mobs[v][0].get_center()).set_opacity(0.0))
                    animations.append(flow_packet.animate.set_opacity(1.0)) # reappear at node center
            
            # Play all animations for the path traversal
            self.play(*animations, run_time=packet_run_time_per_edge * len(path))
            self.remove(flow_packet) # Remove final packet

            self.total_flow += bottleneck # Sum total flow after the path is processed

            # Update Mobjects with new state
            self.play(
                total_flow_display.animate.set_text(f"Total Flow: {self.total_flow:.{self.FLOAT_PRECISION}f}"),
                UpdateFromFunc(self.edge_group, lambda m: update_graph_mobjects(highlight_path=path)),
                run_time=1.5
            )
            self.wait(2)
            self.play(FadeOut(step_description))
            step_count += 1
            
        # Final message about non-termination
        final_message_1 = Text(f"The total flow converges to 1 + φ ({1+PHI:.{self.FLOAT_PRECISION}f}),", color=self.TITLE_COLOR).to_edge(UP).shift(DOWN*0.5)
        final_message_2 = Text("but the algorithm never truly terminates due to irrational capacities and floating point precision.", color=self.TITLE_COLOR).next_to(final_message_1, DOWN).scale(0.8)
        self.play(FadeOut(total_flow_display), FadeOut(self.edge_group))
        self.play(Write(final_message_1), Write(final_message_2))
        self.wait(4)
        self.play(FadeOut(final_message_1), FadeOut(final_message_2), FadeOut(main_title), FadeOut(sub_title))
        self.wait(1)