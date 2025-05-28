from manim import *
import collections
import numpy as np

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.18

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 # For text below main title
PHASE_TEXT_FONT_SIZE = 22     # For text below section title
STATUS_TEXT_FONT_SIZE = 20    # For text below phase title
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
RING_Z_INDEX = 4

LEVEL_COLORS = [RED_D, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK]
DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 4.5
DFS_EDGE_TRY_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.15
DFS_PATH_EDGE_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.25
BOTTLENECK_EDGE_INDICATE_COLOR = RED_D

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

REVERSE_EDGE_COLOR = GREY_B
REVERSE_EDGE_OPACITY = 0.15
REVERSE_EDGE_STROKE_WIDTH_FACTOR = 0.6
REVERSE_EDGE_Z_INDEX = -1

TOP_CENTER_ANCHOR = UP * (config.frame_height / 2 - BUFF_SMALL)


class DinitzAlgorithmVisualizer(Scene):

    def setup_titles_and_placeholders(self):
        self.main_title = Text("Visualizing Dinitz's Algorithm for Max Flow", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.move_to(TOP_CENTER_ANCHOR).set_z_index(10)
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
        old_text_had_actual_content = False
        if isinstance(old_mobj, Text) and old_mobj.text != "":
            old_text_had_actual_content = True
        elif isinstance(old_mobj, Tex) and old_mobj.tex_string != "":
            old_text_had_actual_content = True

        out_animation, in_animation = None, None
        if old_text_had_actual_content and old_mobj is not new_mobj :
             out_animation = FadeOut(old_mobj, run_time=0.35)

        new_text_has_actual_content = False
        if new_text_content_str and new_text_content_str != "":
            new_text_has_actual_content = True

        if new_text_has_actual_content:
            in_animation = FadeIn(new_mobj, run_time=0.35, shift=ORIGIN)
        elif old_text_had_actual_content and not out_animation:
            if old_mobj in self.mobjects and old_mobj.get_family_members_with_points() : # Check if it's still part of the scene
                 out_animation = FadeOut(old_mobj, run_time=0.35)


        animations = [anim for anim in [out_animation, in_animation] if anim]
        if animations: self.play(*animations)


    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False):
        old_mobj = getattr(self, text_attr_name)

        if is_latex:
            new_mobj = Tex(new_text_content, color=color)
            # Attempt to scale LaTeX to match font_size approximately
            ref_text_for_height = Text("Mg", font_size=font_size) # Reference for typical cap height
            if ref_text_for_height.height > 0.001 and new_mobj.height > 0.001: # Avoid division by zero
                new_mobj.scale_to_fit_height(ref_text_for_height.height)
        else:
            new_mobj = Text(new_text_content, font_size=font_size, weight=weight, color=color)


        current_idx = -1
        if old_mobj in self.info_texts_group.submobjects:
            current_idx = self.info_texts_group.submobjects.index(old_mobj)
            new_mobj.move_to(old_mobj.get_center()) # Keep position before group re-arrangement
            self.info_texts_group.remove(old_mobj)


        if old_mobj in self.mobjects : # General removal from scene if it was added directly
            self.remove(old_mobj)

        if current_idx != -1 : # Re-insert into the VGroup at the same position
            self.info_texts_group.insert(current_idx, new_mobj)

        setattr(self, text_attr_name, new_mobj) # Update the class attribute
        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED) # Rearrange the VGroup
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') and old_mobj.z_index is not None else 10)


        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_content)
        else:
            # If not animating, ensure the new mobject is added if it has content and isn't already part of info_texts_group
            # And ensure old one is removed. The removal of old_mobj is handled above.
            is_empty_new_content = (isinstance(new_mobj, Text) and new_mobj.text == "") or \
                                 (isinstance(new_mobj, Tex) and new_mobj.tex_string == "")
            is_in_group = new_mobj in self.info_texts_group.submobjects

            if is_empty_new_content:
                # Empty texts are handled by the general logic; if they are in the group, they stay.
                # If not in group and on scene, self.remove(old_mobj) already handled it.
                # If new_mobj is empty and not in group, it won't be added here.
                pass
            else: # Has content
                if not is_in_group and new_mobj not in self.mobjects:
                    self.add(new_mobj)


    def update_section_title(self, text_str, play_anim=True):
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex)

    def update_max_flow_display(self, play_anim=True):
        new_text_str = f"Sink's value of flow: {self.max_flow_value:.1f}"
        self._update_text_generic("max_flow_display_mobj", new_text_str, MAX_FLOW_DISPLAY_FONT_SIZE, BOLD, GREEN_C, play_anim)

    def _update_sink_action_text(self, new_text_content, new_color=YELLOW, animate=True):
        current_mobj = self.sink_action_text_mobj
        old_text_content = current_mobj.text
        old_color_val = current_mobj.get_color()

        if old_text_content == new_text_content and old_color_val == new_color:
            return # No change needed

        target_text_template = Text(
            new_text_content,
            font_size=STATUS_TEXT_FONT_SIZE, # Use the same font size as algo_status for consistency
            weight=current_mobj.weight, # Use current weight, e.g., BOLD
            color=new_color
        )

        # --- Positioning block (MODIFICATION START by user, kept) ---
        # Position the target_text_template relative to the SOURCE node.
        if hasattr(self, 'node_mobjects') and \
           hasattr(self, 'source_node') and \
           self.source_node in self.node_mobjects and \
           self.node_mobjects.get(self.source_node) is not None:
            source_node_group = self.node_mobjects[self.source_node]
            if isinstance(source_node_group, VGroup) and len(source_node_group.submobjects) > 0:
                source_node_dot = source_node_group[0] # Assuming the first element is the Dot
                target_text_template.next_to(source_node_dot, UP, buff=BUFF_SMALL)
            else: # Should not happen if source_node_group is valid
                target_text_template.move_to(current_mobj.get_center()) # Fallback
        else: # Fallback if source node isn't ready/available
            target_text_template.move_to(current_mobj.get_center())
        
        target_text_template.set_z_index(current_mobj.z_index)
        # --- Positioning block END ---

        if animate:
            if old_text_content and not new_text_content: # Fading out (e.g. "retreat" to "")
                self.play(FadeOut(current_mobj, run_time=0.25))
                current_mobj.become(target_text_template) # Update the mobject's content even if it's now empty
            elif not old_text_content and new_text_content: # Fading in (e.g. "" to "augment")
                current_mobj.become(target_text_template)
                self.play(FadeIn(current_mobj, run_time=0.25))
            elif old_text_content and new_text_content: # Changing text (both non-empty)
                # To animate change, we can fade out old, then fade in new
                # This requires making a temporary copy of old state if current_mobj is updated too soon
                old_mobj_anim_copy = current_mobj.copy() # Create a copy with the old appearance
                current_mobj.become(target_text_template) # Update the actual mobject in-place
                
                # FadeOut will add old_mobj_anim_copy to scene for animation then remove it.
                self.play(
                    FadeOut(old_mobj_anim_copy, run_time=0.20, scale=0.8),
                    FadeIn(current_mobj, run_time=0.20, scale=1.2) # Fade in the updated mobject
                )
            elif new_text_content and old_text_content == new_text_content and old_color_val != new_color: # Only color change
                 self.play(current_mobj.animate.set_color(new_color), run_time=0.3)
            elif not new_text_content and not old_text_content and old_color_val != new_color: # Color change for empty text (no visual change unless color has meaning)
                 current_mobj.set_color(new_color) # Silently update color of empty text
        else: # Not animated
            current_mobj.become(target_text_template) # Directly update the mobject
            if current_mobj not in self.mobjects: # Should always be in self.mobjects after initial add in construct
                self.add(current_mobj)
            # When new_text_content is "", current_mobj becomes an empty text.
            # It remains in self.mobjects.

    def _dfs_recursive_find_path_anim(self, u, pushed, current_path_info_list):
        u_dot_group = self.node_mobjects[u]
        u_dot = u_dot_group[0]

        highlight_ring = Circle(radius=u_dot.width/2 * 1.3, color=PINK, stroke_width=RING_STROKE_WIDTH * 0.7) \
            .move_to(u_dot.get_center()).set_z_index(u_dot.z_index + 2)
        self.dfs_traversal_highlights.add(highlight_ring)
        self.play(Create(highlight_ring), run_time=0.3)
        self.wait(0.5)

        u_display_name = "s" if u == self.source_node else "t" if u == self.sink_node else str(u)

        if u == self.sink_node:
            self.update_status_text(f"DFS Path to Sink T (Node {self.sink_node}) found!", color=GREEN_B, play_anim=False)
            self._update_sink_action_text("advance", new_color=BLUE_A, animate=True) # Text will be above source
            self.wait(2.0)
            self.play(FadeOut(highlight_ring), run_time=0.15)
            if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
            return pushed

        self.update_status_text(f"DFS Advance: From {u_display_name}, exploring valid LG edges.", play_anim=False)
        self.wait(1.5)

        # Iterate over neighbors using self.ptr[u] to handle visited edges from this node in current DFS
        while self.ptr[u] < len(self.adj[u]): # adj[u] should be LG neighbors
            v_candidate = self.adj[u][self.ptr[u]] # This adj might be the original graph's adj
                                                   # Need to filter for LG edges
            edge_key_uv = (u, v_candidate)

            # Check if this edge is in the Level Graph
            # An edge (u,v) is in LG if level[v] == level[u] + 1 and residual_capacity(u,v) > 0
            res_cap_cand = self.capacities.get(edge_key_uv, 0) - self.flow.get(edge_key_uv, 0)
            edge_mo_cand = self.edge_mobjects.get(edge_key_uv)

            is_valid_lg_edge = (edge_mo_cand and
                                self.levels.get(v_candidate, -1) == self.levels.get(u, -1) + 1 and
                                res_cap_cand > 0)

            if is_valid_lg_edge:
                actual_v = v_candidate # This is indeed a valid neighbor in LG
                edge_mo_for_v = edge_mo_cand
                actual_v_display_name = "s" if actual_v == self.source_node else "t" if actual_v == self.sink_node else str(actual_v)

                # Store original visual properties to restore on backtrack or if edge capacity drops
                original_edge_color = edge_mo_for_v.get_color()
                original_edge_width = edge_mo_for_v.stroke_width
                original_edge_opacity = edge_mo_for_v.stroke_opacity

                # Animate trying this edge
                current_anims_try = [
                    edge_mo_for_v.animate.set_color(YELLOW_A).set_stroke(width=DFS_EDGE_TRY_WIDTH, opacity=1.0)
                ]
                # If it's a pure residual edge, animate its capacity label
                if edge_key_uv not in self.original_edge_tuples: # i.e. it's a reverse edge in residual graph context
                    label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                    if label_mobj:
                        target_label = Text(f"{res_cap_cand:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=YELLOW_A)
                        target_label.move_to(label_mobj.get_center()).set_opacity(1.0)
                        if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label.height = self.scaled_flow_text_height * 0.9
                        current_anims_try.append(label_mobj.animate.become(target_label))

                self.update_status_text(f"DFS Try: Edge ({u_display_name},{actual_v_display_name}), Res.Cap: {res_cap_cand:.0f}.", play_anim=False)
                self.wait(1.5) # Time to read status
                if current_anims_try: self.play(*current_anims_try, run_time=0.4)
                self.wait(0.5) # Time to see highlight

                tr = self._dfs_recursive_find_path_anim(actual_v, min(pushed, res_cap_cand), current_path_info_list)

                current_anims_backtrack_restore = []
                if tr > 0: # Path found through v
                    self.update_status_text(f"DFS Path Segment: ({u_display_name},{actual_v_display_name}) is part of an s-t path.", color=GREEN_C, play_anim=False)
                    self.wait(1.5)
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v, original_edge_color, original_edge_width, original_edge_opacity))
                    self.play(FadeOut(highlight_ring), run_time=0.15) # Remove highlight from u as we return up stack
                    if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr # Return flow pushed

                # Backtrack from v: no path found through v or v's capacity used up by other paths
                self.update_status_text(f"DFS Retreat: Edge ({u_display_name},{actual_v_display_name}) is a dead end. Backtracking.", color=YELLOW_C, play_anim=False)
                self._update_sink_action_text("retreat", new_color=ORANGE, animate=True) # Text will be above source
                self.wait(1.5)

                # Restore edge appearance if it's still a valid LG edge or revert to dimmed
                # res_cap_cand is capacity *before* recursive call. We need current capacity.
                current_res_cap_after_fail = self.capacities.get(edge_key_uv, 0) - self.flow.get(edge_key_uv, 0)
                is_still_lg_edge_after_fail = (self.levels.get(actual_v, -1) == self.levels.get(u, -1) + 1 and current_res_cap_after_fail > 0)

                if is_still_lg_edge_after_fail:
                    lg_color = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)] # Color based on u's level
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(lg_color).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0)
                    )
                    if edge_key_uv not in self.original_edge_tuples:
                        label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                        if label_mobj:
                            target_label_revert = Text(f"{current_res_cap_after_fail:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=lg_color)
                            target_label_revert.move_to(label_mobj.get_center()).set_opacity(1.0)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_revert.height = self.scaled_flow_text_height * 0.9
                            current_anims_backtrack_restore.append(label_mobj.animate.become(target_label_revert))
                else: # Not a valid LG edge anymore (e.g. capacity became 0 due to another path)
                    current_anims_backtrack_restore.append(
                        edge_mo_for_v.animate.set_color(DIMMED_COLOR).set_stroke(width=EDGE_STROKE_WIDTH, opacity=DIMMED_OPACITY)
                    )
                    if edge_key_uv not in self.original_edge_tuples:
                        label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                        if label_mobj: current_anims_backtrack_restore.append(label_mobj.animate.set_opacity(0.0))


                if current_anims_backtrack_restore: self.play(*current_anims_backtrack_restore, run_time=0.4)
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.0, run_time=0.45)) # Indicate it's a dead end
                self.wait(0.5)
                self.update_status_text(f"DFS Advance: From {u_display_name}, exploring next valid LG edge.", play_anim=False) # For the while loop
                self.wait(1.0)

            self.ptr[u] += 1 # Move to next neighbor for node u

        # All neighbors of u explored from this DFS path
        self.update_status_text(f"DFS Retreat: All LG edges from {u_display_name} explored. Backtracking from {u_display_name}.", color=ORANGE, play_anim=False)
        self._update_sink_action_text("retreat", new_color=ORANGE, animate=True) # Text will be above source
        self.wait(2.0)
        self.play(FadeOut(highlight_ring), run_time=0.15) # Remove highlight from u
        if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
        return 0 # No flow pushed from u along this path attempt

    def animate_dfs_path_finding_phase(self):
        self.ptr = {v_id: 0 for v_id in self.vertices_data} # Reset pointers for each DFS phase for all nodes
        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1) # Group for DFS traversal node highlights
        if self.dfs_traversal_highlights not in self.mobjects: self.add(self.dfs_traversal_highlights)

        self._update_sink_action_text("", animate=False) # Ensure sink action text is clear at start of DFS

        self.update_phase_text(f"Phase {self.current_phase_num}: Step 2 - Find Blocking Flow in LG (DFS)", color=ORANGE)
        self.update_status_text("DFS searches for s-t paths in LG to create a blocking flow.", play_anim=True)
        self.wait(3.0)

        while True:
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Seeking s->t path in LG from S (Node {self.source_node}).", play_anim=True)
            self.wait(1.5) # Time to read status
            current_path_anim_info = [] # Stores ((u,v), edge_mo, orig_color, orig_width, orig_opacity)

            # DFS finds one path and its bottleneck capacity
            bottleneck_flow = self._dfs_recursive_find_path_anim(self.source_node, float('inf'), current_path_anim_info)

            if bottleneck_flow == 0: # No more s-t paths can be found in LG
                self.update_status_text("No more s-t paths in LG. Blocking flow for this phase is complete.", color=YELLOW_C, play_anim=True)
                self.wait(3.5)
                break # Exit while loop for finding paths

            # An s-t path was found
            self.max_flow_value += bottleneck_flow
            total_flow_this_phase += bottleneck_flow

            # Identify bottleneck edges for indication (edges whose residual capacity becomes 0)
            bottleneck_edges_for_indication = []
            current_path_anim_info.reverse() # Path from S to T

            for (u_path, v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                edge_key = (u_path, v_path)
                res_cap_before_aug = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                # If this edge's capacity was the limiting factor
                if abs(res_cap_before_aug - bottleneck_flow) < 0.01: # Compare with tolerance
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


            self.update_status_text(f"Path #{path_count_this_phase} found. Bottleneck: {bottleneck_flow:.1f}. Augmenting...", color=GREEN_A, play_anim=True)
            self._update_sink_action_text("augment", new_color=GREEN_B, animate=True) # Text will be above source
            self.wait(2.5)

            # Highlight the path before augmentation
            path_highlight_anims = []
            for (u_path, v_path), edge_mo_path, _, _, _ in current_path_anim_info: # Path is S to T
                path_highlight_anims.append(edge_mo_path.animate.set_color(GREEN_D).set_stroke(width=DFS_PATH_EDGE_WIDTH, opacity=1.0))

            if path_highlight_anims: self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.15, run_time=1.0))
            self.wait(2.0) # See augmented path

            # Augment flow and update edge appearances
            augmentation_anims = []
            text_update_anims = [] # For original edge flow/capacity labels

            for (u,v), edge_mo, original_color, original_width, original_opacity in current_path_anim_info:
                # Augment flow
                self.flow[(u,v)] = self.flow.get((u,v), 0) + bottleneck_flow
                self.flow[(v,u)] = self.flow.get((v,u), 0) - bottleneck_flow # Update reverse flow

                # Update original edge's flow text if it's an original edge
                if (u,v) in self.original_edge_tuples:
                    old_flow_text_mobj = self.edge_flow_val_text_mobjects[(u,v)]
                    new_flow_val_uv = self.flow[(u,v)]
                    new_flow_str_uv = f"{new_flow_val_uv:.0f}" if abs(new_flow_val_uv - round(new_flow_val_uv)) < 0.01 else f"{new_flow_val_uv:.1f}"
                    target_text_template_uv = Text(new_flow_str_uv, font=old_flow_text_mobj.font, font_size=old_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                        target_text_template_uv.height = self.scaled_flow_text_height
                    else: target_text_template_uv.match_height(old_flow_text_mobj) # Fallback
                    target_text_template_uv.move_to(old_flow_text_mobj.get_center()).rotate(edge_mo.get_angle(), about_point=target_text_template_uv.get_center())
                    text_update_anims.append(old_flow_text_mobj.animate.become(target_text_template_uv))


                # Update appearance of edge (u,v)
                res_cap_after_uv = self.capacities.get((u,v),0) - self.flow.get((u,v),0)
                is_still_lg_edge_uv = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                                       self.levels[v]==self.levels[u]+1 and res_cap_after_uv > 0 )

                if not is_still_lg_edge_uv: # Edge (u,v) is no longer in LG (saturated or path changed levels)
                    augmentation_anims.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR, width=EDGE_STROKE_WIDTH))
                    if (u,v) not in self.original_edge_tuples: # Pure residual edge label
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv: augmentation_anims.append(label_mobj_uv.animate.set_opacity(0.0))
                else: # Edge (u,v) is still in LG, update its color and residual cap if it's a pure residual edge
                    lg_color_uv = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                    augmentation_anims.append(edge_mo.animate.set_color(lg_color_uv).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))
                    if (u,v) not in self.original_edge_tuples: # Pure residual edge label
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv:
                            target_label_uv = Text(f"{res_cap_after_uv:.0f}", font=label_mobj_uv.font, font_size=label_mobj_uv.font_size, color=lg_color_uv)
                            target_label_uv.move_to(label_mobj_uv.get_center()).set_opacity(1.0)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_uv.height = self.scaled_flow_text_height * 0.9
                            augmentation_anims.append(label_mobj_uv.animate.become(target_label_uv))


                # Update appearance of reverse edge (v,u)
                if (v,u) in self.edge_mobjects: # Check if reverse edge mobject exists
                    rev_edge_mo_vu = self.edge_mobjects[(v,u)]
                    res_cap_vu = self.capacities.get((v,u),0) - self.flow.get((v,u),0) # c(v,u) - f(v,u) = c(v,u) - (-f(u,v)) = c(v,u) + f(u,v)
                                                                                       # If c(v,u) = 0 (original graph), then res_cap_vu = f(u,v)

                    is_rev_edge_in_lg_vu = (self.levels.get(v,-1)!=-1 and self.levels.get(u,-1)!=-1 and \
                                            self.levels[u]==self.levels[v]+1 and res_cap_vu > 0) # Check if (v,u) is now in LG

                    if is_rev_edge_in_lg_vu: # Reverse edge (v,u) becomes part of LG
                        lg_color_vu = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(lg_color_vu))
                    elif res_cap_vu > 0 : # Still has residual capacity but not in LG (or original edge not in LG)
                        base_attrs_vu_edge = self.base_edge_visual_attrs.get((v,u),{})
                        # Make it visible based on its base properties if it's an original edge, or standard reverse otherwise
                        opacity_vu = 0.7 if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("opacity", REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0)
                        color_vu = GREY_A if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("color", REVERSE_EDGE_COLOR)
                        width_vu = EDGE_STROKE_WIDTH if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("stroke_width", EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR)
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=opacity_vu, width=width_vu, color=color_vu))
                    else: # No residual capacity for (v,u)
                        base_attrs_vu_edge = self.base_edge_visual_attrs.get((v,u),{})
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=base_attrs_vu_edge.get("opacity",DIMMED_OPACITY), width=base_attrs_vu_edge.get("stroke_width",EDGE_STROKE_WIDTH), color=base_attrs_vu_edge.get("color",DIMMED_COLOR)))


                    # Update label for reverse edge (v,u)
                    if (v,u) not in self.original_edge_tuples: # It's a pure residual edge
                        label_mobj_vu = self.edge_residual_capacity_mobjects.get((v,u))
                        if label_mobj_vu:
                            if is_rev_edge_in_lg_vu: # Show its capacity if it's in LG
                                lg_color_vu_label = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                                target_label_vu = Text(f"{res_cap_vu:.0f}", font=label_mobj_vu.font, font_size=label_mobj_vu.font_size, color=lg_color_vu_label)
                                target_label_vu.move_to(label_mobj_vu.get_center()).set_opacity(1.0)
                                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                    target_label_vu.height = self.scaled_flow_text_height * 0.9
                                augmentation_anims.append(label_mobj_vu.animate.become(target_label_vu))
                            else: # Hide label if not in LG (or make it very dim if it has capacity but not LG)
                                augmentation_anims.append(label_mobj_vu.animate.set_opacity(0.0)) # Dim or hide
                    else: # It's an original edge, update its f/c label
                        old_rev_flow_text_mobj = self.edge_flow_val_text_mobjects.get((v,u))
                        if old_rev_flow_text_mobj: # If this original edge has a flow label
                            new_rev_flow_val_vu = self.flow[(v,u)] # This will be negative if flow is u->v
                            new_rev_flow_str_vu = f"{new_rev_flow_val_vu:.0f}" if abs(new_rev_flow_val_vu - round(new_rev_flow_val_vu)) < 0.01 else f"{new_rev_flow_val_vu:.1f}"
                            target_rev_text_template_vu = Text(new_rev_flow_str_vu, font=old_rev_flow_text_mobj.font, font_size=old_rev_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_rev_text_template_vu.height = self.scaled_flow_text_height
                            else: target_rev_text_template_vu.match_height(old_rev_flow_text_mobj)
                            target_rev_text_template_vu.move_to(old_rev_flow_text_mobj.get_center()).rotate(rev_edge_mo_vu.get_angle(), about_point=target_rev_text_template_vu.get_center())
                            text_update_anims.append(old_rev_flow_text_mobj.animate.become(target_rev_text_template_vu))

                        # Adjust opacity of the entire label group for original reverse edges
                        rev_label_grp_vu = self.edge_label_groups.get((v,u))
                        if rev_label_grp_vu and rev_label_grp_vu.submobjects: # Check if it exists and has parts
                            if is_rev_edge_in_lg_vu: # If in LG, make fully visible
                                for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR)) # color for text
                            elif res_cap_vu > 0: # Has capacity, but not in LG
                                for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(0.7)) # Semi-visible
                            else: # No capacity (or original capacity was 0 and no reverse flow)
                                base_lbl_attrs = self.base_label_visual_attrs.get((v,u))
                                if base_lbl_attrs:
                                    for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(base_lbl_attrs.get("opacity", DIMMED_OPACITY)))


            if text_update_anims or augmentation_anims:
                 self.play(AnimationGroup(*(text_update_anims + augmentation_anims), lag_ratio=0.1), run_time=1.5)
            else: self.wait(0.1) # Ensure some pause if no visual changes

            self.update_max_flow_display(play_anim=True)
            self.wait(0.5)

            self._update_sink_action_text("", animate=True) # Clear "augment" text

            self.update_status_text(f"Flow augmented. Current phase flow: {total_flow_this_phase:.1f}. Searching next path...", color=WHITE, play_anim=True)
            self.wait(2.5) # Time to read status and see graph state

        # DFS loop finished for this phase
        if self.dfs_traversal_highlights.submobjects: # Clear any remaining DFS node highlights
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)

        # Ensure sink action text is cleared if it was set to "retreat" by the last DFS step and loop broke
        if self.sink_action_text_mobj.text != "":
            self._update_sink_action_text("", animate=True) # Text will be above source (empty)

        return total_flow_this_phase

    def construct(self):
        self.setup_titles_and_placeholders()
        if self.sink_action_text_mobj not in self.mobjects: # Ensure it's added initially
            self.add(self.sink_action_text_mobj)

        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.scaled_flow_text_height = None # Will be set after graph scaling
        self.update_section_title("1. Building the Flow Network", play_anim=True)

        self.current_phase_num = 0
        self.max_flow_value = 0

        # Graph Definition
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11)) # Nodes 1 to 10
        self.edges_with_capacity_list = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        self.original_edge_tuples = set([(u,v) for u,v,c in self.edges_with_capacity_list])

        self.capacities = collections.defaultdict(int)
        self.flow = collections.defaultdict(int) # Stores f(u,v)
        self.adj = collections.defaultdict(list) # Adjacency list for graph structure (residual graph)

        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            # self.capacities[(v,u)] = 0 # Assuming directed edges, reverse capacity is 0 unless specified
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u) # For BFS/DFS to explore both directions in residual graph context

        self.graph_layout = { # X, Y, Z coordinates for nodes
            1: [-4,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }

        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {}
        self.edge_label_groups = {} # VGroups for "flow / capacity" or just "res_cap"
        self.base_label_visual_attrs = {} # To store original opacity etc for labels
        self.edge_residual_capacity_mobjects = {} # For pure reverse edges in residual graph

        self.desired_large_scale = 1.6 # Scale factor for the graph

        # Create Nodes
        nodes_vgroup = VGroup()
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])

        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        # Create Edges (Original and placeholders for reverse in residual graph)
        edges_vgroup = VGroup()
        edge_grow_anims = []
        for u,v,cap in self.edges_with_capacity_list: # Original edges
            n_u_dot = self.node_mobjects[u][0]; n_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS, stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow; edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        all_edge_labels_vgroup = VGroup() # Parent for all labels for scaling
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []

        # Create Labels for Original Edges "0 / C"
        for u, v, cap in self.edges_with_capacity_list:
            arrow = self.edge_mobjects[(u,v)]
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR) # Smaller than flow/cap
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)

            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u,v)] = cap_text_mobj
            self.base_label_visual_attrs[(u,v)] = {"opacity": 1.0} # Default for original labels

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            # Position and rotate label with edge
            label_group.move_to(arrow.get_center()).rotate(arrow.get_angle()) # Rotate around its own center first
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.15 # Offset perpendicular to edge
            label_group.shift(offset_vector).set_z_index(1) # Ensure labels above edges
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj)) # Group flow and slash for Write

        # Create Mobjects for PURE REVERSE EDGES (residual capacity only, initially 0 and hidden)
        for u_node in self.vertices_data:
            for v_node in self.adj[u_node]: # adj contains all potential connections for residual graph
                current_edge_tuple = (u_node, v_node)
                # If this is a reverse of an original edge OR a connection not in original_edges_with_capacity
                if current_edge_tuple not in self.original_edge_tuples and current_edge_tuple not in self.edge_mobjects:
                    n_u_dot = self.node_mobjects[u_node][0]; n_v_dot = self.node_mobjects[v_node][0]
                    rev_arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS,
                                      stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR,
                                      color=REVERSE_EDGE_COLOR,
                                      max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH * 0.8, # Slightly smaller tip
                                      z_index=REVERSE_EDGE_Z_INDEX) # Behind original edges
                    rev_arrow.set_opacity(REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0) # Initially very dim or invisible
                    self.edge_mobjects[current_edge_tuple] = rev_arrow
                    edges_vgroup.add(rev_arrow) # Add to the main edges group for scaling

                    # Residual capacity label for this pure reverse edge
                    # Initial residual capacity is 0 (since flow is 0, and original capacity c(u,v) for this pure reverse is 0)
                    res_cap_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR, opacity=0.0) # Initially hidden
                    res_cap_val_mobj.move_to(rev_arrow.get_center()).rotate(rev_arrow.get_angle())
                    offset_vector_rev = rotate_vector(rev_arrow.get_unit_vector(), PI / 2) * 0.15
                    res_cap_val_mobj.shift(offset_vector_rev).set_z_index(1) # Same z as other labels

                    self.edge_residual_capacity_mobjects[current_edge_tuple] = res_cap_val_mobj
                    self.base_label_visual_attrs[current_edge_tuple] = {"opacity": 0.0} # Default for pure reverse labels

                    pure_rev_label_group = VGroup(res_cap_val_mobj) # Group for scaling
                    pure_rev_label_group.set_opacity(0.0)
                    self.edge_label_groups[current_edge_tuple] = pure_rev_label_group
                    all_edge_labels_vgroup.add(pure_rev_label_group)


        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)

        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        # Calculate target position based on scaled height
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        # network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_LARGE # From bottom
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE # More space from bottom
        target_position = np.array([0, network_target_y, 0]) # Centered horizontally

        # Store base visual attributes for edges (color, width, opacity) AFTER they are created
        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(),
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }
            # Ensure base label visual attrs are set for all edges that have labels
            if edge_key not in self.base_label_visual_attrs: # If not set during label creation (e.g. pure reverse)
                if edge_key in self.original_edge_tuples:
                    self.base_label_visual_attrs[edge_key] = {"opacity": 1.0} # Should have been set
                else: # Pure reverse edges, might not have explicit label opacity if REVERSE_EDGE_OPACITY is 0
                    self.base_label_visual_attrs[edge_key] = {"opacity": 0.0} # Default to hidden


        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        self.wait(0.5)

        # Initial positioning of sink_action_text_mobj (ABOVE SOURCE node)
        # This needs to happen AFTER nodes are scaled and positioned.
        if hasattr(self, 'node_mobjects') and hasattr(self, 'source_node') and \
           self.source_node in self.node_mobjects and self.node_mobjects.get(self.source_node):
            source_node_dot = self.node_mobjects[self.source_node][0] # The Dot mobject
            self.sink_action_text_mobj.next_to(source_node_dot, UP, buff=BUFF_SMALL)
        else: # Fallback if source node isn't ready
            self.sink_action_text_mobj.to_corner(UL, buff=BUFF_MED) # Default position if source node not found

        # Adjust initial opacity of pure reverse edges if REVERSE_EDGE_OPACITY is 0.0 after scaling
        # This ensures they are truly invisible if intended.
        for edge_key, edge_mo in self.edge_mobjects.items():
            base_attrs_edge = self.base_edge_visual_attrs.get(edge_key)
            if base_attrs_edge:
                current_opacity = base_attrs_edge["opacity"]
                if edge_key not in self.original_edge_tuples and REVERSE_EDGE_OPACITY == 0.0:
                    current_opacity = 0.0 # Force invisible if it's pure reverse and global setting is 0
                edge_mo.set_opacity(current_opacity) # Apply this potentially adjusted opacity


            label_grp = self.edge_label_groups.get(edge_key)
            if label_grp: # For all labels (original and pure reverse)
                base_attrs_label = self.base_label_visual_attrs.get(edge_key)
                if base_attrs_label:
                    label_grp.set_opacity(base_attrs_label["opacity"])
                elif edge_key in self.original_edge_tuples: # Fallback for original
                    label_grp.set_opacity(1.0)
                else: # Fallback for pure reverse
                    label_grp.set_opacity(0.0)


        # Set reference height for flow/residual capacity text after scaling
        sample_text_mobj = None
        for key in self.original_edge_tuples: # Find a sample original flow text mobject
            if key in self.edge_flow_val_text_mobjects and self.edge_flow_val_text_mobjects[key] is not None:
                sample_text_mobj = self.edge_flow_val_text_mobjects[key]
                break
        if sample_text_mobj:
            self.scaled_flow_text_height = sample_text_mobj.height # Height after scaling
        else: # Fallback if no original edges (unlikely for this graph)
            dummy_text_unscaled = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            # Scale it notionally as it would have been in the group
            self.scaled_flow_text_height = dummy_text_unscaled.scale(self.desired_large_scale).height


        # Store base visual attributes for nodes (color, size, etc.) AFTER scaling
        self.base_node_visual_attrs = {}
        for v_id, node_group in self.node_mobjects.items():
            dot, label = node_group # Assuming VGroup(Dot, Text)
            self.base_node_visual_attrs[v_id] = {
                "width": dot.width, # Scaled width
                "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(),
                "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity(),
                "label_color": label.get_color()
            }

        # Indicate Source and Sink nodes
        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]

        # Temporary rings for S and T indication
        temp_source_ring = Circle(
            radius=source_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH
        ).move_to(source_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        temp_sink_ring = Circle(
            radius=sink_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH
        ).move_to(sink_node_dot.get_center()).set_z_index(RING_Z_INDEX)

        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        self.play(
            Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7),
            Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7),
        )
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)

        # Change S and T labels from numbers to 's' and 't'
        source_label_original = self.node_mobjects[self.source_node][1]
        sink_label_original = self.node_mobjects[self.sink_node][1]

        new_s_label_mobj = Text("s", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, color=self.base_node_visual_attrs[self.source_node]["label_color"]
                                ).move_to(source_label_original.get_center()).set_z_index(source_label_original.z_index)
        new_t_label_mobj = Text("t", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, color=self.base_node_visual_attrs[self.sink_node]["label_color"]
                                ).move_to(sink_label_original.get_center()).set_z_index(sink_label_original.z_index)
        self.play(
            Transform(source_label_original, new_s_label_mobj),
            Transform(sink_label_original, new_t_label_mobj),
            run_time=0.5
        )
        # Update the mobjects in storage
        self.node_mobjects[self.source_node][1] = new_s_label_mobj
        self.node_mobjects[self.sink_node][1] = new_t_label_mobj
        self.wait(0.5)


        # --- Dinitz Algorithm Start ---
        self.update_section_title("2. Running Dinitz's Algorithm", play_anim=True)
        self.wait(1.0)

        while True: # Main Dinitz loop (Phases)
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Step 1 - Build Level Graph (LG)", color=BLUE_B, play_anim=True)
            
            # <<< MODIFICATION 1: Ensure sink action text is empty for Level Graph (BFS) part >>>
            self._update_sink_action_text("", animate=False) 
            
            self.wait(1.0) # Time to read phase title
            self.update_status_text(f"BFS from S (Node {self.source_node}) to define node levels (shortest dist. from S).", play_anim=True)
            self.wait(3.0) # Time to read status

            # BFS to build level graph
            self.levels = {v_id: -1 for v_id in self.vertices_data} # Reset levels
            q_bfs = collections.deque()

            self.levels[self.source_node] = 0; q_bfs.append(self.source_node)

            # Clear and prepare level display VGroup on the side
            if self.level_display_vgroup.submobjects: # If it has previous content
                self.play(FadeOut(self.level_display_vgroup)) # Fade out old level display
                self.level_display_vgroup.remove(*self.level_display_vgroup.submobjects) # Clear its content

            l_p0 = Text(f"L0:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
            l_n0_text = f" {{s ({self.source_node})}}" # Display 's' and original ID
            l_n0 = Text(l_n0_text, font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
            first_level_text_group = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL)
            self.level_display_vgroup.add(first_level_text_group)
            self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
            self.play(Write(first_level_text_group)); self.wait(1.0)
            max_level_text_width = config.frame_width * 0.30 # Max width for level display VGroup

            # Restore all nodes and edges to their base appearance before highlighting LG
            restore_anims = []
            for v_id, node_group in self.node_mobjects.items():
                dot, lbl = node_group
                node_attrs = self.base_node_visual_attrs[v_id]
                restore_anims.append(
                    dot.animate.set_width(node_attrs["width"]).set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"]).set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"])
                )
                # Restore label color, special handling for s,t if their base color was different due to 's'/'t' text
                if v_id != self.source_node and v_id != self.sink_node:
                     restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))
                elif v_id == self.source_node or v_id == self.sink_node: # 's' and 't' labels
                     restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))


            for edge_key, edge_mo in self.edge_mobjects.items():
                edge_attrs = self.base_edge_visual_attrs[edge_key]
                current_opacity = edge_attrs["opacity"]
                # Special handling for pure reverse edges if they are meant to be fully hidden by default
                if edge_key not in self.original_edge_tuples and REVERSE_EDGE_OPACITY == 0.0:
                    current_opacity = 0.0
                restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"]).set_stroke(width=edge_attrs["stroke_width"], opacity=current_opacity))

                # Restore labels associated with edges
                label_grp = self.edge_label_groups.get(edge_key)
                if label_grp and label_grp.submobjects: # Check if group exists and has content
                    base_label_attr = self.base_label_visual_attrs.get(edge_key)
                    base_opacity_for_label = 0.0 # Default to hidden if no info
                    if base_label_attr:
                        base_opacity_for_label = base_label_attr.get("opacity", 0.0)
                    elif edge_key in self.original_edge_tuples: # Fallback for original edge labels
                         base_opacity_for_label = 1.0

                    restore_anims.append(label_grp.animate.set_opacity(base_opacity_for_label))
                    # If label is visible and it's an original edge, ensure text color is restored
                    if base_opacity_for_label > 0 and edge_key in self.original_edge_tuples:
                        for part in label_grp.submobjects: # Iterate through flow, slash, capacity
                            if isinstance(part, Text): # Ensure it's a Text mobject
                                restore_anims.append(part.animate.set_color(LABEL_TEXT_COLOR))


            if restore_anims: self.play(AnimationGroup(*restore_anims, lag_ratio=0.01), run_time=0.75)
            self.wait(0.5)

            # Highlight source node for BFS start
            s_dot_obj, s_lbl_obj = self.node_mobjects[self.source_node]
            self.play(
                s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(self.base_node_visual_attrs[self.source_node]["width"] * 1.1), # Slightly larger
                s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE) # Contrast label
            )
            self.wait(0.5)

            # BFS loop
            while q_bfs:
                nodes_this_level = list(q_bfs); q_bfs.clear() # Process all nodes at current level
                if not nodes_this_level: break # Should not happen if q_bfs was not empty

                next_level_idx = self.levels[nodes_this_level[0]] + 1
                nodes_found_next_level_set = set() # Nodes found for the next level
                bfs_anims_this_step = [] # Animations for this step of BFS

                for u_bfs in nodes_this_level:
                    u_bfs_display_name = "s" if u_bfs == self.source_node else "t" if u_bfs == self.sink_node else str(u_bfs)
                    self.update_status_text(f"BFS: Exploring from L{self.levels[u_bfs]} node {u_bfs_display_name}...", play_anim=False) # No animation for rapid updates
                    self.wait(0.8) # Time to read status
                    ind_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW_C, buff=0.03, stroke_width=2.0, corner_radius=0.05)
                    self.play(Create(ind_u), run_time=0.20)

                    # Iterate through neighbors in a defined order for consistency
                    sorted_neighbors_bfs = sorted(self.adj[u_bfs]) # adj[u_bfs] has all potential neighbors

                    for v_n_bfs in sorted_neighbors_bfs:
                        edge_key_bfs = (u_bfs, v_n_bfs)
                        res_cap_bfs = self.capacities.get(edge_key_bfs,0) - self.flow.get(edge_key_bfs,0)
                        edge_mo_bfs = self.edge_mobjects.get(edge_key_bfs)

                        if edge_mo_bfs and res_cap_bfs > 0 and self.levels[v_n_bfs] == -1: # Valid edge to unvisited node
                            self.levels[v_n_bfs] = next_level_idx
                            nodes_found_next_level_set.add(v_n_bfs); q_bfs.append(v_n_bfs)

                            # Animate node v_n_bfs being reached and edge (u_bfs, v_n_bfs) being part of LG
                            lvl_color_v = LEVEL_COLORS[next_level_idx % len(LEVEL_COLORS)]
                            n_v_dot, n_v_lbl = self.node_mobjects[v_n_bfs]
                            bfs_anims_this_step.extend([
                                n_v_dot.animate.set_fill(lvl_color_v).set_width(self.base_node_visual_attrs[v_n_bfs]["width"] * 1.1), # Slightly larger
                                n_v_lbl.animate.set_color(BLACK if sum(color_to_rgb(lvl_color_v)) > 1.5 else WHITE) # Contrast label
                            ])
                            # Edge (u,v) in LG gets color of level u
                            edge_color_u_for_lg = LEVEL_COLORS[self.levels[u_bfs] % len(LEVEL_COLORS)]
                            bfs_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_u_for_lg).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))

                            # If it's a pure residual edge, update its capacity label
                            if edge_key_bfs not in self.original_edge_tuples:
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get(edge_key_bfs)
                                if res_cap_mobj:
                                    target_text = Text(f"{res_cap_bfs:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=edge_color_u_for_lg)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                        target_text.height = self.scaled_flow_text_height * 0.9 # Match other res cap texts
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0) # Make visible
                                    bfs_anims_this_step.append(res_cap_mobj.animate.become(target_text))
                            else: # Original edge, ensure its label is fully opaque and standard color
                                label_grp_bfs = self.edge_label_groups.get(edge_key_bfs)
                                if label_grp_bfs: # Ensure full opacity and standard text color for parts
                                    for part in label_grp_bfs.submobjects:
                                        if isinstance(part, Text): # Only color text parts
                                            bfs_anims_this_step.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                                        else: # Other parts of group (if any)
                                            bfs_anims_this_step.append(part.animate.set_opacity(1.0))


                    self.play(FadeOut(ind_u), run_time=0.20) # Remove highlight from u_bfs

                if bfs_anims_this_step: self.play(AnimationGroup(*bfs_anims_this_step, lag_ratio=0.1), run_time=0.8); self.wait(0.5)

                # Update level display on the side
                if nodes_found_next_level_set:
                    def get_node_display_name(n_id): # Helper for s/t names
                        if n_id == self.source_node: return f"s ({n_id})"
                        if n_id == self.sink_node: return f"t ({n_id})"
                        return str(n_id)
                    n_str_list = [get_node_display_name(n) for n in sorted(list(nodes_found_next_level_set))]
                    n_str = ", ".join(n_str_list)

                    self.update_status_text(f"BFS: L{next_level_idx} nodes found: {{{n_str}}}", play_anim=False) # Update status
                    self.wait(0.5) # Time to read
                    l_px = Text(f"L{next_level_idx}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[next_level_idx%len(LEVEL_COLORS)])
                    l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE) # Node list
                    new_level_text_entry = VGroup(l_px,l_nx).arrange(RIGHT,buff=BUFF_VERY_SMALL)
                    self.level_display_vgroup.add(new_level_text_entry)
                    # Rearrange and potentially scale if too wide
                    self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                    if self.level_display_vgroup.width > max_level_text_width:
                        self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                    self.play(Write(new_level_text_entry)); self.wait(1.5) # Show new level info

                if not q_bfs: break # No more nodes to explore in BFS

            # BFS completed for this phase
            sink_display_name = "t" # if self.sink_node == self.sink_node else str(self.sink_node) - already 't'
            if self.levels[self.sink_node] == -1: # Sink not reached
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) not reached by BFS. No more augmenting paths.", color=RED_C, play_anim=True)
                self.wait(3.0)
                self.update_max_flow_display(play_anim=True) # Show final flow
                self.update_phase_text(f"End of Dinitz. Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.update_status_text(f"Algorithm Terminates. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
                self._update_sink_action_text("", animate=False) # Ensure clear on termination
                self.wait(4.5)
                break # End Dinitz algorithm
            else: # Sink reached, proceed to DFS for blocking flow
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) at L{self.levels[self.sink_node]}. Level Graph layers established.", color=GREEN_A, play_anim=True); self.wait(3.0)

                # Isolate Level Graph visually: dim non-LG edges, highlight LG edges
                latex_status_string = r"\mbox{Isolating LG: Edges $(u,v)$ where $level(v)=level(u)+1$ \& residual capacity $>0$.}"
                self.update_status_text(latex_status_string, play_anim=True, is_latex=True)
                self.wait(1.0) # Time to read LaTeX

                lg_iso_anims = []
                for (u_lg,v_lg), edge_mo_lg in self.edge_mobjects.items():
                    res_cap_lg_val = self.capacities.get((u_lg,v_lg),0)-self.flow.get((u_lg,v_lg),0)
                    is_lg_edge = (self.levels.get(u_lg,-1)!=-1 and self.levels.get(v_lg,-1)!=-1 and \
                                  self.levels[v_lg]==self.levels[u_lg]+1 and res_cap_lg_val > 0)

                    label_grp_lg = self.edge_label_groups.get((u_lg,v_lg))

                    if is_lg_edge:
                        lg_color = LEVEL_COLORS[self.levels[u_lg]%len(LEVEL_COLORS)] # Color based on source level of edge
                        lg_iso_anims.append(edge_mo_lg.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(lg_color))
                        # Update label for this LG edge
                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples: # Pure residual edge in LG
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get((u_lg,v_lg))
                                if res_cap_mobj: # Update its text and color
                                    target_text = Text(f"{res_cap_lg_val:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=lg_color)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                        target_text.height = self.scaled_flow_text_height * 0.9
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                    lg_iso_anims.append(res_cap_mobj.animate.become(target_text))
                            else: # Original edge in LG, ensure its label parts are opaque and standard color
                                for part in label_grp_lg.submobjects:
                                    if isinstance(part, Text):
                                        lg_iso_anims.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                                    else: # Non-text parts
                                        lg_iso_anims.append(part.animate.set_opacity(1.0))
                    else: # Not an LG edge, dim it
                        base_edge_attrs_local = self.base_edge_visual_attrs.get((u_lg,v_lg), {})
                        target_opacity = DIMMED_OPACITY
                        target_color = DIMMED_COLOR
                        target_width = base_edge_attrs_local.get("stroke_width", EDGE_STROKE_WIDTH) # Use its base width

                        # Special handling for pure reverse edges that might be meant to be fully hidden
                        if (u_lg,v_lg) not in self.original_edge_tuples: # Pure reverse edge
                            current_base_opacity = base_edge_attrs_local.get("opacity", REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0)
                            if REVERSE_EDGE_OPACITY == 0.0 and (u_lg,v_lg) not in self.original_edge_tuples :
                                target_opacity = 0.0 # Make it completely invisible
                            else: # Use its default reverse opacity or dimmed if that's more opaque
                                target_opacity = min(current_base_opacity, DIMMED_OPACITY) if current_base_opacity > 0 else DIMMED_OPACITY
                            target_color = base_edge_attrs_local.get("color", REVERSE_EDGE_COLOR) # Use its base color

                        lg_iso_anims.append(edge_mo_lg.animate.set_stroke(opacity=target_opacity, color=target_color, width=target_width))

                        # Dim or hide labels of non-LG edges
                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples: # Pure residual edge label
                                lg_iso_anims.append(label_grp_lg.animate.set_opacity(0.0)) # Hide completely
                            else: # Original edge label
                                for part in label_grp_lg.submobjects: lg_iso_anims.append(part.animate.set_opacity(DIMMED_OPACITY))


                if lg_iso_anims: self.play(AnimationGroup(*lg_iso_anims, lag_ratio=0.05), run_time=1.0)
                self.wait(2.0) # View isolated LG
                self.update_status_text("Level Graph isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True); self.wait(2.5)

                # Step 2: Find Blocking Flow using DFS on LG
                flow_this_phase = self.animate_dfs_path_finding_phase() # This will handle its own sink_action_text internally

                # <<< MODIFICATION 2: Ensure sink action text is empty for "End of Phase" message >>>
                self._update_sink_action_text("", animate=False) 

                self.update_phase_text(f"End of Phase {self.current_phase_num}. Blocking Flow: {flow_this_phase:.1f}. Sink Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.wait(3.5) # Time to read end of phase summary
                if self.levels.get(self.sink_node, -1) != -1 : # If sink was reachable (i.e., algo not terminated)
                    self.update_status_text(f"Phase complete. Preparing for next phase.", color=BLUE_A, play_anim=True)
                    self.wait(3.0) # Pause before starting next phase or terminating

        # Dinitz algorithm loop has finished (either sink unreachable or break)
        self.update_section_title("3. Dinitz Algorithm Summary", play_anim=True)
        self.wait(1.0)

        # Final status message
        if self.levels.get(self.sink_node, -1) == -1 : # Check the condition that caused termination
            self.update_status_text(f"Algorithm Concluded. Sink Unreachable. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
        else: # Should only happen if loop broke for other reasons, but typically means sink was found in last phase.
            self.update_status_text(f"Algorithm Concluded. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)

        self.wait(5.0) # Long pause to see final state

        # Clean up scene, leaving titles and final status
        mobjects_that_should_remain_on_screen = Group(
            self.main_title,
            self.info_texts_group # This group contains section_title, phase_text, algo_status, max_flow_display
        )
        # Ensure no non-Mobject types are in the group if accidentally added
        mobjects_that_should_remain_on_screen.remove(*[m for m in mobjects_that_should_remain_on_screen if not isinstance(m, Mobject)])


        final_mobjects_to_fade_out = Group()
        # Collect all mobjects that are part of the "kept" mobjects or their children
        all_descendants_of_kept_mobjects = set()
        for mobj_to_keep in mobjects_that_should_remain_on_screen:
            all_descendants_of_kept_mobjects.update(mobj_to_keep.get_family()) # get_family includes self and children


        # Iterate over all mobjects currently on the scene
        for mobj_on_scene in list(self.mobjects): # list() to copy, as self.mobjects might change during iteration if FadeOut removes
            if mobj_on_scene not in all_descendants_of_kept_mobjects:
                final_mobjects_to_fade_out.add(mobj_on_scene)

        if final_mobjects_to_fade_out.submobjects: # If there's anything to fade
            self.play(FadeOut(final_mobjects_to_fade_out, run_time=1.0))

        self.wait(6) # Final pause before scene ends