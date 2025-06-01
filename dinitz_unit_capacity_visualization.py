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
PHASE_TEXT_FONT_SIZE = 22
STATUS_TEXT_FONT_SIZE = 20
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
LEVEL_TEXT_FONT_SIZE = 18
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

LEVEL_COLORS = [RED_D, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK]
DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 4.5
DFS_EDGE_TRY_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.15
DFS_PATH_EDGE_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.25
BOTTLENECK_EDGE_INDICATE_COLOR = RED_D
BOTTLENECK_CALCULATION_NUMBER_COLOR = BLUE_B

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

# --- Sink Action Text States ---
SINK_ACTION_STATES = {
    "nothing": {"text": "", "color": WHITE},
    "augment": {"text": "augment", "color": GREEN_B},
    "retreat": {"text": "retreat", "color": ORANGE},
    "advance": {"text": "advance", "color": YELLOW_A},
}

class DinitzUnitCapacityVisualizer(Scene):
    """
    Visualization of Dinitz's algorithm for maximum flow in unit-capacity networks.
    In unit-capacity networks, all edges have a capacity of 1, which simplifies the algorithm.
    """

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
        self.main_title = Text("Visualizing Dinitz's Algorithm in Unit-Capacity Networks", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.calculation_details_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.max_flow_display_mobj = Text("", font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj,
            self.calculation_details_mobj
        ).arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        self.add(self.info_texts_group)

        self.level_display_vgroup = VGroup().set_z_index(10).to_corner(UR, buff=BUFF_LARGE)
        self.add(self.level_display_vgroup)

        self.sink_action_text_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD, color=YELLOW).set_z_index(RING_Z_INDEX + 50)

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
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
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex, is_markup=False)

    def update_max_flow_display(self, play_anim=True):
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

    def display_path_info(self, path_info=None, play_anim=True):
        """
        For unit capacity networks, we just need to show the path, not the bottleneck calculation
        since the bottleneck is always 1.
        """
        if path_info is None:
            self._update_text_generic("calculation_details_mobj", "", STATUS_TEXT_FONT_SIZE, NORMAL, WHITE, play_anim, is_markup=False)
            return
            
        path_nodes = []
        for (u, v), _ in path_info:
            # Add first node of the first edge
            if len(path_nodes) == 0:
                u_display = "s" if u == self.source_node else "t" if u == self.sink_node else str(u)
                path_nodes.append(u_display)
            
            # Add second node of each edge
            v_display = "s" if v == self.source_node else "t" if v == self.sink_node else str(v)
            path_nodes.append(v_display)
        
        # Create path display text
        path_display = " → ".join(path_nodes)
        path_markup_str = f"Path found: <span fgcolor='{GREEN_B.to_hex()}'>{path_display}</span> (Flow = 1)"
        
        self._update_text_generic("calculation_details_mobj", path_markup_str, STATUS_TEXT_FONT_SIZE, NORMAL, WHITE, play_anim, is_markup=True)

    def _update_sink_action_text(self, state: str, animate=True):
        state_info = SINK_ACTION_STATES.get(state)
        if not state_info:
            print(f"Warning: Invalid sink action state '{state}' provided.")
            return

        new_text_str = state_info["text"]
        new_color = state_info["color"]

        current_mobj = self.sink_action_text_mobj
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

        self.sink_action_text_mobj = target_mobj 

    def _dfs_advance_and_retreat(self, u, current_path_info_list):
        """
        Recursive DFS function to find a path in the level graph, matching ADVANCE/RETREAT logic.
        In unit-capacity networks, we don't need to keep track of bottleneck flow as it's always 1.
        
        Parameters:
        - u: current node
        - current_path_info_list: stores path edges for animation and augmentation
        
        Returns:
        - bool: True if a path to sink was found, False otherwise
        """
        u_dot_group = self.node_mobjects[u]
        u_dot = u_dot_group[0]

        # Highlight the current node being visited in DFS
        highlight_ring = Circle(radius=u_dot.width/2 * 1.3, color=PINK, stroke_width=RING_STROKE_WIDTH * 0.7) \
            .move_to(u_dot.get_center()).set_z_index(u_dot.z_index + 2)
        self.dfs_traversal_highlights.add(highlight_ring)
        self.play(Create(highlight_ring), run_time=0.3)
        self.wait(0.5)

        u_display_name = "s" if u == self.source_node else "t" if u == self.sink_node else str(u)

        if u == self.sink_node: # Path to sink found (successful ADVANCE to t)
            self.update_status_text(f"Path Found: Reached Sink T (Node {self.sink_node})!", color=GREEN_B, play_anim=False)
            self._update_sink_action_text("augment")
            self.wait(2.0)
            self.play(FadeOut(highlight_ring), run_time=0.15) # Remove highlight
            if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
            return True # Path found

        # Iterate through neighbors using the pointer (ptr) for Dinic's optimization
        while self.ptr[u] < len(self.adj[u]):
            # Set state to "advance" before trying each edge
            self._update_sink_action_text("advance")

            v_candidate = self.adj[u][self.ptr[u]]
            edge_key_uv = (u, v_candidate)

            # In unit capacity networks, residual capacity is either 0 or 1
            res_cap_cand = 1 if self.flow.get(edge_key_uv, 0) == 0 else 0
            edge_mo_cand = self.edge_mobjects.get(edge_key_uv)

            # Check if this edge is a valid Level Graph edge (and destination is not a dead end)
            is_valid_lg_edge = (edge_mo_cand and
                               self.levels.get(v_candidate, -1) == self.levels.get(u, -1) + 1 and
                               res_cap_cand > 0 and
                               v_candidate not in self.dead_nodes_in_phase)

            if is_valid_lg_edge:
                actual_v = v_candidate
                edge_mo_for_v = edge_mo_cand
                actual_v_display_name = "s" if actual_v == self.source_node else "t" if actual_v == self.sink_node else str(actual_v)

                # Animate trying this edge
                current_anims_try = [
                    edge_mo_for_v.animate.set_color(YELLOW_A).set_opacity(1.0).set_stroke(width=DFS_EDGE_TRY_WIDTH)
                ]

                # For unit capacity networks, labels are simpler - we don't show residual capacities
                self.update_status_text(f"Advance: Try edge ({u_display_name} → {actual_v_display_name})", play_anim=False)
                self.wait(1.5)
                if current_anims_try: self.play(*current_anims_try, run_time=0.4)
                self.wait(0.5)

                # Recursive call for the next node in the path
                path_found = self._dfs_advance_and_retreat(actual_v, current_path_info_list)

                if path_found: # Path to sink was found through this edge
                    self.update_status_text(f"Path Segment: ({u_display_name} → {actual_v_display_name}) is part of an augmenting path.", color=GREEN_C, play_anim=False)
                    self.wait(1.5)
                    
                    # Add this edge to the path info list
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v))
                    self.play(FadeOut(highlight_ring), run_time=0.15)
                    if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
                    return True # Path found

                # Backtracking: This edge led to a dead end
                self._update_sink_action_text("retreat")
                self.update_status_text(f"Retreat: Edge ({u_display_name} → {actual_v_display_name}) is a dead end. Backtracking.", color=YELLOW_C, play_anim=False)
                self.wait(1.5)
                
                current_anims_backtrack_restore = []

                # Restore edge appearance based on whether it's still a valid LG edge
                current_res_cap_after_fail = 1 if self.flow.get(edge_key_uv, 0) == 0 else 0
                is_still_lg_edge_after_fail = (self.levels.get(actual_v, -1) == self.levels.get(u, -1) + 1 and current_res_cap_after_fail > 0)

                if is_still_lg_edge_after_fail: # Restore to LG appearance
                    lg_color = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(lg_color).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH)
                    )
                else: # Dim the edge as it's no longer useful in this DFS phase
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH)
                    )

                if current_anims_backtrack_restore: self.play(*current_anims_backtrack_restore, run_time=0.4)
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.1, run_time=0.45)) # Indicate dead end
                self.wait(0.5)

            self.ptr[u] += 1 # Move to the next neighbor (Dinic's optimization)

        # All edges from u explored, this node is a dead end. Time to RETREAT from the node.
        self._update_sink_action_text("retreat")
        self.update_status_text(f"Retreat: All edges from {u_display_name} explored. Node is a dead end.", color=ORANGE, play_anim=False)
        self.wait(2.0)

        # "Delete" a node from the LG for this phase once it's a dead end
        if u != self.source_node: # The source node is never a dead end
            self.dead_nodes_in_phase.add(u)
            u_dot, u_lbl = self.node_mobjects[u]

            self.update_status_text(f"Node {u_display_name} deleted from LG for this phase.", color=ORANGE, play_anim=False)
            self.wait(1.5)

            anims_dead_node = [
                u_dot.animate.set_fill(DIMMED_COLOR, opacity=DIMMED_OPACITY * 1.5),
                u_lbl.animate.set_color(GREY)
            ]
            self.play(*anims_dead_node, run_time=0.5)
            self.wait(1.0)

        self.play(FadeOut(highlight_ring), run_time=0.15)
        if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
        return False # No path found from u

    def animate_dfs_path_finding_phase(self):
        """
        Manages the DFS phase of Dinitz's algorithm in unit-capacity networks.
        In this phase, we find multiple s-t paths to form a blocking flow.
        """
        self.ptr = {v_id: 0 for v_id in self.vertices_data} # Pointers for Dinic's DFS optimization
        self.dead_nodes_in_phase = set() # Tracks dead-end nodes for this phase
        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1)
        if self.dfs_traversal_highlights not in self.mobjects: self.add(self.dfs_traversal_highlights)

        self._update_sink_action_text("nothing", animate=False)
        self.display_path_info(None, play_anim=False)

        self.update_phase_text(f"Phase {self.current_phase_num}: Step 2 - Find Blocking Flow in LG (DFS)", color=ORANGE)
        self.update_status_text("Using DFS to find augmenting paths from S to T in the Level Graph.", play_anim=True)
        self.wait(3.0)

        while True: # Loop to find multiple paths in the current LG
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Seeking S→T path from Node {self.source_node}.", play_anim=True)
            self.wait(1.5)
            current_path_anim_info = [] # Stores ((u,v), edge_mo) for the found path

            # Perform DFS to find one s-t path
            path_found = self._dfs_advance_and_retreat(self.source_node, current_path_anim_info)

            if not path_found: # No more s-t paths can be found in the current LG
                self.update_status_text("No more S-T paths in LG. Blocking flow for this phase is complete.", color=YELLOW_C, play_anim=True)
                self.display_path_info(None, play_anim=True)
                self.wait(3.5)
                break # Exit loop for this DFS phase

            # A path was found, update total flow (always 1 in unit-capacity networks)
            self.max_flow_value += 1
            total_flow_this_phase += 1

            current_path_anim_info.reverse() # Path is built from T to S, reverse for S to T animation

            # Display the path information
            self.display_path_info(current_path_anim_info, play_anim=True)
            self.wait(2.0)
            
            # Add a visual explanation of the unit capacity property
            if path_count_this_phase == 1:
                self._create_overlay_text(
                    "In unit-capacity networks, every augmenting path\nincreases the flow by exactly 1 unit",
                    font_size=28,
                    color=BLUE_A,
                    duration=3.5
                )

            # --- DYNAMIC REVERSE EDGE CREATION ---
            pre_augment_animations = []
            for (u, v), _ in current_path_anim_info:
                if (v, u) not in self.edge_mobjects:
                    n_u_dot, n_v_dot = self.node_mobjects[u][0], self.node_mobjects[v][0]
                    u_center, v_center = n_u_dot.get_center(), n_v_dot.get_center()

                    perp_vector = rotate_vector(normalize(v_center - u_center), PI / 2)
                    fwd_shift_vector = perp_vector * EDGE_SHIFT_AMOUNT
                    rev_shift_vector = perp_vector * -EDGE_SHIFT_AMOUNT

                    rev_start_node_center = v_center + rev_shift_vector
                    rev_end_node_center = u_center + rev_shift_vector

                    base_arrow_rev = self._create_edge_arrow(
                        self.node_mobjects[v], self.node_mobjects[u],
                        start_pos_override=rev_start_node_center,
                        end_pos_override=rev_end_node_center,
                        tip_length=REVERSE_ARROW_TIP_LENGTH,
                        color=REVERSE_EDGE_COLOR,
                        stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR
                    )
                    
                    dashed_line_rev = DashedVMobject(base_arrow_rev[0], num_dashes=12, dashed_ratio=0.6)
                    rev_arrow = VGroup(dashed_line_rev, base_arrow_rev.tip)
                    rev_arrow.set_z_index(REVERSE_EDGE_Z_INDEX).set_color(REVERSE_EDGE_COLOR).set_opacity(0)
                    
                    self.edge_mobjects[(v, u)] = rev_arrow
                    self.base_edge_visual_attrs[(v, u)] = {
                        "color": rev_arrow.get_color(),
                        "stroke_width": rev_arrow.get_stroke_width(),
                        "opacity": REVERSE_EDGE_OPACITY
                    }
                    
                    self.network_display_group.add(rev_arrow)
                    self.add(rev_arrow)

                    forward_edge_mo = self.edge_mobjects[(u, v)]

                    anim_fwd_edge = forward_edge_mo.animate.shift(fwd_shift_vector)
                    anim_rev_edge = rev_arrow.animate.set_opacity(REVERSE_EDGE_OPACITY)

                    pre_augment_animations.append(AnimationGroup(anim_fwd_edge, anim_rev_edge))

            if pre_augment_animations:
                self.play(AnimationGroup(*pre_augment_animations, lag_ratio=0.1, run_time=0.6))
                self.wait(0.2)

            self.update_status_text(f"Path #{path_count_this_phase} found. Augmenting flow...", color=GREEN_A, play_anim=True)
            self._update_sink_action_text("augment")
            self.wait(1.0)

            # Highlight the found path in green
            path_highlight_anims_group = []
            for (u_edge, v_edge), edge_mobject in current_path_anim_info:
                path_highlight_anims_group.append(
                    edge_mobject.animate.set_color(GREEN_D).set_opacity(1.0).set_stroke(width=DFS_PATH_EDGE_WIDTH)
                )
            if path_highlight_anims_group:
                self.play(AnimationGroup(*path_highlight_anims_group, lag_ratio=0.15, run_time=0.7))
            self.wait(0.5)

            # --- FLOW PULSE AND VISUAL UPDATE ANIMATION ---
            path_augmentation_sequence = []

            for (u,v), edge_mo in current_path_anim_info:
                animations_for_current_edge_step = []

                # 1. Flow Pulse Animation
                flash_edge_copy = edge_mo.copy()
                flash_edge_copy.set_color(FLOW_PULSE_COLOR).set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR).set_opacity(1.0)
                flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)

                pulse_animation = ShowPassingFlash(
                    flash_edge_copy, time_width=FLOW_PULSE_TIME_WIDTH, run_time=FLOW_PULSE_EDGE_RUNTIME
                )
                animations_for_current_edge_step.append(pulse_animation)

                # 2. Prepare animations for visual updates
                visual_updates_this_edge = []

                # In unit-capacity networks, edges are either flowing (1) or not (0)
                self.flow[(u,v)] = 1  # Set flow to 1 for forward edge
                self.flow[(v,u)] = -1 # Set flow to -1 for reverse edge (cancels out forward)

                # Update edge appearance for forward edge
                visual_updates_this_edge.append(edge_mo.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH))
                
                # Update reverse edge appearance if it exists
                if (v,u) in self.edge_mobjects:
                    rev_edge_mo_vu = self.edge_mobjects[(v,u)]
                    
                    # Activate the reverse edge
                    base_attrs = self.base_edge_visual_attrs.get((v, u), {})
                    color = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]  # Use level color for reverse edge
                    opacity = 0.7
                    width = base_attrs.get("stroke_width", EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR)
                    
                    visual_updates_this_edge.append(
                        rev_edge_mo_vu.animate.set_color(color).set_opacity(opacity).set_stroke(width=width)
                    )

                if visual_updates_this_edge:
                    update_group_for_this_edge = AnimationGroup(
                        *visual_updates_this_edge,
                        lag_ratio=0.0,
                        run_time=EDGE_UPDATE_RUNTIME
                    )
                    animations_for_current_edge_step.append(update_group_for_this_edge)
                
                path_augmentation_sequence.append(Succession(*animations_for_current_edge_step, lag_ratio=1.0))

            if path_augmentation_sequence:
                self.play(Succession(*path_augmentation_sequence, lag_ratio=1.0))
                self.wait(0.5)

            # Clear path info after the augmentation is complete
            self.display_path_info(None, play_anim=False)
            
            self.update_max_flow_display(play_anim=True)
            self.wait(0.5)
            self._update_sink_action_text("nothing", animate=True)
            self.update_status_text(f"Flow augmented. Current phase flow: {total_flow_this_phase}. Searching for next path...", color=WHITE, play_anim=True)
            self.wait(2.5)

            # Update flow labels on the forward edges
            for (u, v), edge_mo in current_path_anim_info:
                if (u, v) in self.edge_label_groups:
                    label = self.edge_label_groups[(u, v)][0]
                    new_label = Text("1/1", font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=GREEN_C)
                    new_label.move_to(label.get_center())
                    self.play(Transform(label, new_label), run_time=0.4)
                
                # Update reverse edge label if it exists
                if (v, u) in self.edge_label_groups:
                    rev_label = self.edge_label_groups[(v, u)][0]
                    new_rev_label = Text("0/1", font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=GREY_C)
                    new_rev_label.move_to(rev_label.get_center())
                    self.play(Transform(rev_label, new_rev_label), run_time=0.4)
            
            # If this is the first augmenting path, show an explanation
            if path_count_this_phase == 1:
                self._create_overlay_text(
                    "Once an edge carries flow = 1, it's saturated\nand can't carry any more flow",
                    font_size=28,
                    color=YELLOW_A,
                    duration=3.5
                )

        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
        if self.sink_action_text_mobj.text != "":
            self._update_sink_action_text("nothing", animate=True)

        return total_flow_this_phase 

    def _create_overlay_text(self, text_content, position=None, font_size=24, color=WHITE, duration=3.0):
        """
        Creates an explanatory text that appears in the center of the screen
        to provide conceptual explanation during the visualization.
        """
        overlay_text = Text(text_content, font_size=font_size, color=color)
        
        if position is None:
            # Default position is center screen, slightly above network
            overlay_text.to_edge(UP, buff=2.5)
        else:
            overlay_text.move_to(position)
            
        overlay_text.set_z_index(100)  # Ensure it appears above everything
        
        self.play(FadeIn(overlay_text, scale=1.1), run_time=0.7)
        self.wait(duration)
        self.play(FadeOut(overlay_text), run_time=0.7)
        
    def _highlight_max_flow_cut(self):
        """Creates a visual highlight of the min-cut corresponding to the max flow"""
        # Identify nodes reachable from source in final residual graph
        # In unit capacity networks, these are nodes that aren't "saturated"
        reachable = set([self.source_node])
        q = collections.deque([self.source_node])
        
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                # Check if edge (u,v) has remaining capacity in residual graph
                if v not in reachable and ((u,v) not in self.flow or self.flow.get((u,v), 0) == 0):
                    reachable.add(v)
                    q.append(v)
        
        # Highlight source side nodes
        anims = []
        for node_id in reachable:
            if node_id in self.node_mobjects:
                dot = self.node_mobjects[node_id][0]
                anims.append(dot.animate.set_fill(BLUE_B, opacity=0.8))
        
        # Highlight sink side nodes
        sink_side = set(self.vertices_data) - reachable
        for node_id in sink_side:
            if node_id in self.node_mobjects:
                dot = self.node_mobjects[node_id][0]
                anims.append(dot.animate.set_fill(RED_B, opacity=0.8))
        
        # Find cut edges (edges from reachable to non-reachable)
        cut_edges = []
        for u in reachable:
            for v in self.adj[u]:
                if v not in reachable and (u,v) in self.edge_mobjects:
                    cut_edges.append(self.edge_mobjects[(u,v)])
        
        # Highlight cut edges
        for edge in cut_edges:
            anims.append(edge.animate.set_color(YELLOW).set_stroke(width=EDGE_STROKE_WIDTH*1.5))
        
        self.play(*anims, run_time=1.5)
        
        # Add an explanation
        self._create_overlay_text(
            "This is the min-cut corresponding to the max flow\nThe capacity of this cut equals the max flow value",
            font_size=28,
            color=YELLOW,
            duration=4.0
        )

    def construct(self):
        """
        Main method to construct and run the Dinitz algorithm visualization for unit-capacity networks.
        Sets up the graph, then iteratively builds level graphs and finds blocking flows.
        """
        self.setup_titles_and_placeholders()
        if self.sink_action_text_mobj not in self.mobjects:
            self.add(self.sink_action_text_mobj)

        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.update_section_title("1. Building the Unit-Capacity Network", play_anim=True)
        
        # Add an explanatory text about unit capacity networks
        self._create_overlay_text(
            "In unit-capacity networks, all edges have capacity = 1\nThis simplifies the algorithm and makes it more efficient", 
            font_size=28, 
            color=YELLOW,
            duration=4.0
        )

        # Initialize algorithm variables
        self.current_phase_num = 0
        self.max_flow_value = 0

        # Define graph structure for unit-capacity network (all edges have capacity 1)
        self.source_node, self.sink_node = 1, 6
        self.vertices_data = list(range(1, 7))  # Nodes 1 through 6
        
        # Define edges with unit capacity
        self.edges_list = [
            (1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 5), (4, 6), (5, 6)
        ]
        
        # In unit capacity networks, all edge capacities are 1
        self.original_edge_tuples = set(self.edges_list)
        self.capacities = {edge: 1 for edge in self.original_edge_tuples}
        self.flow = collections.defaultdict(int)  # Stores (u,v) -> flow (0 or 1)
        self.adj = collections.defaultdict(list)  # Adjacency list for graph traversal

        for u, v in self.edges_list:
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u)  # For finding all neighbors

        # Define layout for nodes
        self.graph_layout = {
            1: [-4, 0, 0],   # Source (s)
            2: [-2, 1.5, 0],
            3: [-2, -1.5, 0],
            4: [0, 1.5, 0],
            5: [0, -1.5, 0],
            6: [2, 0, 0]     # Sink (t)
        }

        # Dictionaries to store mobjects
        self.node_mobjects = {}
        self.edge_mobjects = {}
        self.base_label_visual_attrs = {}
        self.edge_label_groups = {}

        self.desired_large_scale = 1.1  # Scale factor for the main graph display

        # Create and animate node mobjects (dots and labels)
        nodes_vgroup = VGroup()
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, 
                     z_index=10, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(11)
            self.node_mobjects[v_id] = VGroup(dot, label)
            nodes_vgroup.add(self.node_mobjects[v_id])
            
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        # Create and animate edge mobjects (arrows)
        edges_vgroup = VGroup()
        edge_grow_anims = []
        
        for u, v in self.edges_list:
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

        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        # For unit capacity networks, we display "1" on each edge to indicate capacity
        unit_capacity_labels_vgroup = VGroup()
        capacity_labels_to_animate = []
        
        for u, v in self.edges_list:
            arrow = self.edge_mobjects[(u, v)]
            
            # Create a label showing "0/1" (initial flow/capacity)
            flow_capacity_label = Text("0/1", font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)
            
            flow_capacity_label.move_to(arrow.get_center())
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.15
            flow_capacity_label.shift(offset_vector).set_z_index(6)
            
            # Store the label in edge_label_groups
            self.edge_label_groups[(u, v)] = VGroup(flow_capacity_label)
            self.base_label_visual_attrs[(u, v)] = {"opacity": 1.0}
            
            unit_capacity_labels_vgroup.add(flow_capacity_label)
            capacity_labels_to_animate.append(flow_capacity_label)

        if capacity_labels_to_animate:
            self.play(LaggedStart(*[Write(c) for c in capacity_labels_to_animate], lag_ratio=0.05), run_time=1.2)
            self.wait(0.5)

        # Group all network elements and scale/position them
        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, unit_capacity_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])

        # Store base visual attributes for edges
        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(),
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }
            if edge_key not in self.base_label_visual_attrs:
                self.base_label_visual_attrs[edge_key] = {"opacity": 1.0}

        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        self.wait(0.5)

        # Position the sink_action_text_mobj
        if hasattr(self, 'node_mobjects') and self.source_node in self.node_mobjects:
            source_node_dot = self.node_mobjects[self.source_node][0]
            self.sink_action_text_mobj.next_to(source_node_dot, UP, buff=BUFF_SMALL)
        else:
            self.sink_action_text_mobj.to_corner(UL, buff=BUFF_MED)

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

        # Highlight source and sink nodes briefly
        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]
        temp_source_ring = Circle(radius=source_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, 
                                 stroke_width=RING_STROKE_WIDTH).move_to(source_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        temp_sink_ring = Circle(radius=sink_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, 
                               stroke_width=RING_STROKE_WIDTH).move_to(sink_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        self.play(
            Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7),
            Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7)
        )
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)

        # Change labels of source and sink to "s" and "t"
        source_label_original = self.node_mobjects[self.source_node][1]
        sink_label_original = self.node_mobjects[self.sink_node][1]
        new_s_label_mobj = Text("s", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, 
                               color=self.base_node_visual_attrs[self.source_node]["label_color"]
                               ).move_to(source_label_original.get_center()).set_z_index(source_label_original.z_index)
        new_t_label_mobj = Text("t", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, 
                               color=self.base_node_visual_attrs[self.sink_node]["label_color"]
                               ).move_to(sink_label_original.get_center()).set_z_index(sink_label_original.z_index)
                               
        self.play(Transform(source_label_original, new_s_label_mobj), 
                 Transform(sink_label_original, new_t_label_mobj), run_time=0.5)
        self.node_mobjects[self.source_node][1] = new_s_label_mobj
        self.node_mobjects[self.sink_node][1] = new_t_label_mobj
        self.wait(0.5)

        # --- Start Dinitz Algorithm Phases ---
        self.update_section_title("2. Running Dinitz's Algorithm on Unit-Capacity Network", play_anim=True)
        self.wait(1.0)

        while True:  # Main loop for Dinitz phases
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Step 1 - Build Level Graph (LG)", color=BLUE_B, play_anim=True)
            self._update_sink_action_text("nothing", animate=False)
            self.wait(1.0)
            self.update_status_text(f"BFS from S (Node {self.source_node}) to find shortest paths in the residual graph.", play_anim=True)
            self.wait(3.0)

            # --- Building the Level Graph ---
            self.levels = {v_id: -1 for v_id in self.vertices_data}
            q_bfs = collections.deque()
            self.levels[self.source_node] = 0
            q_bfs.append(self.source_node)

            # Clear and update level display on screen
            if self.level_display_vgroup.submobjects:
                self.play(FadeOut(self.level_display_vgroup))
                self.level_display_vgroup.remove(*self.level_display_vgroup.submobjects)
                
            l_p0 = Text(f"L0:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
            l_n0_text = f" {{s ({self.source_node})}}"
            l_n0 = Text(l_n0_text, font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
            first_level_text_group = VGroup(l_p0, l_n0).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            self.level_display_vgroup.add(first_level_text_group)
            self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
            self.play(Write(first_level_text_group))
            self.wait(1.0)
            max_level_text_width = config.frame_width * 0.30

            # Restore graph elements to base appearance before BFS highlighting
            restore_anims = []
            for v_id, node_group in self.node_mobjects.items():
                dot, lbl = node_group
                node_attrs = self.base_node_visual_attrs[v_id]
                restore_anims.append(dot.animate.set_width(node_attrs["width"])
                                   .set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"])
                                   .set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"]))
                restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))

            for edge_key, edge_mo in self.edge_mobjects.items():
                edge_attrs = self.base_edge_visual_attrs[edge_key]
                opacity = edge_attrs["opacity"]
                restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"])
                                   .set_opacity(opacity)
                                   .set_stroke(width=edge_attrs["stroke_width"]))
                
                label_grp = self.edge_label_groups.get(edge_key)
                if label_grp and label_grp.submobjects:
                    base_label_attr = self.base_label_visual_attrs.get(edge_key)
                    base_opacity_for_label = base_label_attr.get("opacity", 1.0)
                    restore_anims.append(label_grp.animate.set_opacity(base_opacity_for_label))
                    for part in label_grp.submobjects:
                        if isinstance(part, Text): restore_anims.append(part.animate.set_color(LABEL_TEXT_COLOR))
                        
            if restore_anims: self.play(AnimationGroup(*restore_anims, lag_ratio=0.01), run_time=0.75)
            self.wait(0.5)

            # Highlight source node for BFS start
            s_dot_obj, s_lbl_obj = self.node_mobjects[self.source_node]
            self.play(s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(self.base_node_visual_attrs[self.source_node]["width"] * 1.1),
                     s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE))
            self.wait(0.5)

            # BFS main loop
            while q_bfs:
                nodes_this_level = list(q_bfs)
                q_bfs.clear()
                if not nodes_this_level: break
                next_level_idx = self.levels[nodes_this_level[0]] + 1
                nodes_found_next_level_set = set()
                bfs_anims_this_step = []

                for u_bfs in nodes_this_level:
                    u_bfs_display_name = "s" if u_bfs == self.source_node else "t" if u_bfs == self.sink_node else str(u_bfs)
                    self.update_status_text(f"BFS: Exploring from L{self.levels[u_bfs]} node {u_bfs_display_name}...", play_anim=False)
                    self.wait(0.8)
                    ind_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW_C, buff=0.03, 
                                                stroke_width=2.0, corner_radius=0.05)
                    self.play(Create(ind_u), run_time=0.20)

                    sorted_neighbors_bfs = sorted(self.adj[u_bfs])
                    for v_n_bfs in sorted_neighbors_bfs:
                        edge_key_bfs = (u_bfs, v_n_bfs)
                        
                        # In unit-capacity networks, residual capacity is either 0 or 1
                        res_cap_bfs = 1 if self.flow.get(edge_key_bfs, 0) == 0 else 0
                        edge_mo_bfs = self.edge_mobjects.get(edge_key_bfs)

                        if edge_mo_bfs and res_cap_bfs > 0 and self.levels[v_n_bfs] == -1:
                            self.levels[v_n_bfs] = next_level_idx
                            nodes_found_next_level_set.add(v_n_bfs)
                            q_bfs.append(v_n_bfs)

                            lvl_color_v = LEVEL_COLORS[next_level_idx % len(LEVEL_COLORS)]
                            n_v_dot, n_v_lbl = self.node_mobjects[v_n_bfs]
                            bfs_anims_this_step.extend([
                                n_v_dot.animate.set_fill(lvl_color_v).set_width(self.base_node_visual_attrs[v_n_bfs]["width"] * 1.1),
                                n_v_lbl.animate.set_color(BLACK if sum(color_to_rgb(lvl_color_v)) > 1.5 else WHITE)
                            ])
                            edge_color_u_for_lg = LEVEL_COLORS[self.levels[u_bfs] % len(LEVEL_COLORS)]
                            bfs_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_u_for_lg)
                                                     .set_opacity(1.0)
                                                     .set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
                            
                            label_grp_bfs = self.edge_label_groups.get(edge_key_bfs)
                            if label_grp_bfs:
                                bfs_anims_this_step.append(label_grp_bfs.animate.set_opacity(1.0))
                                    
                    self.play(FadeOut(ind_u), run_time=0.20)

                if bfs_anims_this_step: 
                    self.play(AnimationGroup(*bfs_anims_this_step, lag_ratio=0.1), run_time=0.8)
                    self.wait(0.5)

                if nodes_found_next_level_set:
                    def get_node_display_name(n_id):
                        if n_id == self.source_node: return f"s ({n_id})"
                        if n_id == self.sink_node: return f"t ({n_id})"
                        return str(n_id)
                    n_str_list = [get_node_display_name(n) for n in sorted(list(nodes_found_next_level_set))]
                    n_str = ", ".join(n_str_list)
                    self.update_status_text(f"BFS: L{next_level_idx} nodes found: {{{n_str}}}", play_anim=False)
                    self.wait(0.5)
                    l_px = Text(f"L{next_level_idx}:", font_size=LEVEL_TEXT_FONT_SIZE, 
                               color=LEVEL_COLORS[next_level_idx%len(LEVEL_COLORS)])
                    l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
                    new_level_text_entry = VGroup(l_px, l_nx).arrange(RIGHT, buff=BUFF_VERY_SMALL)
                    self.level_display_vgroup.add(new_level_text_entry)
                    self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                    if self.level_display_vgroup.width > max_level_text_width:
                        self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                    self.play(Write(new_level_text_entry))
                    self.wait(1.5)
                if not q_bfs: break

            sink_display_name = "t"
            if self.levels[self.sink_node] == -1:
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) not reached by BFS. No more augmenting paths.", 
                                      color=RED_C, play_anim=True)
                self.wait(3.0)
                self.update_max_flow_display(play_anim=True)
                self.update_phase_text(f"Algorithm Complete. Max Flow: {self.max_flow_value}", color=TEAL_A, play_anim=True)
                self.update_status_text(f"Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
                self._update_sink_action_text("nothing", animate=False)
                self.wait(4.5)
                break
            else:
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) found at L{self.levels[self.sink_node]}. Level Graph established.", 
                                      color=GREEN_A, play_anim=True)
                self.wait(3.0)

                latex_status_string = r"\mbox{Isolating LG: Keep edges $(u,v)$ where $level(v)=level(u)+1$.}"
                self.update_status_text(latex_status_string, play_anim=True, is_latex=True)
                self.wait(1.0)

                lg_iso_anims = []
                for (u_lg, v_lg), edge_mo_lg in self.edge_mobjects.items():
                    # In unit-capacity networks, residual capacity is either 0 or 1
                    res_cap_lg_val = 1 if self.flow.get((u_lg, v_lg), 0) == 0 else 0
                    is_lg_edge = (self.levels.get(u_lg, -1) != -1 and self.levels.get(v_lg, -1) != -1 and
                                 self.levels[v_lg] == self.levels[u_lg] + 1 and res_cap_lg_val > 0)
                    label_grp_lg = self.edge_label_groups.get((u_lg, v_lg))

                    if is_lg_edge:
                        lg_color = LEVEL_COLORS[self.levels[u_lg] % len(LEVEL_COLORS)]
                        lg_iso_anims.append(edge_mo_lg.animate.set_color(lg_color)
                                          .set_opacity(1.0)
                                          .set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
                        if label_grp_lg and label_grp_lg.submobjects:
                            lg_iso_anims.append(label_grp_lg.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                    else:
                        base_attrs = self.base_edge_visual_attrs.get((u_lg, v_lg), {})
                        target_color = DIMMED_COLOR
                        target_opacity = DIMMED_OPACITY
                        target_width = base_attrs.get("stroke_width", EDGE_STROKE_WIDTH)
                        
                        lg_iso_anims.append(edge_mo_lg.animate.set_color(target_color)
                                          .set_opacity(target_opacity)
                                          .set_stroke(width=target_width))

                        if label_grp_lg and label_grp_lg.submobjects:
                            lg_iso_anims.append(label_grp_lg.animate.set_opacity(DIMMED_OPACITY))
                                
                if lg_iso_anims: self.play(AnimationGroup(*lg_iso_anims, lag_ratio=0.05), run_time=1.0)
                self.wait(2.0)
                self.update_status_text("Level Graph isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True)
                self.wait(2.5)

                flow_this_phase = self.animate_dfs_path_finding_phase()

                self._update_sink_action_text("nothing", animate=False)
                self.update_phase_text(f"End of Phase {self.current_phase_num}. Blocking Flow: {flow_this_phase}. Total Flow: {self.max_flow_value}", 
                                      color=TEAL_A, play_anim=True)
                self.wait(3.5)
                if self.levels.get(self.sink_node, -1) != -1:
                    self.update_status_text(f"Phase complete. Resetting for the next BFS.", color=BLUE_A, play_anim=True)
                    self.wait(3.0)

        # Algorithm conclusion
        self.update_section_title("3. Dinitz Algorithm Summary for Unit-Capacity Networks", play_anim=True)
        self.wait(1.0)
        if self.levels.get(self.sink_node, -1) == -1 and self.max_flow_value == 0:
            self.update_status_text(f"Algorithm Concluded. Sink Unreachable. Max Flow: {self.max_flow_value}", color=RED_A, play_anim=True)
        elif self.levels.get(self.sink_node, -1) == -1:
            self.update_status_text(f"Algorithm Concluded. Sink Unreachable in last BFS. Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
        else:
            self.update_status_text(f"Algorithm Concluded. Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
        self.wait(3.0)
        
        # Show the min cut corresponding to the max flow
        self._highlight_max_flow_cut()
        
        # Add a final explanation about unit capacity networks
        self._create_overlay_text(
            f"In unit-capacity networks, max flow = {self.max_flow_value} means\nthere are exactly {self.max_flow_value} edge-disjoint paths from s to t", 
            font_size=28, 
            color=BLUE_A,
            duration=5.0
        )
        
        self.wait(2.0)

        # --- Final Emphasis Flash Animation ---
        if hasattr(self, 'node_mobjects') and self.node_mobjects and \
           self.source_node in self.node_mobjects and self.sink_node in self.node_mobjects:

            source_dot = self.node_mobjects[self.source_node][0]
            sink_dot = self.node_mobjects[self.sink_node][0]

            other_node_dots = []
            for node_id in self.vertices_data:
                if node_id in self.node_mobjects:
                    if node_id != self.source_node and node_id != self.sink_node:
                        other_node_dots.append(self.node_mobjects[node_id][0])
            
            anims_for_final_emphasis = []

            # Flashes for other nodes
            anims_for_final_emphasis.extend([
                Flash(dot, color=BLUE_A, flash_radius=NODE_RADIUS * 2.0)
                for dot in other_node_dots
            ])
            
            # Flashes for source and sink nodes
            anims_for_final_emphasis.append(
                Flash(source_dot, color=GOLD_D, flash_radius=NODE_RADIUS * 3.0) 
            )
            anims_for_final_emphasis.append(
                Flash(sink_dot, color=RED_C, flash_radius=NODE_RADIUS * 3.0)
            )
            
            if anims_for_final_emphasis:
                self.play(*anims_for_final_emphasis, run_time=2.0)

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