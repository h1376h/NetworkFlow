from manim import *
import collections
import numpy as np

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.16
REVERSE_ARROW_TIP_LENGTH = 0.12 # New constant for smaller reverse arrowheads

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 # For text below main title
PHASE_TEXT_FONT_SIZE = 22      # For text below section title
STATUS_TEXT_FONT_SIZE = 20      # For text below phase title
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12 # Used for original edges
EDGE_FLOW_PREFIX_FONT_SIZE = 12    # Used for original edges & pure reverse residual
LEVEL_TEXT_FONT_SIZE = 18
MAX_FLOW_DISPLAY_FONT_SIZE = 20 # For the new current flow display

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
DFS_PATH_EDGE_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.25 # Used for highlighting path in green
BOTTLENECK_EDGE_INDICATE_COLOR = RED_D

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

REVERSE_EDGE_COLOR = GREY_B
REVERSE_EDGE_OPACITY = 0.25
REVERSE_EDGE_STROKE_WIDTH_FACTOR = 0.6
REVERSE_EDGE_Z_INDEX = 4

# This will place the normal edge "above" (in the direction of the perpendicular vector)
# and the reverse edge "below".
EDGE_SHIFT_AMOUNT = 0.12 # Single value for shifting, used as + and -

# Flow pulse animation constants
FLOW_PULSE_COLOR = BLUE_B
FLOW_PULSE_WIDTH_FACTOR = 1.8
FLOW_PULSE_TIME_WIDTH = 0.35  # Proportion of edge length lit up by flash
FLOW_PULSE_EDGE_RUNTIME = 0.5 # Time for pulse to traverse one edge
FLOW_PULSE_Z_INDEX_OFFSET = 10
EDGE_UPDATE_RUNTIME = 0.3         # Time for text/visual updates after pulse on an edge

# --- Sink Action Text States ---
SINK_ACTION_STATES = {
    "nothing": {"text": "", "color": WHITE},
    "augment": {"text": "augment", "color": GREEN_B},
    "retreat": {"text": "retreat", "color": ORANGE},
    "advance": {"text": "advance", "color": YELLOW_A},
}

class DinitzAlgorithmVisualizer(Scene):

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
            return VGroup() # Return an empty mobject if nodes are at the same position

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
        # Initializes main title, section title, phase text, status text, and max flow display mobjects.
        # Sets up their initial properties and positions.
        self.main_title = Text("Visualizing Dinitz's Algorithm for Max Flow", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.max_flow_display_mobj = Text("", font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj,
            self.max_flow_display_mobj
        ).arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        self.add(self.info_texts_group)

        self.level_display_vgroup = VGroup().set_z_index(10).to_corner(UR, buff=BUFF_LARGE)
        self.add(self.level_display_vgroup)

        self.sink_action_text_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD, color=YELLOW).set_z_index(RING_Z_INDEX + 50)

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        # Helper function to animate transitions between old and new text mobjects.
        # Fades out old text and fades in new text.
        old_text_had_actual_content = (isinstance(old_mobj, Text) and old_mobj.text != "") or \
                                      (isinstance(old_mobj, Tex) and old_mobj.tex_string != "")

        new_text_has_actual_content = bool(new_text_content_str and new_text_content_str != "")

        anims_to_play = []
        if old_text_had_actual_content:
            anims_to_play.append(FadeOut(old_mobj, scale=0.8, run_time=0.25))

        if new_text_has_actual_content:
            anims_to_play.append(FadeIn(new_mobj, scale=1.2, run_time=0.25))

        if anims_to_play:
            self.play(*anims_to_play)


    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False):
        # Generic function to update a text mobject (Text or Tex).
        # Handles creation of new mobject, replacement in scene and groups, and animation.
        old_mobj = getattr(self, text_attr_name)

        if is_latex:
            new_mobj = Tex(new_text_content, color=color)
            ref_text_for_height = Text("Mg", font_size=font_size) # Reference for scaling LaTeX
            if ref_text_for_height.height > 0.001 and new_mobj.height > 0.001:
                new_mobj.scale_to_fit_height(ref_text_for_height.height)
        else:
            new_mobj = Text(new_text_content, font_size=font_size, weight=weight, color=color)

        # Handle replacement if the mobject is part of the info_texts_group
        current_idx = -1
        if old_mobj in self.info_texts_group.submobjects:
            current_idx = self.info_texts_group.submobjects.index(old_mobj)
            new_mobj.move_to(old_mobj.get_center())
            self.info_texts_group.remove(old_mobj)

        if old_mobj in self.mobjects :
            self.remove(old_mobj)

        if current_idx != -1 :
            self.info_texts_group.insert(current_idx, new_mobj)

        setattr(self, text_attr_name, new_mobj)
        # Re-arrange the info_texts_group to maintain layout
        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') and old_mobj.z_index is not None else 10)

        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_content)
        else: # If not animating, just add if it's new content and not already present
            is_empty_new_content = (isinstance(new_mobj, Text) and new_mobj.text == "") or \
                                   (isinstance(new_mobj, Tex) and new_mobj.tex_string == "")
            is_in_group = new_mobj in self.info_texts_group.submobjects

            if not is_empty_new_content:
                if not is_in_group and new_mobj not in self.mobjects:
                    self.add(new_mobj)

    def update_section_title(self, text_str, play_anim=True):
        # Updates the current_section_title_mobj.
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        # Updates the phase_text_mobj.
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        # Updates the algo_status_mobj. Can handle plain text or LaTeX.
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex)

    def update_max_flow_display(self, play_anim=True):
        # Updates the max_flow_display_mobj with the current max flow value.
        new_text_str = f"Sink's value of flow: {self.max_flow_value:.1f}"
        self._update_text_generic("max_flow_display_mobj", new_text_str, MAX_FLOW_DISPLAY_FONT_SIZE, BOLD, GREEN_C, play_anim)

    def _update_sink_action_text(self, state: str, animate=True):
        """
        Updates the sink action text based on the desired state (nothing, advance, retreat, augment).
        Manages the text content, color, position, and animation using a state dictionary.
        """
        state_info = SINK_ACTION_STATES.get(state)
        if not state_info:
            print(f"Warning: Invalid sink action state '{state}' provided.")
            return

        new_text_str = state_info["text"]
        new_color = state_info["color"]

        current_mobj = self.sink_action_text_mobj
        old_text_str = current_mobj.text

        # Exit if there's no change to be made
        if old_text_str == new_text_str and current_mobj.get_color() == new_color:
            return

        # Create the target mobject based on the new state
        target_mobj = Text(
            new_text_str,
            font_size=STATUS_TEXT_FONT_SIZE,
            weight=BOLD,
            color=new_color
        )
        target_mobj.set_z_index(current_mobj.z_index)

        # Position the new mobject above the source node
        if hasattr(self, 'source_node') and self.source_node in self.node_mobjects:
            source_dot = self.node_mobjects[self.source_node][0]
            target_mobj.next_to(source_dot, UP, buff=BUFF_MED)
        else:
            # Fallback position if source node isn't available
            target_mobj.move_to(current_mobj.get_center())

        # Animate the transition
        if animate:
            # Transition: from text to empty string
            if old_text_str and not new_text_str:
                self.play(FadeOut(current_mobj, run_time=0.3))
            # Transition: from empty string to new text
            elif not old_text_str and new_text_str:
                self.remove(current_mobj) # Remove the old empty placeholder
                self.add(target_mobj)      # Add the new mobject
                self.play(FadeIn(target_mobj, run_time=0.3))
            # Transition: from one text to another
            else: # old_text_str and new_text_str
                self.play(ReplacementTransform(current_mobj, target_mobj))

        # If not animating, just perform the replacement
        else:
            self.remove(current_mobj)
            if new_text_str: # Only add the new mobject if it has content
                self.add(target_mobj)

        # Update the reference to the current action text mobject
        self.sink_action_text_mobj = target_mobj

    def _dfs_advance_and_retreat(self, u, pushed, current_path_info_list):
        # Recursive DFS function to find a path in the level graph, matching ADVANCE/RETREAT logic.
        # Animates the traversal, highlighting nodes, edges, and "deleting" dead-end nodes.
        # u: current node, pushed: flow pushed so far, current_path_info_list: stores path edges.

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
            return pushed # Return the bottleneck capacity found so far

        # Iterate through neighbors using the pointer (ptr) for Dinic's optimization
        while self.ptr[u] < len(self.adj[u]):
            # Set state to "advance" before trying each edge
            self._update_sink_action_text("advance")

            v_candidate = self.adj[u][self.ptr[u]]
            edge_key_uv = (u, v_candidate)

            res_cap_cand = self.capacities.get(edge_key_uv, 0) - self.flow.get(edge_key_uv, 0)
            edge_mo_cand = self.edge_mobjects.get(edge_key_uv)

            # Check if this edge is a valid Level Graph edge (and destination is not a dead end)
            is_valid_lg_edge = (edge_mo_cand and
                                self.levels.get(v_candidate, -1) == self.levels.get(u, -1) + 1 and
                                res_cap_cand > 0 and
                                v_candidate not in self.dead_nodes_in_phase) # IMPROVEMENT: Check against dead nodes

            if is_valid_lg_edge:
                actual_v = v_candidate
                edge_mo_for_v = edge_mo_cand
                actual_v_display_name = "s" if actual_v == self.source_node else "t" if actual_v == self.sink_node else str(actual_v)

                # Animate trying this edge
                current_anims_try = [
                    edge_mo_for_v.animate.set_color(YELLOW_A).set_opacity(1.0).set_stroke(width=DFS_EDGE_TRY_WIDTH)
                ]
                # If it's a non-original (residual) edge, also animate its capacity label
                if edge_key_uv not in self.original_edge_tuples:
                    label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                    if label_mobj:
                        target_label = Text(f"{res_cap_cand:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=YELLOW_A)
                        target_label.move_to(label_mobj.get_center()).set_opacity(1.0)
                        if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label.height = self.scaled_flow_text_height * 0.9
                        current_anims_try.append(label_mobj.animate.become(target_label))

                self.update_status_text(f"Advance: Try edge ({u_display_name} -> {actual_v_display_name}), Res.Cap: {res_cap_cand:.0f}.", play_anim=False)
                self.wait(1.5)
                if current_anims_try: self.play(*current_anims_try, run_time=0.4)
                self.wait(0.5)

                # Recursive call for the next node in the path
                tr = self._dfs_advance_and_retreat(actual_v, min(pushed, res_cap_cand), current_path_info_list)

                if tr > 0: # Flow was pushed through this edge (it's part of an s-t path)
                    self.update_status_text(f"Path Segment: ({u_display_name} -> {actual_v_display_name}) is part of an augmenting path.", color=GREEN_C, play_anim=False)
                    self.wait(1.5)
                    # We don't need to store original colors anymore as we restore based on state
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v))
                    self.play(FadeOut(highlight_ring), run_time=0.15)
                    if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr # Return flow pushed

                # Backtracking: This edge led to a dead end
                self._update_sink_action_text("retreat")
                self.update_status_text(f"Retreat: Edge ({u_display_name} -> {actual_v_display_name}) is a dead end. Backtracking.", color=YELLOW_C, play_anim=False)
                self.wait(1.5)
                
                current_anims_backtrack_restore = []

                # Restore edge appearance based on whether it's still a valid LG edge or should be dimmed
                current_res_cap_after_fail = self.capacities.get(edge_key_uv, 0) - self.flow.get(edge_key_uv, 0)
                is_still_lg_edge_after_fail = (self.levels.get(actual_v, -1) == self.levels.get(u, -1) + 1 and current_res_cap_after_fail > 0)

                if is_still_lg_edge_after_fail: # Restore to LG appearance
                    lg_color = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(lg_color).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH)
                    )
                    if edge_key_uv not in self.original_edge_tuples: # Restore residual capacity label
                        label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                        if label_mobj:
                            target_label_revert = Text(f"{current_res_cap_after_fail:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=lg_color)
                            target_label_revert.move_to(label_mobj.get_center()).set_opacity(1.0)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_revert.height = self.scaled_flow_text_height * 0.9
                            current_anims_backtrack_restore.append(label_mobj.animate.become(target_label_revert))
                else: # Dim the edge as it's no longer useful in this DFS phase
                    # FIX: Use set_color and set_opacity to dim the entire edge including arrowhead
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH)
                    )
                    if edge_key_uv not in self.original_edge_tuples: # Hide residual capacity label
                        label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                        if label_mobj: current_anims_backtrack_restore.append(label_mobj.animate.set_opacity(0.0))

                if current_anims_backtrack_restore: self.play(*current_anims_backtrack_restore, run_time=0.4)
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.1, run_time=0.45)) # Indicate dead end
                self.wait(0.5)

            self.ptr[u] += 1 # Move to the next neighbor (Dinic's optimization)

        # All edges from u explored, this node is a dead end. Time to RETREAT from the node.
        self._update_sink_action_text("retreat")
        self.update_status_text(f"Retreat: All edges from {u_display_name} explored. Node is a dead end.", color=ORANGE, play_anim=False)
        self.wait(2.0)

        # --- DINIC'S LOGIC: "Delete" a node from the LG for this phase once it's a dead end. ---
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
        return 0 # No path found from u

    def animate_dfs_path_finding_phase(self):
        # Manages the DFS phase of Dinitz's algorithm: finding multiple s-t paths in the Level Graph (LG)
        # to form a blocking flow. Animates path discovery, bottleneck calculation, and flow augmentation.

        self.ptr = {v_id: 0 for v_id in self.vertices_data} # Pointers for Dinic's DFS optimization
        self.dead_nodes_in_phase = set() # Tracks dead-end nodes for this phase. This is reset for each new phase.
        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1) # Group for DFS node highlights
        if self.dfs_traversal_highlights not in self.mobjects: self.add(self.dfs_traversal_highlights)

        self._update_sink_action_text("nothing", animate=False) # Clear any previous action text

        self.update_phase_text(f"Phase {self.current_phase_num}: Step 2 - Find Blocking Flow in LG (DFS)", color=ORANGE)
        self.update_status_text("Using DFS to find augmenting paths from S to T in the Level Graph.", play_anim=True)
        self.wait(3.0)

        while True: # Loop to find multiple paths in the current LG
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Seeking S->T path from Node {self.source_node}.", play_anim=True)
            self.wait(1.5)
            current_path_anim_info = [] # Stores ((u,v), edge_mo) for the found path

            # Perform DFS to find one s-t path and its bottleneck capacity
            bottleneck_flow = self._dfs_advance_and_retreat(self.source_node, float('inf'), current_path_anim_info)

            if bottleneck_flow == 0: # No more s-t paths can be found in the current LG
                self.update_status_text("No more S-T paths in LG. Blocking flow for this phase is complete.", color=YELLOW_C, play_anim=True)
                self.wait(3.5)
                break # Exit loop for this DFS phase

            # A path was found, update total flow
            self.max_flow_value += bottleneck_flow
            total_flow_this_phase += bottleneck_flow

            current_path_anim_info.reverse() # Path is built from T to S, reverse for S to T animation

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

                    res_cap_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR, opacity=0.0)
                    res_cap_mobj.move_to(dashed_line_rev.get_center()).rotate(base_arrow_rev[0].get_angle())
                    offset_vec_lbl = rotate_vector(base_arrow_rev[0].get_unit_vector(), PI / 2) * 0.15
                    res_cap_mobj.shift(offset_vec_lbl).set_z_index(6)
                    
                    self.edge_residual_capacity_mobjects[(v,u)] = res_cap_mobj
                    self.edge_label_groups[(v,u)] = VGroup(res_cap_mobj)
                    self.base_label_visual_attrs[(v,u)] = {"opacity": 0.0}
                    
                    self.network_display_group.add(rev_arrow, res_cap_mobj)
                    self.add(rev_arrow, res_cap_mobj)

                    forward_edge_mo = self.edge_mobjects[(u, v)]
                    forward_label = self.edge_label_groups.get((u, v))

                    anim_fwd_edge = forward_edge_mo.animate.shift(fwd_shift_vector)
                    anim_fwd_label = forward_label.animate.shift(fwd_shift_vector) if forward_label else AnimationGroup()
                    anim_rev_edge = rev_arrow.animate.set_opacity(REVERSE_EDGE_OPACITY)

                    pre_augment_animations.append(AnimationGroup(anim_fwd_edge, anim_fwd_label, anim_rev_edge))

            if pre_augment_animations:
                self.play(AnimationGroup(*pre_augment_animations, lag_ratio=0.1, run_time=0.6))
                self.wait(0.2)

            # Identify bottleneck edges for visual indication
            bottleneck_edges_for_indication = []
            for (u_path, v_path), edge_mo_path in current_path_anim_info:
                edge_key = (u_path, v_path)
                res_cap_before_aug = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                if abs(res_cap_before_aug - bottleneck_flow) < 0.01: # Check if this edge is a bottleneck
                    bottleneck_edges_for_indication.append(edge_mo_path)

            if bottleneck_edges_for_indication:
                self.update_status_text(f"Path #{path_count_this_phase} found. Bottleneck: {bottleneck_flow:.1f}. Identifying bottleneck edges...", color=YELLOW_A, play_anim=True)
                self.wait(1.0)
                flash_anims = [
                    Indicate(edge_mo, color=BOTTLENECK_EDGE_INDICATE_COLOR, scale_factor=1.05, rate_func=there_and_back_with_pause, run_time=1.2)
                    for edge_mo in bottleneck_edges_for_indication
                ]
                if flash_anims:
                    self.play(AnimationGroup(*flash_anims, lag_ratio=0.05))
                    self.wait(0.75)

            self.update_status_text(f"Path #{path_count_this_phase} found. Bottleneck: {bottleneck_flow:.1f}. Augmenting flow...", color=GREEN_A, play_anim=True)
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

            # --- COMBINED FLOW PULSE AND NUMBER/VISUAL UPDATE ANIMATION ---
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

                # 2. Prepare animations for number/visual updates
                text_updates_this_edge = []
                visual_updates_this_edge = []

                self.flow[(u,v)] += bottleneck_flow
                self.flow[(v,u)] -= bottleneck_flow

                if (u,v) in self.original_edge_tuples:
                    old_flow_text_mobj = self.edge_flow_val_text_mobjects[(u,v)]
                    new_flow_val_uv = self.flow[(u,v)]
                    new_flow_str_uv = f"{new_flow_val_uv:.0f}"
                    target_text_template_uv = Text(new_flow_str_uv, font=old_flow_text_mobj.font, font_size=old_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                        target_text_template_uv.height = self.scaled_flow_text_height
                    target_text_template_uv.move_to(old_flow_text_mobj.get_center()).rotate(edge_mo.get_angle(), about_point=target_text_template_uv.get_center())
                    text_updates_this_edge.append(old_flow_text_mobj.animate.become(target_text_template_uv))

                res_cap_after_uv = self.capacities.get((u,v),0) - self.flow.get((u,v),0)
                is_still_lg_edge_uv = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                                       self.levels[v]==self.levels[u]+1 and res_cap_after_uv > 0 and v not in self.dead_nodes_in_phase )
                
                if not is_still_lg_edge_uv: # Edge is saturated or no longer LG
                    # FIX: Use set_color and set_opacity to dim the arrowhead as well
                    visual_updates_this_edge.append(edge_mo.animate.set_color(DIMMED_COLOR).set_opacity(DIMMED_OPACITY).set_stroke(width=EDGE_STROKE_WIDTH))
                    if (u,v) not in self.original_edge_tuples:
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv: visual_updates_this_edge.append(label_mobj_uv.animate.set_opacity(0.0))
                else: # Edge still in LG, update to its LG color
                    # FIX: Use set_opacity(1.0) to ensure the arrowhead is also opaque
                    lg_color_uv = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                    visual_updates_this_edge.append(edge_mo.animate.set_color(lg_color_uv).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
                    if (u,v) not in self.original_edge_tuples:
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv:
                            target_label_uv = Text(f"{res_cap_after_uv:.0f}", font=label_mobj_uv.font, font_size=label_mobj_uv.font_size, color=lg_color_uv)
                            target_label_uv.move_to(label_mobj_uv.get_center()).set_opacity(1.0)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_uv.height = self.scaled_flow_text_height * 0.9
                            text_updates_this_edge.append(label_mobj_uv.animate.become(target_label_uv))

                if (v,u) in self.edge_mobjects:
                    rev_edge_mo_vu = self.edge_mobjects[(v,u)]
                    res_cap_vu = self.capacities.get((v,u),0) - self.flow.get((v,u),0)

                    if res_cap_vu > 0:
                        base_attrs = self.base_edge_visual_attrs.get((v, u), {})
                        color = GREY_A if (v, u) in self.original_edge_tuples else base_attrs.get("color", REVERSE_EDGE_COLOR)
                        opacity = 0.7 if (v, u) in self.original_edge_tuples else base_attrs.get("opacity", REVERSE_EDGE_OPACITY)
                        width = EDGE_STROKE_WIDTH if (v,u) in self.original_edge_tuples else base_attrs.get("stroke_width", EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR)
                        # FIX: Use set_color and set_opacity for reverse edge
                        visual_updates_this_edge.append(rev_edge_mo_vu.animate.set_color(color).set_opacity(opacity).set_stroke(width=width))
                    else:
                        base_attrs = self.base_edge_visual_attrs.get((v, u), {})
                        color = base_attrs.get("color", DIMMED_COLOR)
                        opacity = base_attrs.get("opacity", DIMMED_OPACITY)
                        width = base_attrs.get("stroke_width", EDGE_STROKE_WIDTH)
                        # FIX: Use set_color and set_opacity for reverse edge
                        visual_updates_this_edge.append(rev_edge_mo_vu.animate.set_color(color).set_opacity(opacity).set_stroke(width=width))

                    if (v,u) not in self.original_edge_tuples:
                        label_mobj_vu = self.edge_residual_capacity_mobjects.get((v,u))
                        if label_mobj_vu:
                            visual_updates_this_edge.append(label_mobj_vu.animate.set_opacity(0.0))
                    else:
                        old_rev_flow_text_mobj = self.edge_flow_val_text_mobjects.get((v,u))
                        if old_rev_flow_text_mobj:
                            new_rev_flow_val_vu = self.flow[(v,u)]
                            new_rev_flow_str_vu = f"{new_rev_flow_val_vu:.0f}"
                            target_rev_text = Text(new_rev_flow_str_vu, font=old_rev_flow_text_mobj.font, font_size=old_rev_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_rev_text.height = self.scaled_flow_text_height
                            target_rev_text.move_to(old_rev_flow_text_mobj.get_center()).rotate(rev_edge_mo_vu.get_angle(), about_point=target_rev_text.get_center())
                            text_updates_this_edge.append(old_rev_flow_text_mobj.animate.become(target_rev_text))
                        
                        rev_label_grp_vu = self.edge_label_groups.get((v,u))
                        if rev_label_grp_vu and rev_label_grp_vu.submobjects:
                            target_opacity = 0.7 if res_cap_vu > 0 else self.base_label_visual_attrs.get((v,u), {}).get("opacity", DIMMED_OPACITY)
                            visual_updates_this_edge.append(rev_label_grp_vu.animate.set_opacity(target_opacity))

                if text_updates_this_edge or visual_updates_this_edge:
                    update_group_for_this_edge = AnimationGroup(
                        *(text_updates_this_edge + visual_updates_this_edge),
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
            self._update_sink_action_text("nothing", animate=True)
            self.update_status_text(f"Flow augmented. Current phase flow: {total_flow_this_phase:.1f}. Searching for next path...", color=WHITE, play_anim=True)
            self.wait(2.5)

        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
        if self.sink_action_text_mobj.text != "":
            self._update_sink_action_text("nothing", animate=True)

        return total_flow_this_phase
        
    def construct(self):
        # Main method to construct and run the Dinitz algorithm visualization.
        # Sets up the graph, then iteratively builds level graphs and finds blocking flows.

        self.setup_titles_and_placeholders() # Initialize all text mobjects
        if self.sink_action_text_mobj not in self.mobjects: # Ensure sink action text is on scene
            self.add(self.sink_action_text_mobj)

        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.scaled_flow_text_height = None # Will be set after labels are created
        self.update_section_title("1. Building the Flow Network", play_anim=True)

        # Initialize algorithm variables
        self.current_phase_num = 0
        self.max_flow_value = 0

        # Define graph structure (nodes, edges, capacities)
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11))
        self.edges_with_capacity_list = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        self.original_edge_tuples = set([(u,v) for u,v,c in self.edges_with_capacity_list])

        self.capacities = collections.defaultdict(int) # Stores (u,v) -> capacity
        self.flow = collections.defaultdict(int)       # Stores (u,v) -> flow
        self.adj = collections.defaultdict(list)       # Adjacency list for graph traversal

        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u) # For finding all neighbors (BFS/DFS structure)

        # Define layout for nodes
        self.graph_layout = {
            1: [-4,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }

        # Dictionaries to store mobjects for nodes, edges, and labels
        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {} # For "flow/capacity" display
        self.edge_label_groups = {} # Groups for (flow, slash, capacity) or (residual capacity)
        self.base_label_visual_attrs = {} # Stores original opacity for labels
        self.edge_residual_capacity_mobjects = {} # For non-original edges' capacity labels

        self.desired_large_scale = 1.6 # Scale factor for the main graph display

        # Create and animate node mobjects (dots and labels)
        nodes_vgroup = VGroup()
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=10, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label_str = "s" if v_id == self.source_node else "t" if v_id == self.sink_node else str(v_id)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(11)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)
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

        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        # Create and animate edge labels (flow/capacity)
        all_edge_labels_vgroup = VGroup()
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []

        for u, v, cap in self.edges_with_capacity_list: # Original edges
            arrow = self.edge_mobjects[(u,v)]
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)

            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u,v)] = cap_text_mobj
            self.base_label_visual_attrs[(u,v)] = {"opacity": 1.0} # Original labels are fully opaque

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            label_group.move_to(arrow.get_center()).rotate(arrow.get_angle())
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.15 # Offset label from edge
            label_group.shift(offset_vector).set_z_index(6)
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))

        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)

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

        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        self.wait(0.5)

        # Position the sink_action_text_mobj (for "augment", "retreat" messages)
        if hasattr(self, 'node_mobjects') and hasattr(self, 'source_node') and \
           self.source_node in self.node_mobjects and self.node_mobjects.get(self.source_node):
            source_node_dot = self.node_mobjects[self.source_node][0]
            self.sink_action_text_mobj.next_to(source_node_dot, UP, buff=BUFF_SMALL)
        else: # Fallback position
            self.sink_action_text_mobj.to_corner(UL, buff=BUFF_MED)

        # Determine scaled height for flow text labels for consistency
        sample_text_mobj = None
        for key_orig_edge in self.original_edge_tuples:
            if key_orig_edge in self.edge_flow_val_text_mobjects and self.edge_flow_val_text_mobjects[key_orig_edge] is not None:
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

        # Highlight source and sink nodes briefly
        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]
        temp_source_ring = Circle(radius=source_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(source_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        temp_sink_ring = Circle(radius=sink_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(sink_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        self.play(Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7),
                  Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7))
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)

        # Change labels of source and sink to "s" and "t"
        source_label_original = self.node_mobjects[self.source_node][1]
        sink_label_original = self.node_mobjects[self.sink_node][1]
        new_s_label_mobj = Text("s", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, color=self.base_node_visual_attrs[self.source_node]["label_color"]).move_to(source_label_original.get_center()).set_z_index(source_label_original.z_index)
        new_t_label_mobj = Text("t", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, color=self.base_node_visual_attrs[self.sink_node]["label_color"]).move_to(sink_label_original.get_center()).set_z_index(sink_label_original.z_index)
        self.play(Transform(source_label_original, new_s_label_mobj), Transform(sink_label_original, new_t_label_mobj), run_time=0.5)
        self.node_mobjects[self.source_node][1] = new_s_label_mobj
        self.node_mobjects[self.sink_node][1] = new_t_label_mobj
        self.wait(0.5)

        # --- Start Dinitz Algorithm Phases ---
        self.update_section_title("2. Running Dinitz's Algorithm", play_anim=True)
        self.wait(1.0)

        while True: # Main loop for Dinitz phases
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Step 1 - Build Level Graph (LG)", color=BLUE_B, play_anim=True)
            self._update_sink_action_text("nothing", animate=False)
            self.wait(1.0)
            self.update_status_text(f"BFS from S (Node {self.source_node}) to find shortest paths in the residual graph.", play_anim=True)
            self.wait(3.0)

            # --- KEY CONCEPT: Building the Level Graph ---
            self.levels = {v_id: -1 for v_id in self.vertices_data}
            q_bfs = collections.deque()
            self.levels[self.source_node] = 0; q_bfs.append(self.source_node)

            # Clear and update level display on screen
            if self.level_display_vgroup.submobjects:
                self.play(FadeOut(self.level_display_vgroup))
                self.level_display_vgroup.remove(*self.level_display_vgroup.submobjects)
            l_p0 = Text(f"L0:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
            l_n0_text = f" {{s ({self.source_node})}}"
            l_n0 = Text(l_n0_text, font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
            first_level_text_group = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL)
            self.level_display_vgroup.add(first_level_text_group)
            self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
            self.play(Write(first_level_text_group)); self.wait(1.0)
            max_level_text_width = config.frame_width * 0.30

            # Restore graph elements to base appearance before BFS highlighting
            restore_anims = []
            for v_id, node_group in self.node_mobjects.items():
                dot, lbl = node_group
                node_attrs = self.base_node_visual_attrs[v_id]
                restore_anims.append(dot.animate.set_width(node_attrs["width"]).set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"]).set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"]))
                if v_id != self.source_node and v_id != self.sink_node:
                    restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))
                elif v_id == self.source_node or v_id == self.sink_node:
                    restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))

            for edge_key, edge_mo in self.edge_mobjects.items():
                edge_attrs = self.base_edge_visual_attrs[edge_key]
                opacity = edge_attrs["opacity"]
                # FIX: Use set_color and set_opacity for restoration
                restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"]).set_opacity(opacity).set_stroke(width=edge_attrs["stroke_width"]))
                
                label_grp = self.edge_label_groups.get(edge_key)
                if label_grp and label_grp.submobjects:
                    base_label_attr = self.base_label_visual_attrs.get(edge_key)
                    base_opacity_for_label = base_label_attr.get("opacity", 0.0) if base_label_attr else (1.0 if edge_key in self.original_edge_tuples else 0.0)
                    restore_anims.append(label_grp.animate.set_opacity(base_opacity_for_label))
                    if base_opacity_for_label > 0 and edge_key in self.original_edge_tuples:
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
                nodes_this_level = list(q_bfs); q_bfs.clear()
                if not nodes_this_level: break
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
                        res_cap_bfs = self.capacities.get(edge_key_bfs,0) - self.flow.get(edge_key_bfs,0)
                        edge_mo_bfs = self.edge_mobjects.get(edge_key_bfs)

                        if edge_mo_bfs and res_cap_bfs > 0 and self.levels[v_n_bfs] == -1:
                            self.levels[v_n_bfs] = next_level_idx
                            nodes_found_next_level_set.add(v_n_bfs); q_bfs.append(v_n_bfs)

                            lvl_color_v = LEVEL_COLORS[next_level_idx % len(LEVEL_COLORS)]
                            n_v_dot, n_v_lbl = self.node_mobjects[v_n_bfs]
                            bfs_anims_this_step.extend([
                                n_v_dot.animate.set_fill(lvl_color_v).set_width(self.base_node_visual_attrs[v_n_bfs]["width"] * 1.1),
                                n_v_lbl.animate.set_color(BLACK if sum(color_to_rgb(lvl_color_v)) > 1.5 else WHITE)
                            ])
                            edge_color_u_for_lg = LEVEL_COLORS[self.levels[u_bfs] % len(LEVEL_COLORS)]
                            # FIX: Use set_opacity to ensure full edge is visible
                            bfs_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_u_for_lg).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))

                            if edge_key_bfs not in self.original_edge_tuples:
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get(edge_key_bfs)
                                if res_cap_mobj:
                                    target_text = Text(f"{res_cap_bfs:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=edge_color_u_for_lg)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_text.height = self.scaled_flow_text_height * 0.9
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                    bfs_anims_this_step.append(res_cap_mobj.animate.become(target_text))
                            else:
                                label_grp_bfs = self.edge_label_groups.get(edge_key_bfs)
                                if label_grp_bfs:
                                    bfs_anims_this_step.append(label_grp_bfs.animate.set_opacity(1.0))
                                    
                    self.play(FadeOut(ind_u), run_time=0.20)

                if bfs_anims_this_step: self.play(AnimationGroup(*bfs_anims_this_step, lag_ratio=0.1), run_time=0.8); self.wait(0.5)

                if nodes_found_next_level_set:
                    def get_node_display_name(n_id):
                        if n_id == self.source_node: return f"s ({n_id})"
                        if n_id == self.sink_node: return f"t ({n_id})"
                        return str(n_id)
                    n_str_list = [get_node_display_name(n) for n in sorted(list(nodes_found_next_level_set))]
                    n_str = ", ".join(n_str_list)
                    self.update_status_text(f"BFS: L{next_level_idx} nodes found: {{{n_str}}}", play_anim=False)
                    self.wait(0.5)
                    l_px = Text(f"L{next_level_idx}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[next_level_idx%len(LEVEL_COLORS)])
                    l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
                    new_level_text_entry = VGroup(l_px,l_nx).arrange(RIGHT,buff=BUFF_VERY_SMALL)
                    self.level_display_vgroup.add(new_level_text_entry)
                    self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                    if self.level_display_vgroup.width > max_level_text_width:
                        self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                    self.play(Write(new_level_text_entry)); self.wait(1.5)
                if not q_bfs: break

            sink_display_name = "t"
            if self.levels[self.sink_node] == -1:
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) not reached by BFS. No more augmenting paths.", color=RED_C, play_anim=True)
                self.wait(3.0)
                self.update_max_flow_display(play_anim=True)
                self.update_phase_text(f"Algorithm Complete. Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.update_status_text(f"Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
                self._update_sink_action_text("nothing", animate=False)
                self.wait(4.5)
                break
            else:
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) found at L{self.levels[self.sink_node]}. Level Graph established.", color=GREEN_A, play_anim=True); self.wait(3.0)

                latex_status_string = r"\mbox{Isolating LG: Keep edges $(u,v)$ where $level(v)=level(u)+1$.}"
                self.update_status_text(latex_status_string, play_anim=True, is_latex=True)
                self.wait(1.0)

                lg_iso_anims = []
                for (u_lg,v_lg), edge_mo_lg in self.edge_mobjects.items():
                    res_cap_lg_val = self.capacities.get((u_lg,v_lg),0)-self.flow.get((u_lg,v_lg),0)
                    is_lg_edge = (self.levels.get(u_lg,-1)!=-1 and self.levels.get(v_lg,-1)!=-1 and \
                                  self.levels[v_lg]==self.levels[u_lg]+1 and res_cap_lg_val > 0)
                    label_grp_lg = self.edge_label_groups.get((u_lg,v_lg))

                    if is_lg_edge:
                        lg_color = LEVEL_COLORS[self.levels[u_lg]%len(LEVEL_COLORS)]
                        lg_iso_anims.append(edge_mo_lg.animate.set_color(lg_color).set_opacity(1.0).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples:
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get((u_lg,v_lg))
                                if res_cap_mobj:
                                    target_text = Text(f"{res_cap_lg_val:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=lg_color)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_text.height = self.scaled_flow_text_height * 0.9
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                    lg_iso_anims.append(res_cap_mobj.animate.become(target_text))
                            else:
                                lg_iso_anims.append(label_grp_lg.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                    else:
                        base_attrs = self.base_edge_visual_attrs.get((u_lg, v_lg), {})
                        target_color = DIMMED_COLOR
                        target_opacity = DIMMED_OPACITY
                        target_width = base_attrs.get("stroke_width", EDGE_STROKE_WIDTH)
                        
                        # FIX: Use set_color and set_opacity for dimming non-LG edges
                        lg_iso_anims.append(edge_mo_lg.animate.set_color(target_color).set_opacity(target_opacity).set_stroke(width=target_width))

                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples:
                                lg_iso_anims.append(label_grp_lg.animate.set_opacity(0.0))
                            else:
                                lg_iso_anims.append(label_grp_lg.animate.set_opacity(DIMMED_OPACITY))
                                
                if lg_iso_anims: self.play(AnimationGroup(*lg_iso_anims, lag_ratio=0.05), run_time=1.0)
                self.wait(2.0)
                self.update_status_text("Level Graph isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True); self.wait(2.5)

                flow_this_phase = self.animate_dfs_path_finding_phase()

                self._update_sink_action_text("nothing", animate=False)
                self.update_phase_text(f"End of Phase {self.current_phase_num}. Blocking Flow: {flow_this_phase:.1f}. Total Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.wait(3.5)
                if self.levels.get(self.sink_node, -1) != -1 :
                    self.update_status_text(f"Phase complete. Resetting for the next BFS.", color=BLUE_A, play_anim=True)
                    self.wait(3.0)

        # Algorithm conclusion
        self.update_section_title("3. Dinitz Algorithm Summary", play_anim=True)
        self.wait(1.0)
        if self.levels.get(self.sink_node, -1) == -1 and self.max_flow_value == 0 :
            self.update_status_text(f"Algorithm Concluded. Sink Unreachable. Max Flow: {self.max_flow_value:.1f}", color=RED_A, play_anim=True)
        elif self.levels.get(self.sink_node, -1) == -1 :
            self.update_status_text(f"Algorithm Concluded. Sink Unreachable in last BFS. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
        else:
            self.update_status_text(f"Algorithm Concluded. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
        self.wait(5.0)

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