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
PHASE_TEXT_FONT_SIZE = 22    # For text below section title
STATUS_TEXT_FONT_SIZE = 20   # For text below phase title
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
        # Initial write animation for main title can be done after all setup if preferred, or here.
        # For now, keeping original behavior:
        # self.play(Write(self.main_title), run_time=1)
        # self.wait(1.5)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.max_flow_display_mobj = Text("", font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)


        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj,
            self.max_flow_display_mobj # Added new display here
        ).arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        self.add(self.info_texts_group)

        self.level_display_vgroup = VGroup().set_z_index(10).to_corner(UR, buff=BUFF_LARGE)
        self.add(self.level_display_vgroup)

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        old_text_had_actual_content = isinstance(old_mobj, Text) and old_mobj.text != ""
        out_animation, in_animation = None, None
        if old_text_had_actual_content: out_animation = FadeOut(old_mobj, run_time=0.35)
        if new_text_content_str != "": in_animation = FadeIn(new_mobj, run_time=0.35, shift=ORIGIN)
        animations = [anim for anim in [out_animation, in_animation] if anim]
        if animations: self.play(*animations)

    def _update_text_generic(self, text_attr_name, new_text_str, font_size, weight, color, play_anim=True):
        old_mobj = getattr(self, text_attr_name)
        new_mobj = Text(new_text_str, font_size=font_size, weight=weight, color=color)

        if old_mobj in self.info_texts_group.submobjects:
            new_mobj.move_to(old_mobj.get_center())
        try:
            idx = self.info_texts_group.submobjects.index(old_mobj)
            self.info_texts_group.remove(old_mobj)
            self.info_texts_group.insert(idx, new_mobj)
        except ValueError:
            if old_mobj in self.mobjects: self.remove(old_mobj)

        setattr(self, text_attr_name, new_mobj)
        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') else 10)


        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_str)
        else:
            is_new_mobj_in_group = new_mobj in self.info_texts_group.submobjects
            if not is_new_mobj_in_group: # Should not happen for texts in info_texts_group
                if new_text_str != "" and new_mobj not in self.mobjects: self.add(new_mobj)
                elif new_text_str == "" and new_mobj in self.mobjects: self.remove(new_mobj)


    def update_section_title(self, text_str, play_anim=True):
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim)

    def update_max_flow_display(self, play_anim=True):
        new_text_str = f"Current Max Flow: {self.max_flow_value:.1f}"
        # Use _update_text_generic for consistency
        self._update_text_generic("max_flow_display_mobj", new_text_str, MAX_FLOW_DISPLAY_FONT_SIZE, BOLD, GREEN_C, play_anim)


    def _dfs_recursive_find_path_anim(self, u, pushed, current_path_info_list):
        u_dot_group = self.node_mobjects[u]
        u_dot = u_dot_group[0]

        highlight_ring = Circle(radius=u_dot.width/2 * 1.3, color=PINK, stroke_width=RING_STROKE_WIDTH * 0.7) \
            .move_to(u_dot.get_center()).set_z_index(u_dot.z_index + 2)
        self.dfs_traversal_highlights.add(highlight_ring)
        self.play(Create(highlight_ring), run_time=0.3)
        self.wait(0.5)

        if u == self.sink_node:
            self.update_status_text(f"DFS Path to Sink T={self.sink_node} found!", color=GREEN_B, play_anim=False)
            self.wait(2.0)
            self.play(FadeOut(highlight_ring), run_time=0.15)
            if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
            return pushed

        self.update_status_text(f"DFS Advance: From {u}, exploring valid LG edges.", play_anim=False)
        self.wait(1.5)

        while self.ptr[u] < len(self.adj[u]):
            v_candidate = self.adj[u][self.ptr[u]]
            edge_key_uv = (u, v_candidate)

            res_cap_cand = self.capacities.get(edge_key_uv, 0) - self.flow.get(edge_key_uv, 0)
            edge_mo_cand = self.edge_mobjects.get(edge_key_uv)

            is_valid_lg_edge = (edge_mo_cand and
                                self.levels.get(v_candidate, -1) == self.levels.get(u, -1) + 1 and
                                res_cap_cand > 0)

            if is_valid_lg_edge:
                actual_v = v_candidate
                edge_mo_for_v = edge_mo_cand

                original_edge_color = edge_mo_for_v.get_color()
                original_edge_width = edge_mo_for_v.get_stroke_width()
                original_edge_opacity = edge_mo_for_v.get_stroke_opacity()

                current_anims_try = [
                    edge_mo_for_v.animate.set_color(YELLOW_A).set_stroke(width=DFS_EDGE_TRY_WIDTH, opacity=1.0)
                ]
                if edge_key_uv not in self.original_edge_tuples:
                    label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                    if label_mobj:
                        target_label = Text(f"{res_cap_cand:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=YELLOW_A)
                        target_label.move_to(label_mobj.get_center()).set_opacity(1.0)
                        if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label.set_height(self.scaled_flow_text_height * 0.9)
                        current_anims_try.append(label_mobj.animate.become(target_label))

                self.update_status_text(f"DFS Try: Edge ({u},{actual_v}), Res.Cap: {res_cap_cand:.0f}.", play_anim=False)
                self.wait(1.5)
                if current_anims_try: self.play(*current_anims_try, run_time=0.4)
                self.wait(0.5)

                tr = self._dfs_recursive_find_path_anim(actual_v, min(pushed, res_cap_cand), current_path_info_list)

                current_anims_backtrack_restore = []
                if tr > 0:
                    self.update_status_text(f"DFS Path Segment: ({u},{actual_v}) is part of an s-t path.", color=GREEN_C, play_anim=False)
                    self.wait(1.5)
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v, original_edge_color, original_edge_width, original_edge_opacity))
                    self.play(FadeOut(highlight_ring), run_time=0.15)
                    if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr

                self.update_status_text(f"DFS Retreat: Edge ({u},{actual_v}) is a dead end. Backtracking.", color=YELLOW_C, play_anim=False)
                self.wait(1.5)
                current_anims_backtrack_restore.append(
                    edge_mo_for_v.animate.set_color(original_edge_color).set_stroke(width=original_edge_width, opacity=original_edge_opacity)
                )
                if edge_key_uv not in self.original_edge_tuples:
                    label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                    if label_mobj:
                        is_still_lg_edge_after_fail = (self.levels.get(actual_v, -1) == self.levels.get(u, -1) + 1 and res_cap_cand > 0)
                        if is_still_lg_edge_after_fail:
                             lg_color = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                             target_label_revert = Text(f"{res_cap_cand:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=lg_color)
                             target_label_revert.move_to(label_mobj.get_center()).set_opacity(1.0)
                             if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_revert.set_height(self.scaled_flow_text_height * 0.9)
                             current_anims_backtrack_restore.append(label_mobj.animate.become(target_label_revert))
                        else:
                             current_anims_backtrack_restore.append(label_mobj.animate.set_opacity(0.0))

                if current_anims_backtrack_restore: self.play(*current_anims_backtrack_restore, run_time=0.4)
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.0, run_time=0.45))
                self.wait(0.5)
                self.update_status_text(f"DFS Advance: From {u}, exploring next valid LG edge.", play_anim=False)
                self.wait(1.0)

            self.ptr[u] += 1

        self.update_status_text(f"DFS Retreat: All LG edges from {u} explored. Backtracking from {u}.", color=ORANGE, play_anim=False)
        self.wait(2.0)
        self.play(FadeOut(highlight_ring), run_time=0.15)
        if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
        return 0

    def animate_dfs_path_finding_phase(self):
        self.ptr = {v_id: 0 for v_id in self.vertices_data}
        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1)
        self.add(self.dfs_traversal_highlights)

        self.update_phase_text(f"Phase {self.current_phase_num}: Step 2 - Find Blocking Flow in LG (DFS)", color=ORANGE)
        self.update_status_text("DFS searches for s-t paths in LG to create a blocking flow.", play_anim=True)
        self.wait(3.0)

        while True:
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Seeking s->t path in LG from S={self.source_node}.", play_anim=True)
            self.wait(1.5)
            current_path_anim_info = []
            bottleneck_flow = self._dfs_recursive_find_path_anim(self.source_node, float('inf'), current_path_anim_info)

            if bottleneck_flow == 0:
                self.update_status_text("No more s-t paths in LG. Blocking flow for this phase is complete.", color=YELLOW_C, play_anim=True)
                self.wait(3.5)
                break

            total_flow_this_phase += bottleneck_flow
            # Max flow is updated after the entire phase in the main loop,
            # but we can update the display incrementally if desired or just at phase end.
            # For now, update global max_flow_value at the end of phase.

            # --- Bottleneck Edge Indication ---
            bottleneck_indicator_anims = []
            bottleneck_edges_for_indication = []
            current_path_anim_info.reverse() # Path is built backwards from sink

            for (u_path, v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                edge_key = (u_path, v_path)
                # Residual capacity BEFORE this specific path's augmentation
                res_cap_before_aug = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                if abs(res_cap_before_aug - bottleneck_flow) < 0.01: # Tolerance for float comparison
                    bottleneck_edges_for_indication.append(edge_mo_path)
            
            if bottleneck_edges_for_indication:
                self.update_status_text(f"Path #{path_count_this_phase} found. Bottleneck: {bottleneck_flow:.1f}. Identifying bottleneck edges...", color=YELLOW_A, play_anim=True) # play_anim=True
                self.wait(1.0) # Reduced wait before indication

                flash_anims = [
                    Indicate(edge_mo, color=BOTTLENECK_EDGE_INDICATE_COLOR, scale_factor=1.05, rate_func=there_and_back_with_pause, run_time=1.2)
                    for edge_mo in bottleneck_edges_for_indication
                ]
                if flash_anims:
                    self.play(AnimationGroup(*flash_anims, lag_ratio=0.05))
                    self.wait(0.75) # Wait after bottleneck indication
            # --- End Bottleneck Edge Indication ---


            self.update_status_text(f"Path #{path_count_this_phase} found. Bottleneck: {bottleneck_flow:.1f}. Augmenting...", color=GREEN_A, play_anim=True) # play_anim=True
            self.wait(2.5)

            path_highlight_anims = []
            # current_path_anim_info was already reversed above for bottleneck check
            for (u_path, v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                path_highlight_anims.append(edge_mo_path.animate.set_color(GREEN_D).set_stroke(width=DFS_PATH_EDGE_WIDTH, opacity=1.0))
                edge_key_path = (u_path, v_path)
                if edge_key_path not in self.original_edge_tuples:
                    label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_path)
                    if label_mobj:
                        res_cap_val = self.capacities.get(edge_key_path,0) - self.flow.get(edge_key_path,0) # Before this path's flow
                        # This label should reflect capacity *after* this path's flow conceptually for the green path
                        # However, the actual res_cap isn't updated until flow is updated.
                        # For simplicity, let's show the residual capacity *that was used* by this path from this edge
                        # Or, more simply, just highlight the edge. The text update will happen after flow update.
                        # Let's stick to the original label update behavior, which updates after flow values change.
                        # The green highlight on the label should occur when the main flow values are animated.
                        pass # Label update for residual edges handled in augmentation block

            if path_highlight_anims: self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.15, run_time=1.0))
            self.wait(2.0)

            augmentation_anims = []
            text_update_anims = []

            for (u,v), edge_mo, _, _, _ in current_path_anim_info:
                self.flow[(u,v)] = self.flow.get((u,v), 0) + bottleneck_flow
                self.flow[(v,u)] = self.flow.get((v,u), 0) - bottleneck_flow

                if (u,v) in self.original_edge_tuples:
                    old_flow_text_mobj = self.edge_flow_val_text_mobjects[(u,v)]
                    new_flow_val_uv = self.flow[(u,v)]
                    new_flow_str_uv = f"{new_flow_val_uv:.0f}" if abs(new_flow_val_uv - round(new_flow_val_uv)) < 0.01 else f"{new_flow_val_uv:.1f}"
                    target_text_template_uv = Text(new_flow_str_uv, font=old_flow_text_mobj.font, font_size=old_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_text_template_uv.set_height(self.scaled_flow_text_height)
                    else: target_text_template_uv.match_height(old_flow_text_mobj)
                    target_text_template_uv.move_to(old_flow_text_mobj.get_center()).rotate(edge_mo.get_angle(), about_point=target_text_template_uv.get_center())
                    text_update_anims.append(old_flow_text_mobj.animate.become(target_text_template_uv))

                res_cap_after_uv = self.capacities.get((u,v),0) - self.flow.get((u,v),0)
                is_still_lg_edge_uv = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                                    self.levels[v]==self.levels[u]+1 and res_cap_after_uv > 0 )

                if not is_still_lg_edge_uv:
                    augmentation_anims.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR, width=EDGE_STROKE_WIDTH))
                    if (u,v) not in self.original_edge_tuples:
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv: augmentation_anims.append(label_mobj_uv.animate.set_opacity(0.0))
                else: # Still part of LG
                    lg_color_uv = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                    # Keep it highlighted as part of LG, but it was green from path, now revert to LG color
                    augmentation_anims.append(edge_mo.animate.set_color(lg_color_uv).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))
                    if (u,v) not in self.original_edge_tuples:
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv:
                            target_label_uv = Text(f"{res_cap_after_uv:.0f}", font=label_mobj_uv.font, font_size=label_mobj_uv.font_size, color=lg_color_uv)
                            target_label_uv.move_to(label_mobj_uv.get_center()).set_opacity(1.0)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_uv.set_height(self.scaled_flow_text_height * 0.9)
                            augmentation_anims.append(label_mobj_uv.animate.become(target_label_uv))


                if (v,u) in self.edge_mobjects: # Handle reverse edge
                    rev_edge_mo_vu = self.edge_mobjects[(v,u)]
                    res_cap_vu = self.capacities.get((v,u),0) - self.flow[(v,u)] # Flow on (v,u) is -bottleneck_flow
                    is_rev_edge_in_lg_vu = (self.levels.get(v,-1)!=-1 and self.levels.get(u,-1)!=-1 and \
                                         self.levels[u]==self.levels[v]+1 and res_cap_vu > 0)

                    if is_rev_edge_in_lg_vu: # Reverse edge (v,u) becomes part of LG
                        lg_color_vu = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(lg_color_vu))
                    elif res_cap_vu > 0 : # Not in LG, but has capacity (e.g. original edge or just a residual edge)
                        base_attrs_vu_edge = self.base_edge_visual_attrs.get((v,u),{})
                        opacity_vu = 0.7 if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("opacity", REVERSE_EDGE_OPACITY)
                        color_vu = GREY_A if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("color", REVERSE_EDGE_COLOR)
                        width_vu = EDGE_STROKE_WIDTH if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("stroke_width", EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR)
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=opacity_vu, width=width_vu, color=color_vu))
                    else: # No residual capacity
                        base_attrs_vu_edge = self.base_edge_visual_attrs.get((v,u),{})
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=base_attrs_vu_edge.get("opacity",DIMMED_OPACITY), width=base_attrs_vu_edge.get("stroke_width",EDGE_STROKE_WIDTH), color=base_attrs_vu_edge.get("color",DIMMED_COLOR)))

                    # Handle labels for reverse edge (v,u)
                    if (v,u) not in self.original_edge_tuples: # Pure residual edge
                        label_mobj_vu = self.edge_residual_capacity_mobjects.get((v,u))
                        if label_mobj_vu:
                            if is_rev_edge_in_lg_vu:
                                lg_color_vu_label = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                                target_label_vu = Text(f"{res_cap_vu:.0f}", font=label_mobj_vu.font, font_size=label_mobj_vu.font_size, color=lg_color_vu_label)
                                target_label_vu.move_to(label_mobj_vu.get_center()).set_opacity(1.0)
                                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_vu.set_height(self.scaled_flow_text_height * 0.9)
                                augmentation_anims.append(label_mobj_vu.animate.become(target_label_vu))
                            else: # Not in LG, so residual label should be hidden
                                augmentation_anims.append(label_mobj_vu.animate.set_opacity(0.0))
                    else: # Original edge, update its flow/cap label
                        old_rev_flow_text_mobj = self.edge_flow_val_text_mobjects.get((v,u))
                        if old_rev_flow_text_mobj: # if it's an original edge with flow/cap display
                            new_rev_flow_val_vu = self.flow[(v,u)]
                            new_rev_flow_str_vu = f"{new_rev_flow_val_vu:.0f}" if abs(new_rev_flow_val_vu - round(new_rev_flow_val_vu)) < 0.01 else f"{new_rev_flow_val_vu:.1f}"
                            target_rev_text_template_vu = Text(new_rev_flow_str_vu, font=old_rev_flow_text_mobj.font, font_size=old_rev_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_rev_text_template_vu.set_height(self.scaled_flow_text_height)
                            else: target_rev_text_template_vu.match_height(old_rev_flow_text_mobj)
                            target_rev_text_template_vu.move_to(old_rev_flow_text_mobj.get_center()).rotate(rev_edge_mo_vu.get_angle(), about_point=target_rev_text_template_vu.get_center())
                            text_update_anims.append(old_rev_flow_text_mobj.animate.become(target_rev_text_template_vu))

                        # Adjust overall label group opacity for original reverse edges
                        rev_label_grp_vu = self.edge_label_groups.get((v,u))
                        if rev_label_grp_vu and rev_label_grp_vu.submobjects:
                            if is_rev_edge_in_lg_vu: # Part of LG, fully visible
                                for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                            elif res_cap_vu > 0: # Has capacity, but not LG, standard visibility
                                for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(0.7)) # Or original opacity
                            else: # No capacity, dim it
                                base_lbl_attrs = self.base_label_visual_attrs.get((v,u))
                                if base_lbl_attrs:
                                    for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(base_lbl_attrs.get("opacity", DIMMED_OPACITY)))


            if text_update_anims or augmentation_anims:
                 self.play(AnimationGroup(*(text_update_anims + augmentation_anims), lag_ratio=0.1), run_time=1.5)
            else: self.wait(0.1)
            self.wait(0.5)

            self.update_status_text(f"Flow augmented. Current phase flow: {total_flow_this_phase:.1f}. Searching next path...", color=WHITE, play_anim=True)
            self.wait(2.5)

        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
            # self.remove(self.dfs_traversal_highlights) # Optional: remove from scene mobjects after fade
        return total_flow_this_phase

    def construct(self):
        self.setup_titles_and_placeholders()
        # Animate main title write after other static elements are potentially added
        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.scaled_flow_text_height = None

        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11))
        self.edges_with_capacity_list = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        self.original_edge_tuples = set([(u,v) for u,v,c in self.edges_with_capacity_list])

        self.capacities = collections.defaultdict(int)
        self.flow = collections.defaultdict(int)
        self.adj = collections.defaultdict(list)

        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u) # For BFS/DFS structure

        self.graph_layout = {
            1: [-4,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }

        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {}
        self.edge_label_groups = {}
        self.base_label_visual_attrs = {}
        self.edge_residual_capacity_mobjects = {}

        self.desired_large_scale = 1.6
        self.update_section_title("1. Building the Flow Network", play_anim=False)
        self.update_status_text("Network: Nodes, Edges (Flow / Capacity). Initial flow is 0.", play_anim=False)
        
        self.current_phase_num = 0; self.max_flow_value = 0
        self.update_max_flow_display(play_anim=False) # Initialize max flow display

        nodes_vgroup = VGroup()
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        edges_vgroup = VGroup()
        edge_grow_anims = []
        for u,v,cap in self.edges_with_capacity_list:
            n_u_dot = self.node_mobjects[u][0]; n_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS, stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow; edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        all_edge_labels_vgroup = VGroup()
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []

        for u, v, cap in self.edges_with_capacity_list:
            arrow = self.edge_mobjects[(u,v)]
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)

            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u,v)] = cap_text_mobj
            self.base_label_visual_attrs[(u,v)] = {"opacity": 1.0}

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            label_group.move_to(arrow.get_center()).rotate(arrow.get_angle())
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.25 #Slightly more offset
            label_group.shift(offset_vector).set_z_index(1)
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))

        for u_node in self.vertices_data: # Create reverse edge mobjects (initially invisible or styled as such)
            for v_node in self.adj[u_node]:
                current_edge_tuple = (u_node, v_node)
                # Only create if it's not an original edge AND not already an edge mobject (e.g. if graph was undirected initially for adj)
                if current_edge_tuple not in self.original_edge_tuples and current_edge_tuple not in self.edge_mobjects:
                    n_u_dot = self.node_mobjects[u_node][0]; n_v_dot = self.node_mobjects[v_node][0]
                    rev_arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS,
                                      stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR,
                                      color=REVERSE_EDGE_COLOR,
                                      max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH * 0.8,
                                      z_index=REVERSE_EDGE_Z_INDEX)
                    rev_arrow.set_opacity(REVERSE_EDGE_OPACITY)
                    self.edge_mobjects[current_edge_tuple] = rev_arrow
                    edges_vgroup.add(rev_arrow) # Add to main edges VGroup

                    # Residual capacity label for this pure reverse edge (initially 0, invisible)
                    res_cap_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR, opacity=0.0) # Start with opacity 0
                    res_cap_val_mobj.move_to(rev_arrow.get_center()).rotate(rev_arrow.get_angle())
                    offset_vector_rev = rotate_vector(rev_arrow.get_unit_vector(), PI / 2) * 0.25
                    res_cap_val_mobj.shift(offset_vector_rev).set_z_index(1)

                    self.edge_residual_capacity_mobjects[current_edge_tuple] = res_cap_val_mobj
                    self.base_label_visual_attrs[current_edge_tuple] = {"opacity": 0.0} # Label starts invisible

                    pure_rev_label_group = VGroup(res_cap_val_mobj) # Group for this single label
                    self.edge_label_groups[current_edge_tuple] = pure_rev_label_group
                    all_edge_labels_vgroup.add(pure_rev_label_group)


        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)

        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        self.wait(0.5)

        sample_text_mobj = None
        for key in self.original_edge_tuples: # Find a sample flow text mobject to get its scaled height
            if key in self.edge_flow_val_text_mobjects and self.edge_flow_val_text_mobjects[key] is not None:
                sample_text_mobj = self.edge_flow_val_text_mobjects[key]
                break
        if sample_text_mobj:
            self.scaled_flow_text_height = sample_text_mobj.height # Already scaled with network_display_group
        else: # Fallback if no original edges (should not happen for this example)
            dummy_text_unscaled = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text_unscaled.scale(self.desired_large_scale).height


        self.base_node_visual_attrs = {}
        for v_id, node_group in self.node_mobjects.items():
            dot, label = node_group
            self.base_node_visual_attrs[v_id] = {"width": dot.get_width(), "fill_color": dot.get_fill_color(), "stroke_color": dot.get_stroke_color(), "stroke_width": dot.get_stroke_width(), "opacity": dot.get_fill_opacity(), "label_color": label.get_color()}

        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {"color": edge_mo.get_color(), "stroke_width": edge_mo.get_stroke_width(), "opacity": edge_mo.get_stroke_opacity()}
            if edge_key not in self.base_label_visual_attrs: # Ensure all edges have a base label attr
                 # Default for pure reverse edges (which are initially mostly transparent)
                 self.base_label_visual_attrs[edge_key] = {"opacity": 0.0}


        self.source_ring_mobj = Circle(radius=self.node_mobjects[self.source_node][0].width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(self.node_mobjects[self.source_node][0].get_center()).set_z_index(RING_Z_INDEX)
        self.sink_ring_mobj = Circle(radius=self.node_mobjects[self.sink_node][0].width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(self.node_mobjects[self.sink_node][0].get_center()).set_z_index(RING_Z_INDEX)
        self.play(Create(self.source_ring_mobj), Create(self.sink_ring_mobj))
        self.update_status_text("Source (S) and Sink (T) identified.", play_anim=True); self.wait(2.5)

        self.update_section_title("2. Running Dinitz's Algorithm", play_anim=True)
        self.wait(1.0)
        self.update_status_text("Dinitz's algorithm proceeds in phases to find max flow.", play_anim=True)
        self.wait(3.0)
        self.update_status_text("Each phase: 1. Build Level Graph (BFS), 2. Find Blocking Flow (DFS).", play_anim=True)
        self.wait(3.5)


        while True: # Main Dinitz Loop (Phases)
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Step 1 - Build Level Graph (LG)", color=BLUE_B, play_anim=True)
            self.wait(1.0)
            self.update_status_text(f"BFS from S={self.source_node} to define node levels (shortest dist. from S).", play_anim=True)
            self.wait(3.0)

            self.levels = {v_id: -1 for v_id in self.vertices_data}
            q_bfs = collections.deque()
            self.levels[self.source_node] = 0; q_bfs.append(self.source_node)

            if self.level_display_vgroup.submobjects: # Clear previous level display
                self.play(FadeOut(self.level_display_vgroup))
                self.level_display_vgroup.remove(*self.level_display_vgroup.submobjects) # Clear its content

            l_p0 = Text(f"L0:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
            l_n0 = Text(f" {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
            first_level_text_group = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL)
            self.level_display_vgroup.add(first_level_text_group) # Add to group
            self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE) # Rearrange and position
            self.play(Write(first_level_text_group)); self.wait(1.0)
            max_level_text_width = config.frame_width * 0.30

            # Restore graph to base state before building new level graph
            restore_anims = []
            for v_id, node_group in self.node_mobjects.items():
                dot, lbl = node_group
                node_attrs = self.base_node_visual_attrs[v_id]
                restore_anims.extend([
                    dot.animate.set_width(node_attrs["width"]).set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"]).set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"]),
                    lbl.animate.set_color(node_attrs["label_color"])])

            for edge_key, edge_mo in self.edge_mobjects.items():
                edge_attrs = self.base_edge_visual_attrs[edge_key]
                restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"]).set_stroke(width=edge_attrs["stroke_width"], opacity=edge_attrs["opacity"]))

                label_grp = self.edge_label_groups.get(edge_key)
                if label_grp and label_grp.submobjects:
                    base_label_attr = self.base_label_visual_attrs.get(edge_key, {"opacity": 0.0}) # Default to 0 if not found
                    base_opacity = base_label_attr.get("opacity", 1.0 if edge_key in self.original_edge_tuples else 0.0)

                    for part_idx, part in enumerate(label_grp.submobjects):
                        restore_anims.append(part.animate.set_opacity(base_opacity))
                        if base_opacity > 0: # If the label is supposed to be visible
                            if edge_key in self.original_edge_tuples: # Original edge labels go to default color
                                 if part is self.edge_flow_val_text_mobjects.get(edge_key) or \
                                    part is self.edge_slash_text_mobjects.get(edge_key) or \
                                    part is self.edge_capacity_text_mobjects.get(edge_key):
                                    restore_anims.append(part.animate.set_color(LABEL_TEXT_COLOR))
                            # For pure residual edges, their labels (if visible from base_opacity) keep their color or are handled by LG logic

            if restore_anims: self.play(AnimationGroup(*restore_anims, lag_ratio=0.01), run_time=0.75)
            self.wait(0.5)

            # Highlight source node for BFS start
            s_dot_obj, s_lbl_obj = self.node_mobjects[self.source_node]
            self.play(
                self.source_ring_mobj.animate.set_opacity(1), self.sink_ring_mobj.animate.set_opacity(1), # Ensure S/T rings are visible
                s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(self.base_node_visual_attrs[self.source_node]["width"] * 1.1),
                s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE) # Contrast label
            )
            self.wait(0.5)

            current_bfs_level_idx = 0
            while q_bfs:
                nodes_this_level = list(q_bfs); q_bfs.clear() # Get all nodes at current level
                if not nodes_this_level: break

                next_level_idx = self.levels[nodes_this_level[0]] + 1
                nodes_found_next_level_set = set()
                bfs_anims_this_step = []

                for u_bfs in nodes_this_level:
                    self.update_status_text(f"BFS: Exploring from L{self.levels[u_bfs]} node {u_bfs}...", play_anim=False)
                    self.wait(0.8)
                    ind_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW_C, buff=0.03, stroke_width=2.0, corner_radius=0.05)
                    self.play(Create(ind_u), run_time=0.20)

                    sorted_neighbors_bfs = sorted(self.adj[u_bfs]) # Process neighbors consistently

                    for v_n_bfs in sorted_neighbors_bfs:
                        edge_key_bfs = (u_bfs, v_n_bfs)
                        res_cap_bfs = self.capacities.get(edge_key_bfs,0) - self.flow.get(edge_key_bfs,0)
                        edge_mo_bfs = self.edge_mobjects.get(edge_key_bfs)

                        if edge_mo_bfs and res_cap_bfs > 0 and self.levels[v_n_bfs] == -1: # If valid edge to unvisited node
                            self.levels[v_n_bfs] = next_level_idx
                            nodes_found_next_level_set.add(v_n_bfs); q_bfs.append(v_n_bfs)

                            # Animate node discovery
                            lvl_color_v = LEVEL_COLORS[next_level_idx % len(LEVEL_COLORS)]
                            n_v_dot, n_v_lbl = self.node_mobjects[v_n_bfs]
                            bfs_anims_this_step.extend([
                                n_v_dot.animate.set_fill(lvl_color_v).set_width(self.base_node_visual_attrs[v_n_bfs]["width"] * 1.1),
                                n_v_lbl.animate.set_color(BLACK if sum(color_to_rgb(lvl_color_v)) > 1.5 else WHITE)
                            ])
                            # Animate edge inclusion in BFS tree (part of Level Graph)
                            edge_color_u_for_lg = LEVEL_COLORS[self.levels[u_bfs] % len(LEVEL_COLORS)] # Color by source level
                            bfs_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_u_for_lg).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))

                            # Animate label for this edge if it's a pure residual edge
                            label_grp_bfs = self.edge_label_groups.get(edge_key_bfs)
                            if label_grp_bfs and label_grp_bfs.submobjects:
                                if edge_key_bfs not in self.original_edge_tuples: # Pure residual edge
                                    res_cap_mobj = self.edge_residual_capacity_mobjects.get(edge_key_bfs) # Should be label_grp_bfs.submobjects[0]
                                    if res_cap_mobj:
                                        target_text = Text(f"{res_cap_bfs:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=edge_color_u_for_lg)
                                        if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_text.set_height(self.scaled_flow_text_height * 0.9)
                                        target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                        bfs_anims_this_step.append(res_cap_mobj.animate.become(target_text))
                                else: # Original edge, ensure its label is fully visible
                                    for part in label_grp_bfs.submobjects: bfs_anims_this_step.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))


                    self.play(FadeOut(ind_u), run_time=0.20)

                if bfs_anims_this_step: self.play(AnimationGroup(*bfs_anims_this_step, lag_ratio=0.1), run_time=0.8); self.wait(0.5)

                if nodes_found_next_level_set:
                    n_str = ", ".join(map(str, sorted(list(nodes_found_next_level_set))))
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

                current_bfs_level_idx = next_level_idx
                if not q_bfs: break # No more nodes to visit in queue

            # After BFS completes for this phase
            if self.levels[self.sink_node] == -1: # Sink not reached
                self.update_status_text(f"Sink T={self.sink_node} not reached by BFS. No more augmenting paths.", color=RED_C, play_anim=True)
                self.wait(3.0)
                self.update_max_flow_display(play_anim=True) # Show final flow
                self.update_phase_text(f"End of Dinitz. Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.update_status_text(f"Algorithm Terminates. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
                self.wait(4.5)
                break # Exit main Dinitz loop
            else: # Sink reached, proceed to isolate LG and DFS
                self.update_status_text(f"Sink T={self.sink_node} at L{self.levels[self.sink_node]}. Level Graph layers established.", color=GREEN_A, play_anim=True); self.wait(3.0)
                self.update_status_text(f"Isolating LG: Edges $(u,v)$ where $level(v)=level(u)+1$ & residual capacity $>0$.", play_anim=True)
                self.wait(1.0)
                lg_iso_anims = []
                # Dim non-LG edges, highlight LG edges
                for (u_lg,v_lg), edge_mo_lg in self.edge_mobjects.items():
                    res_cap_lg_val = self.capacities.get((u_lg,v_lg),0)-self.flow.get((u_lg,v_lg),0)
                    is_lg_edge = (self.levels.get(u_lg,-1)!=-1 and self.levels.get(v_lg,-1)!=-1 and \
                                  self.levels[v_lg]==self.levels[u_lg]+1 and res_cap_lg_val > 0)

                    label_grp_lg = self.edge_label_groups.get((u_lg,v_lg))

                    if is_lg_edge:
                        lg_color = LEVEL_COLORS[self.levels[u_lg]%len(LEVEL_COLORS)]
                        lg_iso_anims.append(edge_mo_lg.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(lg_color))
                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples: # Pure residual
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get((u_lg,v_lg))
                                if res_cap_mobj:
                                    target_text = Text(f"{res_cap_lg_val:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=lg_color)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_text.set_height(self.scaled_flow_text_height * 0.9)
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                    lg_iso_anims.append(res_cap_mobj.animate.become(target_text))
                            else: # Original edge, ensure label is full opacity and default color
                                for part in label_grp_lg.submobjects: lg_iso_anims.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                    else: # Not an LG edge, dim it
                        base_edge_attrs = self.base_edge_visual_attrs.get((u_lg,v_lg), {})
                        # Determine target style for non-LG edges
                        target_opacity = DIMMED_OPACITY
                        target_color = DIMMED_COLOR
                        target_width = base_edge_attrs.get("stroke_width", EDGE_STROKE_WIDTH) # Keep original width or a dimmed width

                        if (u_lg,v_lg) not in self.original_edge_tuples: # Pure residual, not in LG
                            target_opacity = base_edge_attrs.get("opacity", REVERSE_EDGE_OPACITY) # Its base opacity (likely very low)
                            target_color = base_edge_attrs.get("color", REVERSE_EDGE_COLOR)
                        
                        lg_iso_anims.append(edge_mo_lg.animate.set_stroke(opacity=target_opacity, color=target_color, width=target_width))

                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples: # Pure residual label
                                res_cap_mobj_lg = self.edge_residual_capacity_mobjects.get((u_lg,v_lg))
                                if res_cap_mobj_lg: lg_iso_anims.append(res_cap_mobj_lg.animate.set_opacity(0.0)) # Hide if not LG
                            else: # Original edge label, dim it
                                for part in label_grp_lg.submobjects: lg_iso_anims.append(part.animate.set_opacity(DIMMED_OPACITY))


                if lg_iso_anims: self.play(AnimationGroup(*lg_iso_anims, lag_ratio=0.05), run_time=1.0)
                self.wait(2.0)
                self.update_status_text("Level Graph isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True); self.wait(2.5)

                flow_this_phase = self.animate_dfs_path_finding_phase() # This function handles its own status updates
                self.max_flow_value += flow_this_phase
                self.update_max_flow_display(play_anim=True) # Update flow display after phase

                self.update_phase_text(f"End of Phase {self.current_phase_num}. Blocking Flow: {flow_this_phase:.1f}. Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.wait(3.5)
                # The loop condition (sink reached by BFS) will determine if another phase runs.
                # If sink was reached (self.levels[self.sink_node] != -1), loop continues. Otherwise, it will break at top.
                if self.levels[self.sink_node] != -1 :
                     self.update_status_text(f"Phase complete. Preparing for next phase.", color=BLUE_A, play_anim=True) #play_anim=True
                     self.wait(3.0)


        # Algorithm has terminated (either by break from BFS or after loop if condition changes)
        self.update_section_title("3. Dinitz Algorithm Summary", play_anim=True)
        self.wait(1.0)
        # Status text is already "Algorithm Terminates..." if BFS failed.
        # If it exited normally after phases, this is a good final summary.
        if self.levels[self.sink_node] != -1: # If last phase was productive but then BFS fails next
             self.update_status_text(f"Algorithm concluded. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
        # else: already handled by BFS fail message.
        # Ensure max flow display is final
        self.update_max_flow_display(play_anim=False) # Ensure it's up-to-date without animation
        self.wait(5.0)


        # --- Final Fade Out Logic ---
        # Define the mobjects that should absolutely remain on screen.
        final_top_level_mobjects_to_keep = VGroup( # VGroup is fine here as we are adding known VMobjects or other VGroups
            self.main_title,
            self.info_texts_group, 
            self.level_display_vgroup,
            self.network_display_group, 
            self.source_ring_mobj,
            self.sink_ring_mobj
        )
        final_top_level_mobjects_to_keep.remove(*[m for m in final_top_level_mobjects_to_keep if m is None])

        mobjects_to_fade_out_final = Group() # <--- Changed from VGroup to Group
        current_scene_mobjects = list(self.mobjects) 

        all_parts_of_kept_mobjects = set()
        for mobj in final_top_level_mobjects_to_keep:
            all_parts_of_kept_mobjects.update(mobj.get_family()) 

        for mobj_on_scene in current_scene_mobjects:
            if mobj_on_scene not in all_parts_of_kept_mobjects:
                mobjects_to_fade_out_final.add(mobj_on_scene)
        
        if hasattr(self, 'dfs_traversal_highlights') and self.dfs_traversal_highlights in current_scene_mobjects:
            if self.dfs_traversal_highlights not in all_parts_of_kept_mobjects:
                is_already_in_fade_list = False
                for sub_m in mobjects_to_fade_out_final.submobjects:
                    if sub_m == self.dfs_traversal_highlights:
                        is_already_in_fade_list = True
                        break
                if not is_already_in_fade_list:
                    mobjects_to_fade_out_final.add(self.dfs_traversal_highlights)

        if mobjects_to_fade_out_final.submobjects: 
            self.play(FadeOut(mobjects_to_fade_out_final, run_time=1.0))
        
        self.wait(6)