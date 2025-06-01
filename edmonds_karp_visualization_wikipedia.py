from manim import *
import collections
import numpy as np

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.16
REVERSE_ARROW_TIP_LENGTH = 0.12

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 
ITERATION_TEXT_FONT_SIZE = 22
STATUS_TEXT_FONT_SIZE = 20
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
MAX_FLOW_DISPLAY_FONT_SIZE = 20

BUFF_VERY_SMALL = 0.05
BUFF_SMALL = 0.1
BUFF_MED = 0.25
BUFF_LARGE = 0.4
BUFF_XLARGE = 0.6

RING_COLOR = YELLOW_C
RING_STROKE_WIDTH = 3.5
RING_RADIUS_OFFSET = 0.1
RING_Z_INDEX = 20

BFS_PATH_COLORS = [BLUE_B, YELLOW_B, GREEN_B, PURPLE_B, TEAL_B]
DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY
BFS_VISITED_NODE_COLOR = GREEN_D
BFS_CURRENT_NODE_COLOR = YELLOW_D
BFS_EDGE_HIGHLIGHT_WIDTH = 4.5
PATH_EDGE_WIDTH = 5.0

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

REVERSE_EDGE_COLOR = GREY_B
REVERSE_EDGE_OPACITY = 0.25
REVERSE_EDGE_STROKE_WIDTH_FACTOR = 0.6
REVERSE_EDGE_Z_INDEX = 4

EDGE_SHIFT_AMOUNT = 0.12

# Flow pulse animation constants
FLOW_PULSE_COLOR = BLUE_B
FLOW_PULSE_WIDTH_FACTOR = 1.8
FLOW_PULSE_TIME_WIDTH = 0.35
FLOW_PULSE_EDGE_RUNTIME = 0.5
FLOW_PULSE_Z_INDEX_OFFSET = 10
EDGE_UPDATE_RUNTIME = 0.3

BOTTLENECK_EDGE_INDICATE_COLOR = RED_D
BOTTLENECK_CALCULATION_NUMBER_COLOR = BLUE_B

# --- Action Text States ---
ACTION_STATES = {
    "nothing": {"text": "", "color": WHITE},
    "augment": {"text": "augment", "color": GREEN_B},
    "bfs": {"text": "BFS", "color": BLUE_B},
}

class EdmondsKarpVisualizer(Scene):
    # Main class for visualizing the Edmonds-Karp algorithm
    pass 

    def _format_number(self, value, precision=1):
        """Formats a number as an integer if it's whole, otherwise as a float with given precision."""
        if value == int(value):
            return f"{int(value)}"
        else:
            return f"{value:.{precision}f}"

    def _create_edge_arrow(
        self,
        start_node_mob: VGroup,
        end_node_mob: VGroup,
        start_pos_override=None,
        end_pos_override=None,
        tip_length=ARROW_TIP_LENGTH,
        color=DEFAULT_EDGE_COLOR,
        stroke_width=EDGE_STROKE_WIDTH
    ):
        """
        Creates an Arrow mobject between two nodes, ensuring the arrowhead
        stops precisely at the node's border.
        """
        start_dot = start_node_mob[0]
        end_dot = end_node_mob[0]

        start_pos = start_pos_override if start_pos_override is not None else start_dot.get_center()
        end_pos = end_pos_override if end_pos_override is not None else end_dot.get_center()

        if np.linalg.norm(end_pos - start_pos) < 1e-6:
            return VGroup()

        direction = normalize(end_pos - start_pos)
        start_buffer = start_dot.width / 2
        end_buffer = end_dot.width / 2

        line_start_point = start_pos + direction * start_buffer
        line_end_point = end_pos - direction * end_buffer

        return Arrow(
            line_start_point,
            line_end_point,
            buff=0,
            stroke_width=stroke_width,
            color=color,
            tip_length=tip_length,
            z_index=5
        )

    def setup_titles_and_placeholders(self):
        """Initialize text mobjects for titles and status displays"""
        self.main_title = Text("Visualizing Edmonds-Karp Algorithm for Max Flow", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.iteration_text_mobj = Text("", font_size=ITERATION_TEXT_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.calculation_details_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.max_flow_display_mobj = Text("", font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.iteration_text_mobj,
            self.algo_status_mobj,
            self.calculation_details_mobj
        ).arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        self.add(self.info_texts_group)

        self.action_text_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD, color=YELLOW).set_z_index(RING_Z_INDEX + 50)

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        """Animate transition between old and new text mobjects"""
        old_text_had_actual_content = False
        if isinstance(old_mobj, Text) and old_mobj.text != "": old_text_had_actual_content = True
        elif isinstance(old_mobj, Tex) and old_mobj.tex_string != "": old_text_had_actual_content = True
        elif isinstance(old_mobj, MarkupText) and old_mobj.text != "": old_text_had_actual_content = True

        new_text_has_actual_content = bool(new_text_content_str and new_text_content_str != "")

        anims_to_play = []
        if old_text_had_actual_content:
            anims_to_play.append(FadeOut(old_mobj, scale=0.8, run_time=0.25))

        if new_text_has_actual_content:
            anims_to_play.append(FadeIn(new_mobj, scale=1.2, run_time=0.25))

        if anims_to_play:
            self.play(*anims_to_play)

    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False, is_markup=False):
        """Generic method to update text mobjects with animation"""
        old_mobj = getattr(self, text_attr_name)

        if is_markup:
            new_mobj = MarkupText(new_text_content, font_size=font_size, color=color)
        elif is_latex:
            new_mobj = Tex(new_text_content, color=color)
            ref_text_for_height = Text("Mg", font_size=font_size)
            if ref_text_for_height.height > 0.001 and new_mobj.height > 0.001 and new_mobj.tex_string:
                new_mobj.scale_to_fit_height(ref_text_for_height.height)
        else:
            new_mobj = Text(new_text_content, font_size=font_size, weight=weight, color=color)

        current_idx = -1
        is_in_info_group = hasattr(self, 'info_texts_group') and old_mobj in self.info_texts_group.submobjects

        if is_in_info_group:
            current_idx = self.info_texts_group.submobjects.index(old_mobj)
            new_mobj.move_to(old_mobj.get_center())
            self.info_texts_group.remove(old_mobj)
        elif old_mobj in self.mobjects:
             new_mobj.move_to(old_mobj.get_center())

        if old_mobj in self.mobjects:
            self.remove(old_mobj)

        if current_idx != -1:
            self.info_texts_group.insert(current_idx, new_mobj)
        
        setattr(self, text_attr_name, new_mobj)

        if is_in_info_group:
            self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') and old_mobj.z_index is not None else 10)

        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_content)
        else:
            is_empty_new_content = False
            if isinstance(new_mobj, Text) and not new_mobj.text: is_empty_new_content = True
            elif isinstance(new_mobj, Tex) and not new_mobj.tex_string: is_empty_new_content = True
            elif isinstance(new_mobj, MarkupText) and not new_mobj.text: is_empty_new_content = True

            if not is_empty_new_content:
                if not is_in_info_group and new_mobj not in self.mobjects:
                     self.add(new_mobj)

    def update_section_title(self, text_str, play_anim=True):
        """Update the section title text"""
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_iteration_text(self, text_str, color=WHITE, play_anim=True):
        """Update the iteration text"""
        self._update_text_generic("iteration_text_mobj", text_str, ITERATION_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        """Update the algorithm status text"""
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex, is_markup=False)

    def update_max_flow_display(self, play_anim=True):
        """Update the maximum flow value display"""
        new_text_str = self._format_number(self.max_flow_value)
        old_mobj = self.max_flow_display_mobj
        
        new_mobj = Text(new_text_str, font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)
        
        if hasattr(self, 'sink_node') and self.sink_node in self.node_mobjects:
            sink_dot = self.node_mobjects[self.sink_node][0]
            new_mobj.next_to(sink_dot, DOWN, buff=BUFF_MED)
        
        if old_mobj in self.mobjects:
            self.remove(old_mobj)

        setattr(self, "max_flow_display_mobj", new_mobj)
        
        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_str)
        else: 
            is_empty_new_content = (isinstance(new_mobj, Text) and new_mobj.text == "")
            if not is_empty_new_content and new_mobj not in self.mobjects:
                self.add(new_mobj)

    def display_calculation_details(self, path_edges=None, bottleneck_value=None, play_anim=True):
        """Display the bottleneck calculation details for an augmenting path"""
        if path_edges is None or bottleneck_value is None:
            self._update_text_generic("calculation_details_mobj", "", STATUS_TEXT_FONT_SIZE, NORMAL, WHITE, play_anim, is_markup=False)
            return
            
        min_parts = []
        for u, v in path_edges:
            res_cap = self.capacities.get((u, v), 0) - self.flow.get((u, v), 0)
            u_display = "s" if u == self.source_node else "t" if u == self.sink_node else str(u)
            v_display = "s" if v == self.source_node else "t" if v == self.sink_node else str(v)
            
            formatted_res_cap = self._format_number(res_cap)
            min_parts.append(f"<span fgcolor='{BOTTLENECK_CALCULATION_NUMBER_COLOR.to_hex()}'>{formatted_res_cap}</span> on {u_display}→{v_display}")
        
        formatted_bottleneck_val = self._format_number(bottleneck_value)
        calculation_markup_str = f"Bottleneck = min({', '.join(min_parts)}) = <span fgcolor='{BOTTLENECK_CALCULATION_NUMBER_COLOR.to_hex()}'>{formatted_bottleneck_val}</span>"
        
        self._update_text_generic("calculation_details_mobj", calculation_markup_str, STATUS_TEXT_FONT_SIZE, NORMAL, YELLOW_B, play_anim, is_markup=True)

    def _update_action_text(self, state: str, animate=True):
        """Update the action text that appears near the source node"""
        state_info = ACTION_STATES.get(state)
        if not state_info:
            print(f"Warning: Invalid action state '{state}' provided.")
            return

        new_text_str = state_info["text"]
        new_color = state_info["color"]

        current_mobj = self.action_text_mobj
        old_text_str = current_mobj.text

        if old_text_str == new_text_str and current_mobj.get_color() == new_color:
            return

        target_mobj = Text(
            new_text_str,
            font_size=STATUS_TEXT_FONT_SIZE,
            weight=BOLD,
            color=new_color
        )
        target_mobj.set_z_index(current_mobj.z_index)

        if hasattr(self, 'source_node') and self.source_node in self.node_mobjects:
            source_dot = self.node_mobjects[self.source_node][0]
            target_mobj.next_to(source_dot, UP, buff=BUFF_LARGE)
        else:
            target_mobj.move_to(current_mobj.get_center())

        if animate:
            if old_text_str and not new_text_str:
                self.play(FadeOut(current_mobj, run_time=0.3))
            elif not old_text_str and new_text_str:
                if current_mobj in self.mobjects: self.remove(current_mobj) 
                self.add(target_mobj)    
                self.play(FadeIn(target_mobj, run_time=0.3))
            else: 
                self.play(ReplacementTransform(current_mobj, target_mobj))
        else:
            if current_mobj in self.mobjects: self.remove(current_mobj)
            if new_text_str: 
                self.add(target_mobj)

        self.action_text_mobj = target_mobj

    def _bfs_find_augmenting_path(self):
        """
        Performs BFS to find an augmenting path from source to sink in the residual graph.
        Animates the BFS traversal process in detail.
        
        This is the key difference between Edmonds-Karp and Ford-Fulkerson:
        Edmonds-Karp always uses BFS to find the shortest augmenting path.
        
        Returns:
            tuple: (path_edges, bottleneck_capacity) or (None, 0) if no path exists
        """
        
        self.update_status_text(f"BFS: Searching for shortest path from S ({self.source_node}) to T ({self.sink_node}) in residual graph.", 
                               color=BLUE_B, play_anim=True)
        self._update_action_text("bfs", animate=True)
        self.wait(1.5)

        # Setup for BFS search
        parent = {v_id: None for v_id in self.vertices_data}
        visited = {v_id: False for v_id in self.vertices_data}
        queue = collections.deque([self.source_node])
        visited[self.source_node] = True
        
        # We'll use these to animate the traversal
        bfs_visited_nodes = set([self.source_node])
        bfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1)
        
        # Visual highlight of source node to start
        source_dot, _ = self.node_mobjects[self.source_node]
        source_highlight = Circle(
            radius=source_dot.width/2 + RING_RADIUS_OFFSET,
            color=BFS_PATH_COLORS[0],
            stroke_width=RING_STROKE_WIDTH
        ).move_to(source_dot.get_center()).set_z_index(RING_Z_INDEX)
        bfs_traversal_highlights.add(source_highlight)
        self.play(Create(source_highlight), run_time=0.3)
        self.wait(0.5)
        
        # BFS main loop
        found_path = False
        path_edges = []
        bottleneck_flow = float('inf')
        
        while queue and not found_path:
            current = queue.popleft()
            current_display_name = "s" if current == self.source_node else "t" if current == self.sink_node else str(current)
            
            # Get current node visual
            current_dot, _ = self.node_mobjects[current]
            
            # Show we're processing this node
            self.update_status_text(f"BFS: Processing node {current_display_name}...", color=YELLOW_D, play_anim=True)
            current_processing_indicator = SurroundingRectangle(
                self.node_mobjects[current], 
                color=YELLOW_D, 
                buff=0.03, 
                stroke_width=2.0, 
                corner_radius=0.05
            ).set_z_index(RING_Z_INDEX - 1)
            self.play(Create(current_processing_indicator), run_time=0.2)
            self.wait(0.5)
            
            # Check all neighbors in sorted order (for consistency)
            for neighbor in sorted(self.adj[current]):
                # Skip if already visited
                if visited[neighbor]:
                    continue
                
                # Check if there's residual capacity
                edge_key = (current, neighbor)
                residual_cap = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                edge_mo = self.edge_mobjects.get(edge_key)
                
                # Show exploring this edge if it exists
                if edge_mo:
                    neighbor_name = "s" if neighbor == self.source_node else "t" if neighbor == self.sink_node else str(neighbor)
                    self.update_status_text(f"BFS: Checking edge {current_display_name} → {neighbor_name} (Residual cap: {self._format_number(residual_cap)})", 
                                          color=WHITE, play_anim=True)
                    self.play(edge_mo.animate.set_color(YELLOW_C).set_opacity(0.7), run_time=0.2)
                    self.wait(0.3)
                    
                    # If there's residual capacity, add to BFS queue
                    if residual_cap > 0:
                        # Record path information
                        parent[neighbor] = current
                        visited[neighbor] = True
                        bfs_visited_nodes.add(neighbor)
                        queue.append(neighbor)
                        
                        # Animate edge and node highlighting
                        neighbor_dot, _ = self.node_mobjects[neighbor]
                        neighbor_highlight = Circle(
                            radius=neighbor_dot.width/2 + RING_RADIUS_OFFSET,
                            color=BFS_PATH_COLORS[len(bfs_visited_nodes) % len(BFS_PATH_COLORS)],
                            stroke_width=RING_STROKE_WIDTH
                        ).move_to(neighbor_dot.get_center()).set_z_index(RING_Z_INDEX)
                        bfs_traversal_highlights.add(neighbor_highlight)
                        
                        # Animate the successful edge traversal
                        self.update_status_text(f"BFS: Found edge with residual capacity {self._format_number(residual_cap)}. Adding {neighbor_name} to queue.", 
                                              color=GREEN_C, play_anim=True)
                        self.play(
                            edge_mo.animate.set_color(BLUE_C).set_opacity(1.0).set_stroke(width=BFS_EDGE_HIGHLIGHT_WIDTH),
                            Create(neighbor_highlight),
                            run_time=0.4
                        )
                        self.wait(0.5)
                        
                        # Check if we've reached the sink
                        if neighbor == self.sink_node:
                            self.update_status_text(f"BFS: Found path to sink T (Node {self.sink_node})!", 
                                                  color=GREEN_B, play_anim=True)
                            found_path = True
                            break
                    else:
                        # No residual capacity - show and restore original appearance
                        self.update_status_text(f"BFS: Edge has no residual capacity, cannot use.", 
                                              color=RED_C, play_anim=True)
                        self.play(
                            edge_mo.animate.set_color(self.base_edge_visual_attrs[edge_key]["color"])
                                           .set_opacity(self.base_edge_visual_attrs[edge_key]["opacity"])
                                           .set_stroke(width=self.base_edge_visual_attrs[edge_key]["stroke_width"]),
                            run_time=0.2
                        )
                        self.wait(0.3)
            
            # Done processing this node
            self.play(FadeOut(current_processing_indicator), run_time=0.2)
            
            # If we found a path to the sink, stop the BFS
            if found_path:
                break
                
            # If the queue is empty and we haven't found a path, we're done
            if not queue:
                self.update_status_text("BFS: No augmenting path found. Max flow achieved.", 
                                      color=RED_C, play_anim=True)
                self.wait(1.0)
                
                # Clean up visual highlights
                if bfs_traversal_highlights.submobjects:
                    self.play(FadeOut(bfs_traversal_highlights), run_time=0.3)
                return None, 0
        
        # If we found a path, reconstruct it from parent pointers
        if found_path:
            self.update_status_text("BFS: Reconstructing augmenting path...", color=GREEN_C, play_anim=True)
            self.wait(0.5)
            
            # Trace back from sink to source
            current = self.sink_node
            while current != self.source_node:
                prev = parent[current]
                edge_key = (prev, current)
                
                # Add edge to path and find bottleneck flow
                path_edges.append(edge_key)
                residual_cap = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                bottleneck_flow = min(bottleneck_flow, residual_cap)
                
                # Prepare for next iteration
                current = prev
            
            # Reverse path to go from source to sink
            path_edges.reverse()
            
            # Highlight the augmenting path
            self.update_status_text(f"BFS: Found augmenting path with bottleneck flow {self._format_number(bottleneck_flow)}.", 
                                  color=GREEN_B, play_anim=True)
            
            # Highlight edges in the path
            path_highlight_anims = []
            for u, v in path_edges:
                edge_mo = self.edge_mobjects[(u, v)]
                path_highlight_anims.append(
                    edge_mo.animate.set_color(GREEN_D).set_opacity(1.0).set_stroke(width=PATH_EDGE_WIDTH)
                )
            if path_highlight_anims:
                self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.1), run_time=0.5)
            
            # Clean up BFS highlights but leave path highlighted
            clean_highlights = [h for h in bfs_traversal_highlights if h not in path_edges]
            if clean_highlights:
                self.play(FadeOut(VGroup(*clean_highlights)), run_time=0.3)
            
            self.wait(1.0)
            return path_edges, bottleneck_flow
        
        # Fallback (should not reach here)
        if bfs_traversal_highlights.submobjects:
            self.play(FadeOut(bfs_traversal_highlights), run_time=0.3)
        return None, 0
        
    def _augment_path(self, path_edges, bottleneck_flow):
        """
        Augments flow along the given path by the bottleneck value.
        Animates the flow augmentation with detailed visual effects.
        
        Args:
            path_edges: List of (u, v) edge tuples representing the augmenting path
            bottleneck_flow: The bottleneck capacity of the path
        """
        if not path_edges or bottleneck_flow <= 0:
            return
            
        # Display calculation details for bottleneck
        self.display_calculation_details(path_edges, bottleneck_flow, play_anim=True)
        self.wait(1.5)
        
        # Set status and action text
        self.update_status_text(f"Augmenting flow by {self._format_number(bottleneck_flow)} along the path...", color=GREEN_B, play_anim=True)
        self._update_action_text("augment", animate=True)
        self.wait(1.0)
        
        # Create animations for dynamic reverse edges if needed
        pre_augment_animations = []
        
        for u, v in path_edges:
            # Check if we need to create a reverse edge
            if (v, u) not in self.edge_mobjects:
                # Create visual for reverse edge
                u_dot, v_dot = self.node_mobjects[u][0], self.node_mobjects[v][0]
                u_center, v_center = u_dot.get_center(), v_dot.get_center()
                
                # Calculate perpendicular vector for edge separation
                perp_vector = rotate_vector(normalize(v_center - u_center), PI / 2)
                fwd_shift_vector = perp_vector * EDGE_SHIFT_AMOUNT
                rev_shift_vector = perp_vector * -EDGE_SHIFT_AMOUNT
                
                # Calculate positions for the reverse edge
                rev_start_pos = v_center + rev_shift_vector
                rev_end_pos = u_center + rev_shift_vector
                
                # Create reverse edge arrow
                base_arrow_rev = self._create_edge_arrow(
                    self.node_mobjects[v], self.node_mobjects[u],
                    start_pos_override=rev_start_pos,
                    end_pos_override=rev_end_pos,
                    tip_length=REVERSE_ARROW_TIP_LENGTH,
                    color=REVERSE_EDGE_COLOR,
                    stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR
                )
                
                # Make it dashed for residual edge appearance
                dashed_line_rev = DashedVMobject(base_arrow_rev[0], num_dashes=12, dashed_ratio=0.6)
                rev_arrow = VGroup(dashed_line_rev, base_arrow_rev.tip)
                rev_arrow.set_z_index(REVERSE_EDGE_Z_INDEX).set_color(REVERSE_EDGE_COLOR).set_opacity(0)
                
                # Store in our edge collections
                self.edge_mobjects[(v, u)] = rev_arrow
                self.base_edge_visual_attrs[(v, u)] = {
                    "color": rev_arrow.get_color(),
                    "stroke_width": rev_arrow.get_stroke_width(),
                    "opacity": REVERSE_EDGE_OPACITY
                }
                
                # Create capacity label for reverse edge
                res_cap_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR, opacity=0.0)
                res_cap_mobj.move_to(dashed_line_rev.get_center()).rotate(base_arrow_rev[0].get_angle())
                offset_vec_lbl = rotate_vector(base_arrow_rev[0].get_unit_vector(), PI / 2) * 0.15
                res_cap_mobj.shift(offset_vec_lbl).set_z_index(6)
                
                self.edge_residual_capacity_mobjects[(v, u)] = res_cap_mobj
                self.edge_label_groups[(v, u)] = VGroup(res_cap_mobj)
                self.base_label_visual_attrs[(v, u)] = {"opacity": 0.0}
                
                # Add to scene
                self.network_display_group.add(rev_arrow, res_cap_mobj)
                self.add(rev_arrow, res_cap_mobj)
                
                # Animate forward edge shifting and reverse edge appearing
                forward_edge_mo = self.edge_mobjects[(u, v)]
                forward_label = self.edge_label_groups.get((u, v))
                
                anim_fwd_edge = forward_edge_mo.animate.shift(fwd_shift_vector)
                anim_fwd_label = forward_label.animate.shift(fwd_shift_vector) if forward_label else AnimationGroup()
                anim_rev_edge = rev_arrow.animate.set_opacity(REVERSE_EDGE_OPACITY)
                
                pre_augment_animations.append(AnimationGroup(anim_fwd_edge, anim_fwd_label, anim_rev_edge))
        
        # Play the animations for creating/adjusting reverse edges
        if pre_augment_animations:
            self.play(AnimationGroup(*pre_augment_animations, lag_ratio=0.1), run_time=0.6)
            self.wait(0.5)
        
        # Identify and highlight bottleneck edges
        bottleneck_edges = []
        for u, v in path_edges:
            edge_key = (u, v)
            res_cap = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
            if abs(res_cap - bottleneck_flow) < 0.01:  # This edge is a bottleneck
                bottleneck_edges.append(self.edge_mobjects[edge_key])
        
        if bottleneck_edges:
            self.update_status_text(f"Highlighting bottleneck edges with capacity {self._format_number(bottleneck_flow)}...", 
                                  color=YELLOW_A, play_anim=True)
            bottleneck_anims = [
                Indicate(edge, color=BOTTLENECK_EDGE_INDICATE_COLOR, scale_factor=1.05, run_time=1.2)
                for edge in bottleneck_edges
            ]
            self.play(AnimationGroup(*bottleneck_anims))
            self.wait(0.5)
        
        # Animate flow augmentation along the path
        self.update_status_text(f"Sending {self._format_number(bottleneck_flow)} units of flow along the path...", 
                              color=GREEN_A, play_anim=True)
        self.wait(0.5)
        
        # Sequential animation of flow through each edge
        path_augmentation_sequence = []
        
        for u, v in path_edges:
            edge_mo = self.edge_mobjects[(u, v)]
            animations_for_edge = []
            
            # 1. Flow pulse animation
            flash_edge_copy = edge_mo.copy()
            flash_edge_copy.set_color(FLOW_PULSE_COLOR)
            flash_edge_copy.set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR, opacity=1.0)
            flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)
            
            pulse_animation = ShowPassingFlash(
                flash_edge_copy, 
                time_width=FLOW_PULSE_TIME_WIDTH, 
                run_time=FLOW_PULSE_EDGE_RUNTIME
            )
            animations_for_edge.append(pulse_animation)
            
            # 2. Prepare animations for number/visual updates
            text_updates = []
            visual_updates = []
            
            # Update flow values (internal data)
            self.flow[(u, v)] = self.flow.get((u, v), 0) + bottleneck_flow
            self.flow[(v, u)] = self.flow.get((v, u), 0) - bottleneck_flow
            
            # Update flow text on original edges
            if (u, v) in self.original_edge_tuples:
                old_flow_text = self.edge_flow_val_text_mobjects[(u, v)]
                new_flow_val = self.flow[(u, v)]
                new_flow_str = self._format_number(new_flow_val)
                target_text = Text(
                    new_flow_str, 
                    font=old_flow_text.font, 
                    font_size=old_flow_text.font_size, 
                    color=LABEL_TEXT_COLOR
                )
                
                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                    target_text.height = self.scaled_flow_text_height
                    
                target_text.move_to(old_flow_text.get_center()).rotate(edge_mo.get_angle(), about_point=target_text.get_center())
                text_updates.append(old_flow_text.animate.become(target_text))
            
            # Calculate residual capacity after augmentation
            res_cap_after = self.capacities.get((u, v), 0) - self.flow.get((u, v), 0)
            
            # Update forward edge visual based on remaining capacity
            if res_cap_after > 0:
                visual_updates.append(
                    edge_mo.animate.set_color(BLUE_C).set_opacity(1.0).set_stroke(width=BFS_EDGE_HIGHLIGHT_WIDTH)
                )
            else:
                # Saturated edge (no residual capacity)
                visual_updates.append(
                    edge_mo.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH)
                )
                
                # Hide residual capacity label if it's not an original edge
                if (u, v) not in self.original_edge_tuples:
                    label_mobj = self.edge_residual_capacity_mobjects.get((u, v))
                    if label_mobj:
                        visual_updates.append(label_mobj.animate.set_opacity(0.0))
            
            # Update reverse edge
            if (v, u) in self.edge_mobjects:
                rev_edge_mo = self.edge_mobjects[(v, u)]
                rev_res_cap = self.capacities.get((v, u), 0) - self.flow.get((v, u), 0)
                
                # Positive flow creates positive residual capacity on reverse edge
                if rev_res_cap > 0 or self.flow.get((u, v), 0) > 0:
                    # Reverse edge should be visible (there's flow that can be "undone")
                    visual_updates.append(
                        rev_edge_mo.animate.set_color(REVERSE_EDGE_COLOR).set_opacity(REVERSE_EDGE_OPACITY)
                    )
                    
                    # Update reverse edge capacity label if it's not original
                    if (v, u) not in self.original_edge_tuples:
                        rev_label = self.edge_residual_capacity_mobjects.get((v, u))
                        if rev_label:
                            new_rev_flow = self.flow.get((u, v), 0)  # Residual capacity on reverse = flow on forward
                            if new_rev_flow > 0:
                                target_rev_label = Text(
                                    self._format_number(new_rev_flow), 
                                    font=rev_label.font, 
                                    font_size=rev_label.font_size, 
                                    color=REVERSE_EDGE_COLOR
                                )
                                target_rev_label.move_to(rev_label.get_center()).set_opacity(0.8)
                                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                    target_rev_label.height = self.scaled_flow_text_height * 0.9
                                text_updates.append(rev_label.animate.become(target_rev_label))
                            else:
                                visual_updates.append(rev_label.animate.set_opacity(0.0))
                else:
                    # No residual capacity on reverse edge
                    visual_updates.append(
                        rev_edge_mo.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY * 0.5)
                    )
                    
                    # Hide reverse edge label
                    if (v, u) not in self.original_edge_tuples:
                        rev_label = self.edge_residual_capacity_mobjects.get((v, u))
                        if rev_label:
                            visual_updates.append(rev_label.animate.set_opacity(0.0))
            
            # Group all updates for this edge
            if text_updates or visual_updates:
                update_group = AnimationGroup(
                    *(text_updates + visual_updates),
                    lag_ratio=0.0,
                    run_time=EDGE_UPDATE_RUNTIME
                )
                animations_for_edge.append(update_group)
            
            # Add this edge's animation sequence to the overall path sequence
            path_augmentation_sequence.append(Succession(*animations_for_edge, lag_ratio=1.0))
        
        # Play the entire path augmentation sequence
        if path_augmentation_sequence:
            self.play(Succession(*path_augmentation_sequence, lag_ratio=1.0))
            self.wait(0.5)
        
        # Update max flow display
        self.max_flow_value += bottleneck_flow
        self.update_max_flow_display(play_anim=True)
        
        # Clear action text and update status
        self._update_action_text("nothing", animate=True)
        self.update_status_text(f"Flow augmented by {self._format_number(bottleneck_flow)}. Current maximum flow: {self._format_number(self.max_flow_value)}.", 
                              color=WHITE, play_anim=True)
        self.wait(1.0)
        
        # Clear calculation details
        self.display_calculation_details(None, None, play_anim=True)
        
    def construct(self):
        """
        Main method that constructs the Edmonds-Karp algorithm visualization.
        Sets up the graph and iteratively runs BFS to find augmenting paths.
        """
        # Initialize titles and text displays
        self.setup_titles_and_placeholders()
        if self.action_text_mobj not in self.mobjects:
            self.add(self.action_text_mobj)
            
        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)
        
        # Initialize variables for the algorithm
        self.scaled_flow_text_height = None  # Will be set after creating labels
        self.update_section_title("1. Building the Flow Network", play_anim=True)
        
        self.current_iteration_num = 0
        self.max_flow_value = 0
        
        # Define graph structure (nodes, edges, capacities)
        self.source_node, self.sink_node = 1, 7
        self.vertices_data = list(range(1, 8))
        self.edges_with_capacity_list = [
            (1,2,3),(1,4,3),(2,3,4),(3,1,3),(3,4,1),(3,5,2),
            (4,5,2),(4,6,6),(5,2,1),(5,7,1),(6,7,9)
        ]
        self.original_edge_tuples = set([(u,v) for u,v,c in self.edges_with_capacity_list])
        
        # Initialize data structures
        self.capacities = collections.defaultdict(int)  # Stores (u,v) -> capacity
        self.flow = collections.defaultdict(int)        # Stores (u,v) -> flow
        self.adj = collections.defaultdict(list)        # Adjacency list for graph traversal
        
        # Build the graph data
        for u, v, cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u)  # For residual graph traversal
            
        # Define layout for nodes
        self.graph_layout = {
            1: [-3,1,0], 2:[-3,-1,0], 3:[-1,0,0], 4:[1,1,0],
            5:[1,-1,0], 6:[3,1,0], 7: [3,-1,0]
        }
        
        # Dictionaries to store mobjects for nodes, edges, and labels
        self.node_mobjects = {}
        self.edge_mobjects = {}
        self.edge_capacity_text_mobjects = {}
        self.edge_flow_val_text_mobjects = {}
        self.edge_slash_text_mobjects = {}
        self.edge_label_groups = {}
        self.base_label_visual_attrs = {}
        self.edge_residual_capacity_mobjects = {}
        
        self.desired_large_scale = 1.1  # Scale factor for the main graph display
        
        # Create and animate node mobjects (dots and labels)
        nodes_vgroup = VGroup()
        for v_id in self.vertices_data:
            dot = Dot(
                point=self.graph_layout[v_id], 
                radius=NODE_RADIUS, 
                color=DEFAULT_NODE_COLOR, 
                z_index=10, 
                stroke_color=BLACK, 
                stroke_width=NODE_STROKE_WIDTH
            )
            label = Text(
                str(v_id), 
                font_size=NODE_LABEL_FONT_SIZE, 
                weight=BOLD
            ).move_to(dot.get_center()).set_z_index(11)
            
            self.node_mobjects[v_id] = VGroup(dot, label)
            nodes_vgroup.add(self.node_mobjects[v_id])
            
        self.play(
            LaggedStart(
                *[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data],
                lag_ratio=0.05
            ),
            run_time=1.5
        )
        self.wait(0.5)
        
        # Create and animate edge mobjects (arrows)
        edges_vgroup = VGroup()
        edge_grow_anims = []
        
        for u, v, cap in self.edges_with_capacity_list:
            arrow = self._create_edge_arrow(
                self.node_mobjects[u],
                self.node_mobjects[v],
                tip_length=ARROW_TIP_LENGTH,
                color=DEFAULT_EDGE_COLOR,
                stroke_width=EDGE_STROKE_WIDTH
            )
            self.edge_mobjects[(u, v)] = arrow
            edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
            
        self.play(
            LaggedStart(*edge_grow_anims, lag_ratio=0.05),
            run_time=1.5
        )
        self.wait(0.5)
        
        # Create and animate edge labels (flow/capacity)
        all_edge_labels_vgroup = VGroup()
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []
        
        for u, v, cap in self.edges_with_capacity_list:
            arrow = self.edge_mobjects[(u, v)]
            
            # Create flow value, slash, and capacity text
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)
            
            # Store text mobjects in their respective dictionaries
            self.edge_flow_val_text_mobjects[(u, v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u, v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u, v)] = cap_text_mobj
            self.base_label_visual_attrs[(u, v)] = {"opacity": 1.0}  # Original labels are fully opaque
            
            # Group and position the label components
            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            label_group.move_to(arrow.get_center()).rotate(arrow.get_angle())
            
            # Offset label from edge
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.15
            label_group.shift(offset_vector).set_z_index(6)
            
            # Store and add to scene
            self.edge_label_groups[(u, v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            
            # Prepare animations
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))
            
        # Animate the appearance of capacity values
        if capacities_to_animate_write:
            self.play(
                LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05),
                run_time=1.2
            )
            self.wait(0.5)
            
        # Animate the appearance of flow values and slashes
        if flow_slashes_to_animate_write:
            self.play(
                LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05),
                run_time=1.2
            )
            self.wait(0.5)
            
        # Group all network elements and scale/position them
        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        
        # Store base visual attributes for edges (color, width, opacity) for restoration
        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(),
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }
            
            if edge_key not in self.base_label_visual_attrs:
                if edge_key in self.original_edge_tuples:
                    self.base_label_visual_attrs[edge_key] = {"opacity": 1.0}
                else:
                    self.base_label_visual_attrs[edge_key] = {"opacity": 0.0}
                    
        # Animate scaling and positioning the network
        self.play(
            self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position)
        )
        self.wait(0.5)
        
        # Position the action text near the source node
        if hasattr(self, 'node_mobjects') and self.source_node in self.node_mobjects:
            source_dot = self.node_mobjects[self.source_node][0]
            self.action_text_mobj.next_to(source_dot, UP, buff=BUFF_SMALL)
        else:
            self.action_text_mobj.to_corner(UL, buff=BUFF_MED)
            
        # Determine scaled height for flow text labels for consistency
        sample_text_mobj = None
        for key_orig_edge in self.original_edge_tuples:
            if key_orig_edge in self.edge_flow_val_text_mobjects:
                sample_text_mobj = self.edge_flow_val_text_mobjects[key_orig_edge]
                break
                
        if sample_text_mobj:
            self.scaled_flow_text_height = sample_text_mobj.height
        else:
            dummy_text_unscaled = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text_unscaled.scale(self.desired_large_scale).height
            
        # Store base visual attributes for nodes
        self.base_node_visual_attrs = {}
        for v_id, node_group in self.node_mobjects.items():
            dot, label = node_group
            self.base_node_visual_attrs[v_id] = {
                "width": dot.width,
                "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(),
                "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity(),
                "label_color": label.get_color()
            }
            
        # Highlight source and sink nodes
        source_dot = self.node_mobjects[self.source_node][0]
        sink_dot = self.node_mobjects[self.sink_node][0]
        
        temp_source_ring = Circle(
            radius=source_dot.width / 2 + RING_RADIUS_OFFSET,
            color=RING_COLOR,
            stroke_width=RING_STROKE_WIDTH
        ).move_to(source_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        temp_sink_ring = Circle(
            radius=sink_dot.width / 2 + RING_RADIUS_OFFSET,
            color=RING_COLOR,
            stroke_width=RING_STROKE_WIDTH
        ).move_to(sink_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        
        self.play(
            Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, run_time=0.7),
            Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, run_time=0.7)
        )
        
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)
        
        # Change labels of source and sink to "s" and "t"
        source_label_original = self.node_mobjects[self.source_node][1]
        sink_label_original = self.node_mobjects[self.sink_node][1]
        
        new_s_label = Text(
            "s", 
            font_size=NODE_LABEL_FONT_SIZE, 
            weight=BOLD, 
            color=self.base_node_visual_attrs[self.source_node]["label_color"]
        ).move_to(source_label_original.get_center()).set_z_index(source_label_original.z_index)
        
        new_t_label = Text(
            "t", 
            font_size=NODE_LABEL_FONT_SIZE, 
            weight=BOLD, 
            color=self.base_node_visual_attrs[self.sink_node]["label_color"]
        ).move_to(sink_label_original.get_center()).set_z_index(sink_label_original.z_index)
        
        self.play(
            Transform(source_label_original, new_s_label),
            Transform(sink_label_original, new_t_label),
            run_time=0.5
        )
        
        self.node_mobjects[self.source_node][1] = new_s_label
        self.node_mobjects[self.sink_node][1] = new_t_label
        self.wait(0.5)
        
        # --- Start the Edmonds-Karp Algorithm ---
        self.update_section_title("2. Running Edmonds-Karp Algorithm", play_anim=True)
        self.wait(1.0)
        
        # Main algorithm loop
        while True:
            self.current_iteration_num += 1
            
            # Update iteration text
            self.update_iteration_text(f"Iteration {self.current_iteration_num}", color=BLUE_C, play_anim=True)
            self.wait(0.5)
            
            # Clear any previous calculation details
            self.display_calculation_details(None, None, play_anim=False)
            
            # Execute BFS to find an augmenting path
            path_edges, bottleneck_flow = self._bfs_find_augmenting_path()
            
            # If no augmenting path found, we're done
            if not path_edges or bottleneck_flow <= 0:
                self.update_status_text("No more augmenting paths found. Maximum flow achieved!", 
                                      color=GREEN_B, play_anim=True)
                self.wait(1.0)
                break
                
            # Augment flow along the found path
            self._augment_path(path_edges, bottleneck_flow)
            
            # After augmenting, add a small wait
            self.wait(1.0)
            
        # Show algorithm summary
        self.update_section_title("3. Edmonds-Karp Algorithm Summary", play_anim=True)
        self.wait(1.0)
        
        self.update_status_text(f"Algorithm concluded. Final max flow: {self._format_number(self.max_flow_value)}", 
                              color=GREEN_A, play_anim=True)
        self.wait(1.0)
        
        # Explain key concepts
        summary_text = (
            "Key insights:\n"
            "1. BFS always finds the shortest augmenting path\n"
            "2. Each augmentation increases the total flow\n"
            "3. The algorithm terminates when no more augmenting paths exist"
        )
        self.update_status_text(summary_text, color=YELLOW_B, play_anim=True)
        self.wait(4.0)
        
        # Final animation for emphasis
        if hasattr(self, 'node_mobjects') and self.node_mobjects and \
           hasattr(self, 'source_node') and hasattr(self, 'sink_node') and \
           self.source_node in self.node_mobjects and self.sink_node in self.node_mobjects:
            
            source_dot = self.node_mobjects[self.source_node][0]
            sink_dot = self.node_mobjects[self.sink_node][0]
            
            other_node_dots = []
            for node_id in self.vertices_data:
                if node_id in self.node_mobjects:
                    if node_id != self.source_node and node_id != self.sink_node:
                        other_node_dots.append(self.node_mobjects[node_id][0])
            
            final_anims = []
            
            # Flash all normal nodes
            final_anims.extend([
                Flash(dot, color=BLUE_A, flash_radius=NODE_RADIUS * 2.0)
                for dot in other_node_dots
            ])
            
            # Special flashes for source and sink
            final_anims.append(Flash(source_dot, color=GOLD_D, flash_radius=NODE_RADIUS * 3.0))
            final_anims.append(Flash(sink_dot, color=RED_C, flash_radius=NODE_RADIUS * 3.0))
            
            if final_anims:
                self.play(*final_anims, run_time=2.0)
        
        self.wait(3.0)

        # Clean up scene, leaving only titles and final status
        mobjects_that_should_remain_on_screen = Group(self.main_title, self.info_texts_group)
        mobjects_that_should_remain_on_screen.remove(*[m for m in mobjects_that_should_remain_on_screen if not isinstance(m, Mobject)])
        final_mobjects_to_fade_out = Group()
        all_descendants_of_kept_mobjects = set()
        for mobj_to_keep in mobjects_that_should_remain_on_screen:
            all_descendants_of_kept_mobjects.update(mobj_to_keep.get_family())
        for mobj_on_scene in list(self.mobjects):
            if mobj_on_scene not in all_descendants_of_kept_mobjects:
                final_mobjects_to_fade_out.add(mobj_on_scene)
        if final_mobjects_to_fade_out.submobjects:
            self.play(FadeOut(final_mobjects_to_fade_out, run_time=1.0))
        self.wait(6)