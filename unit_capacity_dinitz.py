from manim import *
import collections
import numpy as np

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.0
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

# This will place the normal edge "above" (in the direction of the perpendicular vector)
# and the reverse edge "below".
EDGE_SHIFT_AMOUNT = 0.12

# Flow pulse animation constants
FLOW_PULSE_COLOR = BLUE_B
FLOW_PULSE_WIDTH_FACTOR = 1.8
FLOW_PULSE_TIME_WIDTH = 0.35
FLOW_PULSE_EDGE_RUNTIME = 0.5
FLOW_PULSE_Z_INDEX_OFFSET = 10
EDGE_UPDATE_RUNTIME = 0.3

# --- Action Text States ---
ACTION_STATES = {
    "nothing": {"text": "", "color": WHITE},
    "augment": {"text": "augment", "color": GREEN_B},
    "retreat": {"text": "retreat", "color": ORANGE},
    "advance": {"text": "advance", "color": YELLOW_A},
}

class UnitCapacityDinitzVisualizer(Scene):
    """
    Visualizes Dinitz's Algorithm for unit capacity networks.
    """
    
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
        """Initialize text elements and placeholders"""
        self.main_title = Text("Dinitz's Algorithm for Unit Capacity Networks", font_size=MAIN_TITLE_FONT_SIZE)
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

        self.action_text_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD, color=YELLOW).set_z_index(RING_Z_INDEX + 50)

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        """Animate text updates with fade effects"""
        old_text_had_content = False
        if isinstance(old_mobj, Text) and old_mobj.text != "": 
            old_text_had_content = True
        elif isinstance(old_mobj, Tex) and old_mobj.tex_string != "": 
            old_text_had_content = True
        elif isinstance(old_mobj, MarkupText) and old_mobj.text != "": 
            old_text_had_content = True

        new_text_has_content = bool(new_text_content_str and new_text_content_str != "")

        anims_to_play = []
        if old_text_had_content:
            anims_to_play.append(FadeOut(old_mobj, scale=0.8, run_time=0.25))

        if new_text_has_content:
            anims_to_play.append(FadeIn(new_mobj, scale=1.2, run_time=0.25))

        if anims_to_play:
            self.play(*anims_to_play)

    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False, is_markup=False):
        """Generic method to update text objects with optional animation"""
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

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        """Update the phase description text"""
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        """Update the algorithm status text"""
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex, is_markup=False)

    def update_max_flow_display(self, play_anim=True):
        """Update the max flow value display"""
        new_text_str = str(self.max_flow_value) 
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

    def _update_action_text(self, state: str, animate=True):
        """Update the action text (advance, retreat, augment)"""
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

    def _dfs_advance_and_retreat(self, u, current_path_info_list):
        """
        Recursive DFS function to find a path in the level graph, implementing the ADVANCE/RETREAT logic.
        Animates the traversal, highlighting nodes, edges, and "deleting" dead-end nodes.
        For unit capacity networks, we either can push 1 unit or 0 (no path).
        
        Args:
            u: current node
            current_path_info_list: stores path edges as ((u,v), edge_mobject)
        
        Returns:
            1 if a path to sink is found, 0 otherwise
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

        if u == self.sink_node:  # Path to sink found (successful ADVANCE to t)
            self.update_status_text(f"Path Found: Reached Sink T (Node {self.sink_node})!", color=GREEN_B, play_anim=False)
            self._update_action_text("augment")
            self.wait(2.0)
            self.play(FadeOut(highlight_ring), run_time=0.15)  # Remove highlight
            if highlight_ring in self.dfs_traversal_highlights:
                self.dfs_traversal_highlights.remove(highlight_ring)
            return 1  # Return 1 for unit capacity networks

        # Iterate through neighbors using the pointer (ptr) for optimization
        while self.ptr[u] < len(self.adj[u]):
            # Set state to "advance" before trying each edge
            self._update_action_text("advance")

            v_candidate = self.adj[u][self.ptr[u]]
            edge_key_uv = (u, v_candidate)

            # In unit capacity networks, res_cap is either 0 or 1
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

                self.update_status_text(f"Advance: Try edge ({u_display_name} -> {actual_v_display_name})", play_anim=False)
                self.wait(1.5)
                if current_anims_try:
                    self.play(*current_anims_try, run_time=0.4)
                self.wait(0.5)

                # Recursive call for the next node in the path
                tr = self._dfs_advance_and_retreat(actual_v, current_path_info_list)

                if tr > 0:  # Flow was pushed through this edge (it's part of an s-t path)
                    self.update_status_text(f"Path Segment: ({u_display_name} -> {actual_v_display_name}) is part of an augmenting path.", color=GREEN_C, play_anim=False)
                    self.wait(1.5)
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v))
                    self.play(FadeOut(highlight_ring), run_time=0.15)
                    if highlight_ring in self.dfs_traversal_highlights:
                        self.dfs_traversal_highlights.remove(highlight_ring)
                    return 1  # Return 1 for unit capacity

                # Backtracking: This edge led to a dead end
                self._update_action_text("retreat")
                self.update_status_text(f"Retreat: Edge ({u_display_name} -> {actual_v_display_name}) is a dead end. Backtracking.", color=YELLOW_C, play_anim=False)
                self.wait(1.5)
                
                current_anims_backtrack_restore = []

                # Restore edge appearance based on whether it's still a valid LG edge or should be dimmed
                # In unit capacity networks, after trying and failing, the capacity is still 1
                is_still_lg_edge_after_fail = (self.levels.get(actual_v, -1) == self.levels.get(u, -1) + 1 and 
                                              self.flow.get(edge_key_uv, 0) == 0)

                if is_still_lg_edge_after_fail:  # Restore to LG appearance
                    lg_color = LEVEL_COLORS[self.levels[u] % len(LEVEL_COLORS)]
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(lg_color).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH)
                    )
                else:  # Dim the edge as it's no longer useful in this DFS phase
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH)
                    )

                if current_anims_backtrack_restore:
                    self.play(*current_anims_backtrack_restore, run_time=0.4)
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.1, run_time=0.45))  # Indicate dead end
                self.wait(0.5)

            self.ptr[u] += 1  # Move to the next neighbor

        # All edges from u explored, this node is a dead end. Time to RETREAT from the node.
        self._update_action_text("retreat")
        self.update_status_text(f"Retreat: All edges from {u_display_name} explored. Node is a dead end.", color=ORANGE, play_anim=False)
        self.wait(2.0)

        # "Delete" a node from the LG for this phase once it's a dead end
        if u != self.source_node:  # The source node is never a dead end
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
        if highlight_ring in self.dfs_traversal_highlights:
            self.dfs_traversal_highlights.remove(highlight_ring)
        return 0  # No path found from u

    def animate_dfs_path_finding_phase(self):
        """
        Manages the DFS phase of Dinitz's algorithm: finding multiple s-t paths in the Level Graph (LG).
        For unit capacity networks, we find a blocking flow by augmenting along paths in the LG.
        """
        self.ptr = {v_id: 0 for v_id in self.vertices_data}  # Pointers for DFS optimization
        self.dead_nodes_in_phase = set()  # Tracks dead-end nodes for this phase
        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1)  # Group for DFS node highlights
        if self.dfs_traversal_highlights not in self.mobjects:
            self.add(self.dfs_traversal_highlights)

        self._update_action_text("nothing", animate=False)  # Clear any previous action text

        self.update_phase_text(f"Phase {self.current_phase_num}: Step 2 - Find Blocking Flow in LG (DFS)", color=ORANGE)
        self.update_status_text("Using DFS to find augmenting paths from S to T in the Level Graph.", play_anim=True)
        self.wait(3.0)

        while True:  # Loop to find multiple paths in the current LG
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Seeking S->T path from Node {self.source_node}.", play_anim=True)
            self.wait(1.5)
            current_path_anim_info = []  # Stores ((u,v), edge_mo) for the found path

            # Perform DFS to find one s-t path
            flow_pushed = self._dfs_advance_and_retreat(self.source_node, current_path_anim_info)

            if flow_pushed == 0:  # No more s-t paths can be found in the current LG
                self.update_status_text("No more S-T paths in LG. Blocking flow for this phase is complete.", color=YELLOW_C, play_anim=True)
                self.wait(3.5)
                break  # Exit loop for this DFS phase

            # A path was found, update total flow
            self.max_flow_value += flow_pushed
            total_flow_this_phase += flow_pushed

            current_path_anim_info.reverse()  # Path is built from T to S, reverse for S to T animation

            self.update_status_text(f"Path #{path_count_this_phase} found. Augmenting flow...", color=GREEN_A, play_anim=True)
            self._update_action_text("augment")
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

            # Animate flow augmentation along the path
            path_augmentation_sequence = []

            for (u, v), edge_mo in current_path_anim_info:
                animations_for_current_edge_step = []

                # Flow Pulse Animation
                flash_edge_copy = edge_mo.copy()
                flash_edge_copy.set_color(FLOW_PULSE_COLOR).set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR).set_opacity(1.0)
                flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)

                pulse_animation = ShowPassingFlash(
                    flash_edge_copy, time_width=FLOW_PULSE_TIME_WIDTH, run_time=FLOW_PULSE_EDGE_RUNTIME
                )
                animations_for_current_edge_step.append(pulse_animation)

                # Update flow values and edge appearances
                visual_updates_this_edge = []
                
                # Update flow along the edge
                self.flow[(u, v)] = 1  # For unit capacity networks, flow is either 0 or 1
                
                # Edge is now saturated - dim it
                visual_updates_this_edge.append(
                    edge_mo.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH)
                )
                
                # Create reverse edge if it doesn't exist
                if (v, u) not in self.edge_mobjects and (v, u) not in self.original_edge_tuples:
                    n_u_dot, n_v_dot = self.node_mobjects[u][0], self.node_mobjects[v][0]
                    u_center, v_center = n_u_dot.get_center(), n_v_dot.get_center()

                    perp_vector = rotate_vector(normalize(v_center - u_center), PI / 2)
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
                    
                    # Make the reverse edge visible
                    visual_updates_this_edge.append(rev_arrow.animate.set_opacity(REVERSE_EDGE_OPACITY))
                    
                    # Update adjacency list if needed
                    if u not in self.adj[v]:
                        self.adj[v].append(u)
                        
                # Show the reverse edge with full capacity (1)
                if (v, u) in self.edge_mobjects:
                    rev_edge_mo_vu = self.edge_mobjects[(v, u)]
                    # Reverse edge now has capacity 1
                    visual_updates_this_edge.append(
                        rev_edge_mo_vu.animate.set_color(REVERSE_EDGE_COLOR).set_opacity(REVERSE_EDGE_OPACITY)
                    )

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
            
            self.update_max_flow_display(play_anim=True)
            self.wait(0.5)
            self._update_action_text("nothing", animate=True)
            self.update_status_text(f"Flow augmented. Current phase flow: {total_flow_this_phase}. Searching for next path...", color=WHITE, play_anim=True)
            self.wait(2.5)

        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
        if self.action_text_mobj.text != "":
            self._update_action_text("nothing", animate=True)

        return total_flow_this_phase 

    def build_level_graph(self):
        """Build level graph using BFS from source node"""
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
            restore_anims.append(dot.animate.set_width(node_attrs["width"]).set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"]).set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"]))
            restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))

        for edge_key, edge_mo in self.edge_mobjects.items():
            edge_attrs = self.base_edge_visual_attrs[edge_key]
            opacity = edge_attrs["opacity"]
            restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"]).set_opacity(opacity).set_stroke(width=edge_attrs["stroke_width"]))
            
        if restore_anims:
            self.play(AnimationGroup(*restore_anims, lag_ratio=0.01), run_time=0.75)
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
            if not nodes_this_level:
                break
                
            next_level_idx = self.levels[nodes_this_level[0]] + 1
            nodes_found_next_level_set = set()
            bfs_anims_this_step = []

            for u_bfs in nodes_this_level:
                u_bfs_display_name = "s" if u_bfs == self.source_node else "t" if u_bfs == self.sink_node else str(u_bfs)
                self.update_status_text(f"BFS: Exploring from L{self.levels[u_bfs]} node {u_bfs_display_name}...", play_anim=False)
                self.wait(0.8)
                ind_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW_C, buff=0.03, stroke_width=2.0, corner_radius=0.05)
                self.play(Create(ind_u), run_time=0.20)

                sorted_neighbors_bfs = sorted(self.adj[u_bfs])
                for v_n_bfs in sorted_neighbors_bfs:
                    edge_key_bfs = (u_bfs, v_n_bfs)
                    # For unit capacity networks, check if flow is 0 (residual capacity is 1)
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
                        bfs_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_u_for_lg).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))

                self.play(FadeOut(ind_u), run_time=0.20)

            if bfs_anims_this_step:
                self.play(AnimationGroup(*bfs_anims_this_step, lag_ratio=0.1), run_time=0.8)
                self.wait(0.5)

            if nodes_found_next_level_set:
                def get_node_display_name(n_id):
                    if n_id == self.source_node:
                        return f"s ({n_id})"
                    if n_id == self.sink_node:
                        return f"t ({n_id})"
                    return str(n_id)
                    
                n_str_list = [get_node_display_name(n) for n in sorted(list(nodes_found_next_level_set))]
                n_str = ", ".join(n_str_list)
                self.update_status_text(f"BFS: L{next_level_idx} nodes found: {{{n_str}}}", play_anim=False)
                self.wait(0.5)
                l_px = Text(f"L{next_level_idx}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[next_level_idx % len(LEVEL_COLORS)])
                l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
                new_level_text_entry = VGroup(l_px, l_nx).arrange(RIGHT, buff=BUFF_VERY_SMALL)
                self.level_display_vgroup.add(new_level_text_entry)
                self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                if self.level_display_vgroup.width > max_level_text_width:
                    self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                self.play(Write(new_level_text_entry))
                self.wait(1.5)
                
            if not q_bfs:
                break

        # After BFS, isolate the Level Graph by highlighting only edges where level(v)=level(u)+1
        self.update_status_text(r"\mbox{Isolating LG: Keep edges $(u,v)$ where $level(v)=level(u)+1$.}", play_anim=True, is_latex=True)
        self.wait(1.0)

        lg_iso_anims = []
        for (u_lg, v_lg), edge_mo_lg in self.edge_mobjects.items():
            # For unit capacity networks, check if edge has flow=0 (available capacity)
            res_cap_lg_val = 1 if self.flow.get((u_lg, v_lg), 0) == 0 else 0
            is_lg_edge = (self.levels.get(u_lg, -1) != -1 and 
                          self.levels.get(v_lg, -1) != -1 and
                          self.levels[v_lg] == self.levels[u_lg] + 1 and 
                          res_cap_lg_val > 0)

            if is_lg_edge:
                lg_color = LEVEL_COLORS[self.levels[u_lg] % len(LEVEL_COLORS)]
                lg_iso_anims.append(edge_mo_lg.animate.set_color(lg_color).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
            else:
                base_attrs = self.base_edge_visual_attrs.get((u_lg, v_lg), {})
                target_color = DIMMED_COLOR
                target_opacity = DIMMED_OPACITY
                target_width = base_attrs.get("stroke_width", EDGE_STROKE_WIDTH)
                lg_iso_anims.append(edge_mo_lg.animate.set_color(target_color).set_opacity(target_opacity).set_stroke(width=target_width))

        if lg_iso_anims:
            self.play(AnimationGroup(*lg_iso_anims, lag_ratio=0.05), run_time=1.0)
        self.wait(2.0)
        
        return self.levels[self.sink_node] != -1

    def construct(self):
        """Main method to run the Dinitz algorithm visualization for unit capacity networks"""
        self.setup_titles_and_placeholders()
        if self.action_text_mobj not in self.mobjects:
            self.add(self.action_text_mobj)

        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.update_section_title("1. Building the Network", play_anim=True)

        # Initialize algorithm variables
        self.current_phase_num = 0
        self.max_flow_value = 0

        # Define graph structure for a unit capacity network
        # Example of a bipartite matching problem
        self.source_node, self.sink_node = 0, 7
        self.vertices_data = list(range(8))  # Nodes 0-7
        self.edges_with_capacity_list = [
            (0, 1, 1), (0, 2, 1), (0, 3, 1),  # Source to left side
            (1, 4, 1), (1, 5, 1),            # Connections between sides
            (2, 4, 1), (2, 6, 1),
            (3, 5, 1), (3, 6, 1),
            (4, 7, 1), (5, 7, 1), (6, 7, 1)   # Right side to sink
        ]
        self.original_edge_tuples = set([(u, v) for u, v, c in self.edges_with_capacity_list])

        self.capacities = collections.defaultdict(int)  # Stores (u,v) -> capacity (always 1)
        self.flow = collections.defaultdict(int)       # Stores (u,v) -> flow (0 or 1)
        self.adj = collections.defaultdict(list)       # Adjacency list for graph traversal

        for u, v, cap in self.edges_with_capacity_list:
            self.capacities[(u, v)] = cap
            if v not in self.adj[u]:
                self.adj[u].append(v)
            if u not in self.adj[v]:
                self.adj[v].append(u)  # For finding all neighbors

        # Define layout for nodes in a bipartite arrangement
        self.graph_layout = {
            0: [-4, 0, 0],         # Source
            1: [-2, 1, 0],         # Left side
            2: [-2, 0, 0],
            3: [-2, -1, 0],
            4: [1, 1, 0],          # Right side
            5: [1, 0, 0],
            6: [1, -1, 0],
            7: [3, 0, 0]           # Sink
        }

        # Create data structures for mobjects
        self.node_mobjects = {}
        self.edge_mobjects = {}
        self.base_edge_visual_attrs = {}
        self.base_node_visual_attrs = {}
        self.network_display_group = VGroup()

        # Create nodes (dots and labels)
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
            
            # Use "s" for source, "t" for sink, or node number
            if v_id == self.source_node:
                label_text = "s"
            elif v_id == self.sink_node:
                label_text = "t"
            else:
                label_text = str(v_id)
                
            label = Text(
                label_text,
                font_size=NODE_LABEL_FONT_SIZE,
                weight=BOLD
            ).move_to(dot.get_center()).set_z_index(11)
            
            self.node_mobjects[v_id] = VGroup(dot, label)
            nodes_vgroup.add(self.node_mobjects[v_id])
            
            # Store original visual attributes
            self.base_node_visual_attrs[v_id] = {
                "width": dot.width,
                "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(),
                "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity(),
                "label_color": label.get_color()
            }
            
        self.play(
            LaggedStart(
                *[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data],
                lag_ratio=0.05
            ),
            run_time=1.5
        )
        self.wait(0.5)

        # Create edges (arrows)
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
            
            # Store original visual attributes
            self.base_edge_visual_attrs[(u, v)] = {
                "color": arrow.get_color(),
                "stroke_width": arrow.get_stroke_width(),
                "opacity": arrow.get_stroke_opacity()
            }
            
        self.play(
            LaggedStart(*edge_grow_anims, lag_ratio=0.05),
            run_time=1.5
        )
        self.wait(0.5)

        # Add labels for unit capacity (just "1" on each edge)
        all_edge_labels_vgroup = VGroup()
        capacity_labels_to_animate = []
        
        for u, v, _ in self.edges_with_capacity_list:
            edge = self.edge_mobjects[(u, v)]
            capacity_label = Text("1", font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)
            capacity_label.move_to(edge.get_center())
            
            # Offset label from edge
            offset_vector = rotate_vector(edge.get_unit_vector(), PI/2) * 0.15
            capacity_label.shift(offset_vector).set_z_index(6)
            
            all_edge_labels_vgroup.add(capacity_label)
            capacity_labels_to_animate.append(capacity_label)
            
        if capacity_labels_to_animate:
            self.play(
                LaggedStart(*[Write(c) for c in capacity_labels_to_animate], lag_ratio=0.05),
                run_time=1.2
            )
            self.wait(0.5)

        # Group all network elements
        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        
        # Scale and position the network
        target_scale = 1.4
        temp_scaled_network = self.network_display_group.copy().scale(target_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        
        self.play(
            self.network_display_group.animate.scale(target_scale).move_to(target_position)
        )
        self.wait(0.5)

        # Position the action text above the source node
        source_dot = self.node_mobjects[self.source_node][0]
        self.action_text_mobj.next_to(source_dot, UP, buff=BUFF_LARGE)

        # Highlight source and sink
        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]
        
        temp_source_ring = Circle(
            radius=source_node_dot.width / 2 + RING_RADIUS_OFFSET,
            color=RING_COLOR,
            stroke_width=RING_STROKE_WIDTH
        ).move_to(source_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        temp_sink_ring = Circle(
            radius=sink_node_dot.width / 2 + RING_RADIUS_OFFSET,
            color=RING_COLOR,
            stroke_width=RING_STROKE_WIDTH
        ).move_to(sink_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        self.play(
            Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, run_time=0.7),
            Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, run_time=0.7)
        )
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)
        self.wait(1.0)

        # Start Dinitz Algorithm Phases
        self.update_section_title("2. Running Dinitz's Algorithm", play_anim=True)
        self.wait(1.0)
        
        # Main algorithm loop
        while True:
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Step 1 - Build Level Graph (BFS)", color=BLUE_B, play_anim=True)
            self._update_action_text("nothing", animate=False)
            self.wait(1.0)
            
            self.update_status_text(f"BFS from source (s) to find shortest paths in the residual graph.", play_anim=True)
            self.wait(2.0)
            
            # Build level graph using BFS
            sink_reachable = self.build_level_graph()
            
            if not sink_reachable:
                self.update_status_text("Sink not reachable by BFS. No more augmenting paths exist.", color=RED_C, play_anim=True)
                self.wait(2.0)
                self.update_max_flow_display(play_anim=True)
                self.update_phase_text(f"Algorithm Complete. Max Flow: {self.max_flow_value}", color=TEAL_A, play_anim=True)
                self.update_status_text(f"Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
                self.wait(3.0)
                break
            
            self.update_status_text("Level Graph established. Ready for path finding phase.", color=GREEN_A, play_anim=True)
            self.wait(2.0)
            
            # Find blocking flow using DFS
            flow_this_phase = self.animate_dfs_path_finding_phase()
            
            self._update_action_text("nothing", animate=False)
            self.update_phase_text(f"End of Phase {self.current_phase_num}. Blocking Flow: {flow_this_phase}. Total Flow: {self.max_flow_value}", color=TEAL_A, play_anim=True)
            self.wait(3.0)
        
        # Final summary
        self.update_section_title("3. Dinitz Algorithm Summary", play_anim=True)
        self.wait(1.0)
        
        self.update_status_text(f"Algorithm complete. Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
        self.wait(2.0)
        
        # Final flash animation on source and sink
        source_dot = self.node_mobjects[self.source_node][0]
        sink_dot = self.node_mobjects[self.sink_node][0]
        
        other_nodes = []
        for node_id in self.vertices_data:
            if node_id not in [self.source_node, self.sink_node]:
                other_nodes.append(self.node_mobjects[node_id][0])
        
        final_anims = []
        
        # Flash other nodes
        final_anims.extend([
            Flash(dot, color=BLUE_A, flash_radius=NODE_RADIUS * 2.0)
            for dot in other_nodes
        ])
        
        # Flash source and sink with different colors
        final_anims.append(Flash(source_dot, color=GOLD_D, flash_radius=NODE_RADIUS * 3.0))
        final_anims.append(Flash(sink_dot, color=RED_C, flash_radius=NODE_RADIUS * 3.0))
        
        if final_anims:
            self.play(*final_anims, run_time=2.0)
        
        self.wait(3.0) 