from manim import *
import collections
import numpy as np

# --- Style and Layout Constants ---
# ... (Your existing constants) ...
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.18

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 # For text below main title
PHASE_TEXT_FONT_SIZE = 22    # For text below phase title
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
            if old_mobj in self.mobjects and old_mobj.get_family_members_with_points() :
                 out_animation = FadeOut(old_mobj, run_time=0.35)


        animations = [anim for anim in [out_animation, in_animation] if anim]
        if animations: self.play(*animations)


    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False):
        old_mobj = getattr(self, text_attr_name)

        if is_latex:
            new_mobj = Tex(new_text_content, color=color)
            ref_text_for_height = Text("Mg", font_size=font_size)
            if ref_text_for_height.height > 0.001 and new_mobj.height > 0.001:
                 new_mobj.scale_to_fit_height(ref_text_for_height.height)
        else:
            new_mobj = Text(new_text_content, font_size=font_size, weight=weight, color=color)


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
        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') and old_mobj.z_index is not None else 10)


        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_content)
        else:
            is_empty_new_content = (isinstance(new_mobj, Text) and new_mobj.text == "") or \
                                 (isinstance(new_mobj, Tex) and new_mobj.tex_string == "")
            is_in_group = new_mobj in self.info_texts_group.submobjects

            if is_empty_new_content:
                if not is_in_group and new_mobj in self.mobjects:
                    self.remove(new_mobj)
            else:
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
            return

        target_text_template = Text(
            new_text_content,
            font_size=STATUS_TEXT_FONT_SIZE,
            weight=current_mobj.weight,
            color=new_color
        )

        # --- MODIFICATION START ---
        # Position the target_text_template relative to the sink node.
        # This ensures it's always "exactly above" the sink node upon update.
        if hasattr(self, 'node_mobjects') and \
           hasattr(self, 'sink_node') and \
           self.sink_node in self.node_mobjects and \
           self.node_mobjects.get(self.sink_node) is not None: # Check if sink_node key exists and its value is not None
            # Ensure that self.node_mobjects[self.sink_node] is a VGroup and has at least one element (the dot)
            sink_node_group = self.node_mobjects[self.sink_node]
            if isinstance(sink_node_group, VGroup) and len(sink_node_group.submobjects) > 0:
                sink_node_dot = sink_node_group[0]
                target_text_template.next_to(sink_node_dot, UP, buff=BUFF_SMALL)
            else:
                # Fallback: if sink_node_group is not as expected, position at current mobject's center.
                target_text_template.move_to(current_mobj.get_center())
        else:
            # Fallback: if sink node attributes/mobjects aren't ready, position at current mobject's center.
            target_text_template.move_to(current_mobj.get_center())
        
        # Preserve the Z-index
        target_text_template.set_z_index(current_mobj.z_index)
        # --- MODIFICATION END ---


        if animate:
            if old_text_content and not new_text_content: # Fading out
                self.play(FadeOut(current_mobj, run_time=0.25))
                current_mobj.become(target_text_template)
            elif not old_text_content and new_text_content: # Fading in
                current_mobj.become(target_text_template)
                self.play(FadeIn(current_mobj, run_time=0.25))
            elif old_text_content and new_text_content: # Changing text (both non-empty)
                temp_old_visual_copy = current_mobj.copy()
                if current_mobj in self.mobjects: self.remove(current_mobj)
                current_mobj.become(target_text_template)
                if current_mobj not in self.mobjects: self.add(current_mobj)

                self.play(FadeOut(temp_old_visual_copy, run_time=0.20, scale=0.8),
                          FadeIn(current_mobj, run_time=0.20, scale=1.2))

            elif new_text_content and old_text_content == new_text_content and old_color_val != new_color: # Only color change
                 self.play(current_mobj.animate.set_color(new_color), run_time=0.3)
            elif not new_text_content and not old_text_content and old_color_val != new_color: # Color change for empty text
                 current_mobj.set_color(new_color) 

        else: # Not animated
            current_mobj.become(target_text_template)
            if current_mobj not in self.mobjects: # Ensure it's on scene
                self.add(current_mobj)


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
            self._update_sink_action_text("advance", new_color=BLUE_A, animate=True) # Text will be above sink
            self.wait(2.0)
            self.play(FadeOut(highlight_ring), run_time=0.15)
            if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
            return pushed

        self.update_status_text(f"DFS Advance: From {u_display_name}, exploring valid LG edges.", play_anim=False)
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
                actual_v_display_name = "s" if actual_v == self.source_node else "t" if actual_v == self.sink_node else str(actual_v)

                original_edge_color = edge_mo_for_v.get_color()
                original_edge_width = edge_mo_for_v.stroke_width
                original_edge_opacity = edge_mo_for_v.stroke_opacity

                current_anims_try = [
                    edge_mo_for_v.animate.set_color(YELLOW_A).set_stroke(width=DFS_EDGE_TRY_WIDTH, opacity=1.0)
                ]
                if edge_key_uv not in self.original_edge_tuples:
                    label_mobj = self.edge_residual_capacity_mobjects.get(edge_key_uv)
                    if label_mobj:
                        target_label = Text(f"{res_cap_cand:.0f}", font=label_mobj.font, font_size=label_mobj.font_size, color=YELLOW_A)
                        target_label.move_to(label_mobj.get_center()).set_opacity(1.0)
                        if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label.height = self.scaled_flow_text_height * 0.9
                        current_anims_try.append(label_mobj.animate.become(target_label))

                self.update_status_text(f"DFS Try: Edge ({u_display_name},{actual_v_display_name}), Res.Cap: {res_cap_cand:.0f}.", play_anim=False)
                self.wait(1.5)
                if current_anims_try: self.play(*current_anims_try, run_time=0.4)
                self.wait(0.5)

                tr = self._dfs_recursive_find_path_anim(actual_v, min(pushed, res_cap_cand), current_path_info_list)

                current_anims_backtrack_restore = []
                if tr > 0:
                    self.update_status_text(f"DFS Path Segment: ({u_display_name},{actual_v_display_name}) is part of an s-t path.", color=GREEN_C, play_anim=False)
                    self.wait(1.5)
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v, original_edge_color, original_edge_width, original_edge_opacity))
                    self.play(FadeOut(highlight_ring), run_time=0.15)
                    if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr

                self.update_status_text(f"DFS Retreat: Edge ({u_display_name},{actual_v_display_name}) is a dead end. Backtracking.", color=YELLOW_C, play_anim=False)
                self._update_sink_action_text("retreat", new_color=ORANGE, animate=True) # Text will be above sink
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
                             if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_revert.height = self.scaled_flow_text_height * 0.9
                             current_anims_backtrack_restore.append(label_mobj.animate.become(target_label_revert))
                        else:
                             current_anims_backtrack_restore.append(label_mobj.animate.set_opacity(0.0))

                if current_anims_backtrack_restore: self.play(*current_anims_backtrack_restore, run_time=0.4)
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.0, run_time=0.45))
                self.wait(0.5)
                self.update_status_text(f"DFS Advance: From {u_display_name}, exploring next valid LG edge.", play_anim=False)
                self.wait(1.0)

            self.ptr[u] += 1

        self.update_status_text(f"DFS Retreat: All LG edges from {u_display_name} explored. Backtracking from {u_display_name}.", color=ORANGE, play_anim=False)
        self._update_sink_action_text("retreat", new_color=ORANGE, animate=True) # Text will be above sink
        self.wait(2.0)
        self.play(FadeOut(highlight_ring), run_time=0.15)
        if highlight_ring in self.dfs_traversal_highlights: self.dfs_traversal_highlights.remove(highlight_ring)
        return 0

    def animate_dfs_path_finding_phase(self):
        self.ptr = {v_id: 0 for v_id in self.vertices_data}
        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1)
        if self.dfs_traversal_highlights not in self.mobjects: self.add(self.dfs_traversal_highlights)


        self._update_sink_action_text("", animate=False) # Text will be above sink (empty)

        self.update_phase_text(f"Phase {self.current_phase_num}: Step 2 - Find Blocking Flow in LG (DFS)", color=ORANGE)
        self.update_status_text("DFS searches for s-t paths in LG to create a blocking flow.", play_anim=True)
        self.wait(3.0)

        while True:
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Seeking s->t path in LG from S (Node {self.source_node}).", play_anim=True)
            self.wait(1.5)
            current_path_anim_info = []

            bottleneck_flow = self._dfs_recursive_find_path_anim(self.source_node, float('inf'), current_path_anim_info)

            if bottleneck_flow == 0:
                self.update_status_text("No more s-t paths in LG. Blocking flow for this phase is complete.", color=YELLOW_C, play_anim=True)
                self.wait(3.5)
                break

            self.max_flow_value += bottleneck_flow
            total_flow_this_phase += bottleneck_flow

            bottleneck_edges_for_indication = []
            current_path_anim_info.reverse()

            for (u_path, v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                edge_key = (u_path, v_path)
                res_cap_before_aug = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                if abs(res_cap_before_aug - bottleneck_flow) < 0.01:
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
            self._update_sink_action_text("augment", new_color=GREEN_B, animate=True) # Text will be above sink
            self.wait(2.5)

            path_highlight_anims = []
            for (u_path, v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                path_highlight_anims.append(edge_mo_path.animate.set_color(GREEN_D).set_stroke(width=DFS_PATH_EDGE_WIDTH, opacity=1.0))

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
                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                        target_text_template_uv.height = self.scaled_flow_text_height
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
                else:
                    lg_color_uv = LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]
                    augmentation_anims.append(edge_mo.animate.set_color(lg_color_uv).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))
                    if (u,v) not in self.original_edge_tuples:
                        label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                        if label_mobj_uv:
                            target_label_uv = Text(f"{res_cap_after_uv:.0f}", font=label_mobj_uv.font, font_size=label_mobj_uv.font_size, color=lg_color_uv)
                            target_label_uv.move_to(label_mobj_uv.get_center()).set_opacity(1.0)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_uv.height = self.scaled_flow_text_height * 0.9
                            augmentation_anims.append(label_mobj_uv.animate.become(target_label_uv))

                if (v,u) in self.edge_mobjects:
                    rev_edge_mo_vu = self.edge_mobjects[(v,u)]
                    res_cap_vu = self.capacities.get((v,u),0) - self.flow.get((v,u),0)
                    is_rev_edge_in_lg_vu = (self.levels.get(v,-1)!=-1 and self.levels.get(u,-1)!=-1 and \
                                         self.levels[u]==self.levels[v]+1 and res_cap_vu > 0)

                    if is_rev_edge_in_lg_vu:
                        lg_color_vu = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(lg_color_vu))
                    elif res_cap_vu > 0 :
                        base_attrs_vu_edge = self.base_edge_visual_attrs.get((v,u),{})
                        opacity_vu = 0.7 if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("opacity", REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0)
                        color_vu = GREY_A if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("color", REVERSE_EDGE_COLOR)
                        width_vu = EDGE_STROKE_WIDTH if (v,u) in self.original_edge_tuples else base_attrs_vu_edge.get("stroke_width", EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR)
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=opacity_vu, width=width_vu, color=color_vu))
                    else:
                        base_attrs_vu_edge = self.base_edge_visual_attrs.get((v,u),{})
                        augmentation_anims.append(rev_edge_mo_vu.animate.set_stroke(opacity=base_attrs_vu_edge.get("opacity",DIMMED_OPACITY), width=base_attrs_vu_edge.get("stroke_width",EDGE_STROKE_WIDTH), color=base_attrs_vu_edge.get("color",DIMMED_COLOR)))


                    if (v,u) not in self.original_edge_tuples:
                        label_mobj_vu = self.edge_residual_capacity_mobjects.get((v,u))
                        if label_mobj_vu:
                            if is_rev_edge_in_lg_vu:
                                lg_color_vu_label = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                                target_label_vu = Text(f"{res_cap_vu:.0f}", font=label_mobj_vu.font, font_size=label_mobj_vu.font_size, color=lg_color_vu_label)
                                target_label_vu.move_to(label_mobj_vu.get_center()).set_opacity(1.0)
                                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                    target_label_vu.height = self.scaled_flow_text_height * 0.9
                                augmentation_anims.append(label_mobj_vu.animate.become(target_label_vu))
                            else:
                                augmentation_anims.append(label_mobj_vu.animate.set_opacity(0.0))
                    else:
                        old_rev_flow_text_mobj = self.edge_flow_val_text_mobjects.get((v,u))
                        if old_rev_flow_text_mobj:
                            new_rev_flow_val_vu = self.flow[(v,u)]
                            new_rev_flow_str_vu = f"{new_rev_flow_val_vu:.0f}" if abs(new_rev_flow_val_vu - round(new_rev_flow_val_vu)) < 0.01 else f"{new_rev_flow_val_vu:.1f}"
                            target_rev_text_template_vu = Text(new_rev_flow_str_vu, font=old_rev_flow_text_mobj.font, font_size=old_rev_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_rev_text_template_vu.height = self.scaled_flow_text_height
                            else: target_rev_text_template_vu.match_height(old_rev_flow_text_mobj)
                            target_rev_text_template_vu.move_to(old_rev_flow_text_mobj.get_center()).rotate(rev_edge_mo_vu.get_angle(), about_point=target_rev_text_template_vu.get_center())
                            text_update_anims.append(old_rev_flow_text_mobj.animate.become(target_rev_text_template_vu))

                        rev_label_grp_vu = self.edge_label_groups.get((v,u))
                        if rev_label_grp_vu and rev_label_grp_vu.submobjects:
                            if is_rev_edge_in_lg_vu:
                                for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                            elif res_cap_vu > 0:
                                for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(0.7))
                            else:
                                base_lbl_attrs = self.base_label_visual_attrs.get((v,u))
                                if base_lbl_attrs:
                                    for part in rev_label_grp_vu.submobjects: augmentation_anims.append(part.animate.set_opacity(base_lbl_attrs.get("opacity", DIMMED_OPACITY)))


            if text_update_anims or augmentation_anims:
                 self.play(AnimationGroup(*(text_update_anims + augmentation_anims), lag_ratio=0.1), run_time=1.5)
            else: self.wait(0.1)

            self.update_max_flow_display(play_anim=True)
            self.wait(0.5)

            self._update_sink_action_text("", animate=True) # Text will be above sink (empty)

            self.update_status_text(f"Flow augmented. Current phase flow: {total_flow_this_phase:.1f}. Searching next path...", color=WHITE, play_anim=True)
            self.wait(2.5)

        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)

        if self.sink_action_text_mobj.text != "":
            self._update_sink_action_text("", animate=True) # Text will be above sink (empty)

        return total_flow_this_phase

    def construct(self):
        self.setup_titles_and_placeholders()
        if self.sink_action_text_mobj not in self.mobjects:
             self.add(self.sink_action_text_mobj)

        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.scaled_flow_text_height = None
        self.update_section_title("1. Building the Flow Network", play_anim=True)

        self.current_phase_num = 0
        self.max_flow_value = 0

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
            if u not in self.adj[v]: self.adj[v].append(u)

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
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.25
            label_group.shift(offset_vector).set_z_index(1)
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))

        for u_node in self.vertices_data:
            for v_node in self.adj[u_node]:
                current_edge_tuple = (u_node, v_node)
                if current_edge_tuple not in self.original_edge_tuples and current_edge_tuple not in self.edge_mobjects:
                    n_u_dot = self.node_mobjects[u_node][0]; n_v_dot = self.node_mobjects[v_node][0]
                    rev_arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS,
                                      stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR,
                                      color=REVERSE_EDGE_COLOR,
                                      max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH * 0.8,
                                      z_index=REVERSE_EDGE_Z_INDEX)
                    rev_arrow.set_opacity(REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0)
                    self.edge_mobjects[current_edge_tuple] = rev_arrow
                    edges_vgroup.add(rev_arrow)

                    res_cap_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR, opacity=0.0)
                    res_cap_val_mobj.move_to(rev_arrow.get_center()).rotate(rev_arrow.get_angle())
                    offset_vector_rev = rotate_vector(rev_arrow.get_unit_vector(), PI / 2) * 0.25
                    res_cap_val_mobj.shift(offset_vector_rev).set_z_index(1)

                    self.edge_residual_capacity_mobjects[current_edge_tuple] = res_cap_val_mobj
                    self.base_label_visual_attrs[current_edge_tuple] = {"opacity": 0.0}

                    pure_rev_label_group = VGroup(res_cap_val_mobj)
                    self.edge_label_groups[current_edge_tuple] = pure_rev_label_group
                    all_edge_labels_vgroup.add(pure_rev_label_group)


        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)

        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])

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

        # Initial positioning of sink_action_text_mobj
        # This ensures it's correctly placed when the graph is first drawn.
        # The _update_sink_action_text method will maintain this relative positioning.
        if hasattr(self, 'node_mobjects') and self.sink_node in self.node_mobjects:
            sink_node_dot = self.node_mobjects[self.sink_node][0]
            self.sink_action_text_mobj.next_to(sink_node_dot, UP, buff=BUFF_SMALL)
        else: # Fallback, though sink_node should exist here
            self.sink_action_text_mobj.to_corner(UL, buff=BUFF_MED) # Or some other default

        for edge_key, edge_mo in self.edge_mobjects.items():
            base_attrs_edge = self.base_edge_visual_attrs.get(edge_key)
            if base_attrs_edge:
                current_opacity = base_attrs_edge["opacity"]
                if edge_key not in self.original_edge_tuples and REVERSE_EDGE_OPACITY == 0.0:
                    current_opacity = 0.0
                edge_mo.set_opacity(current_opacity)


            label_grp = self.edge_label_groups.get(edge_key)
            if label_grp:
                base_attrs_label = self.base_label_visual_attrs.get(edge_key)
                if base_attrs_label:
                    label_grp.set_opacity(base_attrs_label["opacity"])
                elif edge_key in self.original_edge_tuples:
                    label_grp.set_opacity(1.0)
                else:
                    label_grp.set_opacity(0.0)

        sample_text_mobj = None
        for key in self.original_edge_tuples:
            if key in self.edge_flow_val_text_mobjects and self.edge_flow_val_text_mobjects[key] is not None:
                sample_text_mobj = self.edge_flow_val_text_mobjects[key]
                break
        if sample_text_mobj:
            self.scaled_flow_text_height = sample_text_mobj.height
        else:
            dummy_text_unscaled = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text_unscaled.scale(self.desired_large_scale).height


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

        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]

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
        self.node_mobjects[self.source_node][1] = new_s_label_mobj
        self.node_mobjects[self.sink_node][1] = new_t_label_mobj
        self.wait(0.5)

        self.update_section_title("2. Running Dinitz's Algorithm", play_anim=True)
        self.wait(1.0)

        while True:
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Step 1 - Build Level Graph (LG)", color=BLUE_B, play_anim=True)
            self.wait(1.0)
            self.update_status_text(f"BFS from S (Node {self.source_node}) to define node levels (shortest dist. from S).", play_anim=True)
            self.wait(3.0)

            self.levels = {v_id: -1 for v_id in self.vertices_data}
            q_bfs = collections.deque()
            self.levels[self.source_node] = 0; q_bfs.append(self.source_node)

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

            restore_anims = []
            for v_id, node_group in self.node_mobjects.items():
                dot, lbl = node_group
                node_attrs = self.base_node_visual_attrs[v_id]
                restore_anims.append(
                    dot.animate.set_width(node_attrs["width"]).set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"]).set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"])
                )
                if v_id != self.source_node and v_id != self.sink_node:
                     restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))
                elif v_id == self.source_node or v_id == self.sink_node: 
                     restore_anims.append(lbl.animate.set_color(node_attrs["label_color"]))


            for edge_key, edge_mo in self.edge_mobjects.items():
                edge_attrs = self.base_edge_visual_attrs[edge_key]
                current_opacity = edge_attrs["opacity"]
                if edge_key not in self.original_edge_tuples and REVERSE_EDGE_OPACITY == 0.0:
                    current_opacity = 0.0
                restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"]).set_stroke(width=edge_attrs["stroke_width"], opacity=current_opacity))

                label_grp = self.edge_label_groups.get(edge_key)
                if label_grp and label_grp.submobjects:
                    base_label_attr = self.base_label_visual_attrs.get(edge_key)
                    base_opacity_for_label = 0.0
                    if base_label_attr:
                        base_opacity_for_label = base_label_attr.get("opacity", 0.0)
                    elif edge_key in self.original_edge_tuples:
                         base_opacity_for_label = 1.0

                    restore_anims.append(label_grp.animate.set_opacity(base_opacity_for_label))
                    if base_opacity_for_label > 0 and edge_key in self.original_edge_tuples:
                        for part in label_grp.submobjects:
                            if isinstance(part, Text): 
                                restore_anims.append(part.animate.set_color(LABEL_TEXT_COLOR))


            if restore_anims: self.play(AnimationGroup(*restore_anims, lag_ratio=0.01), run_time=0.75)
            self.wait(0.5)

            s_dot_obj, s_lbl_obj = self.node_mobjects[self.source_node]
            self.play(
                s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(self.base_node_visual_attrs[self.source_node]["width"] * 1.1),
                s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE)
            )
            self.wait(0.5)

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
                            bfs_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_u_for_lg).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))

                            if edge_key_bfs not in self.original_edge_tuples:
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get(edge_key_bfs)
                                if res_cap_mobj:
                                    target_text = Text(f"{res_cap_bfs:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=edge_color_u_for_lg)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                        target_text.height = self.scaled_flow_text_height * 0.9
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                    bfs_anims_this_step.append(res_cap_mobj.animate.become(target_text))
                            else:
                                label_grp_bfs = self.edge_label_groups.get(edge_key_bfs)
                                if label_grp_bfs:
                                    for part in label_grp_bfs.submobjects:
                                        if isinstance(part, Text): 
                                            bfs_anims_this_step.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                                        else:
                                            bfs_anims_this_step.append(part.animate.set_opacity(1.0))


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
                self.update_phase_text(f"End of Dinitz. Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.update_status_text(f"Algorithm Terminates. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
                self.wait(4.5)
                break
            else:
                self.update_status_text(f"Sink {sink_display_name} (Node {self.sink_node}) at L{self.levels[self.sink_node]}. Level Graph layers established.", color=GREEN_A, play_anim=True); self.wait(3.0)

                latex_status_string = r"\mbox{Isolating LG: Edges $(u,v)$ where $level(v)=level(u)+1$ \& residual capacity $>0$.}"
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
                        lg_iso_anims.append(edge_mo_lg.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(lg_color))
                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples:
                                res_cap_mobj = self.edge_residual_capacity_mobjects.get((u_lg,v_lg))
                                if res_cap_mobj:
                                    target_text = Text(f"{res_cap_lg_val:.0f}", font=res_cap_mobj.font, font_size=res_cap_mobj.font_size, color=lg_color)
                                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                                        target_text.height = self.scaled_flow_text_height * 0.9
                                    target_text.move_to(res_cap_mobj.get_center()).set_opacity(1.0)
                                    lg_iso_anims.append(res_cap_mobj.animate.become(target_text))
                            else:
                                for part in label_grp_lg.submobjects:
                                    if isinstance(part, Text):
                                        lg_iso_anims.append(part.animate.set_opacity(1.0).set_color(LABEL_TEXT_COLOR))
                                    else:
                                        lg_iso_anims.append(part.animate.set_opacity(1.0))
                    else:
                        base_edge_attrs_local = self.base_edge_visual_attrs.get((u_lg,v_lg), {})
                        target_opacity = DIMMED_OPACITY
                        target_color = DIMMED_COLOR
                        target_width = base_edge_attrs_local.get("stroke_width", EDGE_STROKE_WIDTH)

                        if (u_lg,v_lg) not in self.original_edge_tuples:
                            current_base_opacity = base_edge_attrs_local.get("opacity", REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0)
                            if REVERSE_EDGE_OPACITY == 0.0 and (u_lg,v_lg) not in self.original_edge_tuples :
                                target_opacity = 0.0
                            else:
                                target_opacity = current_base_opacity
                            target_color = base_edge_attrs_local.get("color", REVERSE_EDGE_COLOR)

                        lg_iso_anims.append(edge_mo_lg.animate.set_stroke(opacity=target_opacity, color=target_color, width=target_width))

                        if label_grp_lg and label_grp_lg.submobjects:
                            if (u_lg,v_lg) not in self.original_edge_tuples:
                                lg_iso_anims.append(label_grp_lg.animate.set_opacity(0.0))
                            else:
                                for part in label_grp_lg.submobjects: lg_iso_anims.append(part.animate.set_opacity(DIMMED_OPACITY))


                if lg_iso_anims: self.play(AnimationGroup(*lg_iso_anims, lag_ratio=0.05), run_time=1.0)
                self.wait(2.0)
                self.update_status_text("Level Graph isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True); self.wait(2.5)

                flow_this_phase = self.animate_dfs_path_finding_phase()

                self.update_phase_text(f"End of Phase {self.current_phase_num}. Blocking Flow: {flow_this_phase:.1f}. Sink Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.wait(3.5)
                if self.levels[self.sink_node] != -1 :
                     self.update_status_text(f"Phase complete. Preparing for next phase.", color=BLUE_A, play_anim=True)
                     self.wait(3.0)

        self.update_section_title("3. Dinitz Algorithm Summary", play_anim=True)
        self.wait(1.0)

        if self.levels[self.sink_node] == -1 :
             self.update_status_text(f"Algorithm Concluded. Sink Unreachable. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)
        else:
             self.update_status_text(f"Algorithm Concluded. Final Max Flow: {self.max_flow_value:.1f}", color=GREEN_A, play_anim=True)

        self.wait(5.0)

        mobjects_that_should_remain_on_screen = Group(
            self.main_title,
            self.info_texts_group
        )
        # Ensure no None or non-Mobject types are in this group before processing
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