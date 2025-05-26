from manim import *
import collections

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
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
LEVEL_TEXT_FONT_SIZE = 18

MAIN_TITLE_SMALL_SCALE = 0.65

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

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

TOP_CENTER_ANCHOR = UP * (config.frame_height / 2 - BUFF_SMALL)

class DinitzAlgorithmVisualizer(Scene):

    def setup_titles_and_placeholders(self):
        self.main_title = Text("Visualizing Dinitz's Algorithm", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.move_to(TOP_CENTER_ANCHOR)
        self.main_title.set_z_index(5)
        self.add(self.main_title)
        self.play(Write(self.main_title), run_time=1)
        self.wait(0.5)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD)
        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj
        ).set_z_index(5)

        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED)
        self.info_texts_group.next_to(self.main_title, DOWN, buff=BUFF_MED)

        self.add(self.info_texts_group)

        self.level_display_vgroup = VGroup().set_z_index(5)
        self.level_display_vgroup.to_corner(UR, buff=BUFF_LARGE)
        self.add(self.level_display_vgroup)


    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        old_text_had_actual_content = isinstance(old_mobj, Text) and old_mobj.text != ""
        out_animation = None
        in_animation = None

        if old_text_had_actual_content:
            out_animation = FadeOut(old_mobj, run_time=0.35)

        if new_text_content_str != "":
            in_animation = FadeIn(new_mobj, run_time=0.35, shift=ORIGIN)

        animations_to_play = []
        if out_animation: animations_to_play.append(out_animation)
        if in_animation: animations_to_play.append(in_animation)

        if animations_to_play:
            self.play(*animations_to_play)

    def _update_text_generic(self, text_attr_name, new_text_str, font_size, weight, color, play_anim=True):
        old_mobj = getattr(self, text_attr_name)
        was_placeholder = (old_mobj.text == "")

        new_mobj = Text(new_text_str, font_size=font_size, weight=weight, color=color)

        try:
            idx = self.info_texts_group.submobjects.index(old_mobj)
            self.info_texts_group.remove(old_mobj)

            if was_placeholder and old_mobj in self.mobjects:
                self.remove(old_mobj)

            self.info_texts_group.insert(idx, new_mobj)
        except ValueError: # pragma: no cover
            if old_mobj in self.mobjects:
                self.remove(old_mobj)
            self.info_texts_group.add(new_mobj)

        setattr(self, text_attr_name, new_mobj)

        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED)

        if hasattr(self, 'main_title') and self.main_title in self.mobjects:
             self.info_texts_group.next_to(self.main_title, DOWN, buff=BUFF_MED)

        self.bring_to_front(self.info_texts_group)

        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_str)
        else:
            if old_mobj in self.mobjects and old_mobj is not new_mobj : self.remove(old_mobj)
            if new_text_str != "" and new_mobj not in self.mobjects: self.add(new_mobj)
            elif new_text_str == "" and new_mobj in self.mobjects : self.remove(new_mobj)

    def update_section_title(self, text_str, play_anim=True):
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim)

    def _dfs_recursive_find_path_anim(self, u, pushed, current_path_info_list):
        u_dot_group = self.node_mobjects[u]
        u_dot = u_dot_group[0]

        highlight_ring = Circle(
            radius=u_dot.width/2 * 1.3,
            color=PINK,
            stroke_width=RING_STROKE_WIDTH * 0.7
        ).move_to(u_dot.get_center()).set_z_index(u_dot.z_index + 2)
        self.dfs_traversal_highlights.add(highlight_ring)
        self.play(Create(highlight_ring), run_time=0.25)

        if u == self.sink_node: # Reached t
            self.play(FadeOut(highlight_ring), run_time=0.15)
            self.dfs_traversal_highlights.remove(highlight_ring)
            return pushed

        # Advance along an edge in LG
        while self.ptr[u] < len(self.adj[u]):
            v_candidate = self.adj[u][self.ptr[u]]

            res_cap_cand = self.capacities.get((u, v_candidate), 0) - self.flow.get((u, v_candidate), 0)
            edge_mo_cand = self.edge_mobjects.get((u,v_candidate))

            is_valid_lg_edge = (edge_mo_cand and \
                               self.levels.get(v_candidate, -1) == self.levels[u] + 1 and \
                               res_cap_cand > 0)

            if is_valid_lg_edge:
                actual_v = v_candidate
                edge_mo_for_v = edge_mo_cand
                res_cap_for_v = res_cap_cand

                original_edge_color = edge_mo_for_v.get_color()
                original_edge_width = edge_mo_for_v.get_stroke_width()
                original_edge_opacity = edge_mo_for_v.get_stroke_opacity()

                self.play(edge_mo_for_v.animate.set_color(YELLOW_A).set_stroke(width=DFS_EDGE_TRY_WIDTH, opacity=1.0), run_time=0.3)

                tr = self._dfs_recursive_find_path_anim(actual_v, min(pushed, res_cap_for_v), current_path_info_list)

                if tr > 0: # Path to t found via this edge
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v, original_edge_color, original_edge_width, original_edge_opacity))
                    self.play(FadeOut(highlight_ring), run_time=0.15)
                    self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr # Propagate bottleneck flow back

                # Did not reach t via this edge (actual_v got stuck)
                self.play(
                    edge_mo_for_v.animate.set_color(original_edge_color).set_stroke(width=original_edge_width, opacity=original_edge_opacity),
                    run_time=0.3
                )
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.0, run_time=0.35)) # Indicate edge led to a dead end

            self.ptr[u] += 1 # Try next edge for u

        # If loop finishes, u is stuck (no path to t from u with remaining edges)
        # "Retreat to previous node" happens by returning 0
        # The "delete node from LG" concept is handled by ptr: u won't be used successfully from this path again
        if u != self.sink_node : # Avoid "stuck" message if initial call was to sink (though unlikely)
             # Brief visual indication or silent retreat is often preferred over text for every backtrack
             pass # Current visual is highlight_ring fading out

        self.play(FadeOut(highlight_ring), run_time=0.15)
        self.dfs_traversal_highlights.remove(highlight_ring)
        return 0 # Did not reach t from u

    # --- TODO: Animate flow augmentation and residual graph updates --- (Addressed in this function)
    # --- TODO: Animate max flow calculation and display --- (Addressed by overall flow updates and text)
    def animate_dfs_path_finding_phase(self):
        self.ptr = {v_id: 0 for v_id in self.vertices_data} # Pointer for DFS to avoid re-exploring dead ends from a node

        total_flow_this_phase = 0
        path_count_this_phase = 0
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1)
        self.add(self.dfs_traversal_highlights)

        # Update phase text for this stage of Dinitz
        self.update_phase_text(f"Phase {self.current_phase_num}: Finding Augmenting Paths in LG (DFS)", color=ORANGE, play_anim=True)
        self.wait(0.5)

        while True: # Loop to find multiple augmenting paths (blocking flow) in the current Level Graph (LG)
            path_count_this_phase += 1
            # "Start at s, advance along an edge in LG until reach t or get stuck."
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Searching s->t path from S={self.source_node} in LG", play_anim=True)

            current_path_anim_info = [] # Stores ((u,v), edge_mo, ...) for edges in the found path

            # _dfs_recursive_find_path_anim implements: "advance along an edge in LG until reach t or get stuck"
            # "If get stuck (locally for a node u), retreat to previous node" (handled by DFS recursion and ptr)
            bottleneck_flow = self._dfs_recursive_find_path_anim(
                self.source_node,
                float('inf'), # Initial available capacity
                current_path_anim_info # List to be populated with path edges
            )

            if bottleneck_flow == 0:
                # "If get stuck" (globally from s, no more paths in this LG)
                # This means DFS from source_node could not find any path to sink_node in the current LG.
                self.update_status_text("No more s-t paths in current Level Graph.", color=YELLOW_C, play_anim=True)
                self.wait(1.5)
                break # Exit while loop, blocking flow for this LG is found (or no paths existed)

            # "If reach t, augment flow; update LG; and restart from s."
            total_flow_this_phase += bottleneck_flow
            # Augment flow:
            self.update_status_text(f"Path s->t found! Bottleneck: {bottleneck_flow:.1f}. Augmenting flow.", color=GREEN_A, play_anim=True)

            path_highlight_anims = []
            # Reverse path info because it's collected during DFS backtracking
            current_path_anim_info.reverse()
            for (u_path,v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                path_highlight_anims.append(
                    edge_mo_path.animate.set_color(GREEN_D).set_stroke(width=DFS_PATH_EDGE_WIDTH, opacity=1.0)
                )
            if path_highlight_anims:
                self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.15, run_time=0.8))
            self.wait(0.6)

            # Update LG (flow values and edge appearances):
            augmentation_anims = []
            text_update_anims = []

            for (u,v), edge_mo, orig_color, orig_width, orig_opacity in current_path_anim_info:
                self.flow[(u,v)] = self.flow.get((u,v), 0) + bottleneck_flow
                # Also consider reverse edges if your graph model includes them for residual graph
                # self.flow[(v,u)] = self.flow.get((v,u), 0) - bottleneck_flow # If explicit reverse edges

                old_flow_text_mobj = self.edge_flow_val_text_mobjects[(u,v)]
                new_flow_val = self.flow[(u,v)]
                new_flow_str = f"{new_flow_val:.0f}" if abs(new_flow_val - round(new_flow_val)) < 0.01 else f"{new_flow_val:.1f}"

                arrow = self.edge_mobjects[(u,v)]
                target_text_template = Text(
                    new_flow_str,
                    font=old_flow_text_mobj.font,
                    font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                    color=LABEL_TEXT_COLOR
                )
                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height is not None:
                    target_text_template.set_height(self.scaled_flow_text_height)
                else: # pragma: no cover
                    target_text_template.match_height(old_flow_text_mobj)
                target_text_template.move_to(old_flow_text_mobj.get_center())
                target_text_template.rotate(arrow.get_angle(), about_point=target_text_template.get_center())
                text_update_anims.append(old_flow_text_mobj.animate.become(target_text_template))

                res_cap_after = self.capacities[(u,v)] - self.flow.get((u,v),0)
                # Check if edge is still part of the Level Graph (same levels and positive residual capacity)
                is_still_lg_edge = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                                    self.levels[v]==self.levels[u]+1 and res_cap_after > 0)

                if not is_still_lg_edge: # Edge saturated or no longer valid in LG
                    augmentation_anims.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR, width=EDGE_STROKE_WIDTH))
                else: # Edge still usable in LG, revert to its LG color/width
                    augmentation_anims.append(edge_mo.animate.set_color(LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=orig_opacity))


            all_augmentation_related_anims = text_update_anims + augmentation_anims
            if all_augmentation_related_anims:
                 self.play(AnimationGroup(*all_augmentation_related_anims, lag_ratio=0.1), run_time=1.2)
            else: # pragma: no cover
                 self.wait(1.0)

            # "Restart from s": The loop will continue to find the next path in the same LG
            self.update_status_text(f"Augmented. Flow this phase: {total_flow_this_phase:.1f}. Searching for next s-t path...", color=WHITE, play_anim=True)
            self.wait(1.0)

        # Cleanup DFS highlights if any remain (e.g. if loop broke early)
        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
            self.remove(self.dfs_traversal_highlights) # Ensure removal
        return total_flow_this_phase

    def construct(self):
        self.setup_titles_and_placeholders()
        
        self.scaled_flow_text_height = None # Will be set after scaling graph

        # Graph data
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11))
        self.edges_with_capacity_list = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        self.capacities = collections.defaultdict(int); self.flow = collections.defaultdict(int);
        self.adj = collections.defaultdict(list)
        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)]=cap
            self.adj[u].append(v)
            # For a full residual graph, you'd also add reverse edges if not explicitly in list
            # self.adj[v].append(u) # And handle capacities accordingly (0 initially for reverse)

        self.graph_layout = {
            1: [-3,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }
        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {}
        self.edge_label_groups = {}

        self.desired_large_scale = 1.6

        self.update_section_title("1. Building the Network", play_anim=False)

        nodes_vgroup = VGroup()
        for i, v_id in enumerate(self.vertices_data):
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)

        edges_vgroup = VGroup()
        edge_grow_anims = []
        for u,v,cap in self.edges_with_capacity_list:
            n_u_dot = self.node_mobjects[u][0]; n_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS, stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow; edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)

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

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj)
            label_group.arrange(RIGHT, buff=BUFF_VERY_SMALL)
            label_group.move_to(arrow.get_center())
            label_group.rotate(arrow.get_angle())
            offset_distance = 0.25
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * offset_distance
            label_group.shift(offset_vector)
            label_group.set_z_index(1)
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))

        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2)

        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        
        if self.edge_flow_val_text_mobjects:
            first_edge_key = next(iter(self.edge_flow_val_text_mobjects))
            sample_flow_mobj = self.edge_flow_val_text_mobjects[first_edge_key]
            self.scaled_flow_text_height = sample_flow_mobj.height # Height after scaling
        else: # pragma: no cover
            dummy_text = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text.height * self.desired_large_scale

        self.base_node_visual_attrs = {} # Store base attributes after scaling
        for v_id, node_group in self.node_mobjects.items():
            dot = node_group[0]
            self.base_node_visual_attrs[v_id] = {
                "width": dot.get_width(), "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(), "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity()
            }
        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(), "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }

        s_dot = self.node_mobjects[self.source_node][0]; t_dot = self.node_mobjects[self.sink_node][0]
        source_ring = Circle(radius=s_dot.width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(s_dot.get_center()).set_z_index(RING_Z_INDEX)
        sink_ring = Circle(radius=t_dot.width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(t_dot.get_center()).set_z_index(RING_Z_INDEX)
        self.source_ring_mobj = source_ring; self.sink_ring_mobj = sink_ring
        self.play(Create(self.source_ring_mobj), Create(self.sink_ring_mobj), run_time=0.75)
        self.wait(1.0)
        self.update_status_text("", play_anim=False); self.wait(0.5)

        # Dinitz Algorithm Execution Begins
        self.update_section_title("2. Dinitz Algorithm Execution")
        self.current_phase_num = 1 # Assuming one full pass (BFS + DFS augmentations) is one "phase" here
        self.max_flow_value = 0
        
        # "Construct level graph LG."
        self.update_phase_text(f"Phase {self.current_phase_num}: Construct Level Graph (LG) using BFS", color=BLUE_B)
        self.update_status_text(f"Starting BFS from Source S={self.source_node} to find levels to Sink T={self.sink_node}")

        self.levels = {v_id: -1 for v_id in self.vertices_data} # Stores level of each node
        q_bfs = collections.deque()

        current_bfs_level_num = 0
        self.levels[self.source_node] = current_bfs_level_num
        q_bfs.append(self.source_node)

        s_dot_obj = self.node_mobjects[self.source_node][0]; s_lbl_obj = self.node_mobjects[self.source_node][1]
        s_base_width = self.base_node_visual_attrs[self.source_node]["width"]
        self.play(
            s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(s_base_width * 1.1),
            s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE),
            run_time=0.5
        )
        l_p0 = Text(f"L{current_bfs_level_num}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
        l_n0 = Text(f" {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
        l0_vg = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL)
        self.level_display_vgroup.add(l0_vg)
        self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
        self.play(Write(l0_vg))
        max_level_text_width = config.frame_width * 0.30

        bfs_path_found_to_sink = False
        while q_bfs:
            nodes_to_process = list(q_bfs); q_bfs.clear()
            if not nodes_to_process: break
            target_level = self.levels[nodes_to_process[0]] + 1
            nodes_found_next_lvl_set = set(); node_color_anims = []; edge_highlight_anims_this_step = []

            for u_bfs in nodes_to_process:
                node_to_indicate = self.node_mobjects[u_bfs]
                ind_u = SurroundingRectangle(node_to_indicate, color=YELLOW_C, buff=0.03, stroke_width=2.0, corner_radius=0.05)
                self.play(Create(ind_u), run_time=0.15)

                for v_n_bfs in self.adj[u_bfs]: # Check neighbors in original graph structure
                    res_cap_bfs = self.capacities[(u_bfs,v_n_bfs)]-self.flow.get((u_bfs,v_n_bfs),0)
                    if res_cap_bfs > 0 and self.levels[v_n_bfs] == -1: # If unvisited and reachable
                        self.levels[v_n_bfs] = target_level
                        nodes_found_next_lvl_set.add(v_n_bfs)
                        q_bfs.append(v_n_bfs)
                        lvl_color = LEVEL_COLORS[target_level % len(LEVEL_COLORS)]
                        n_v_dot = self.node_mobjects[v_n_bfs][0]; n_v_lbl = self.node_mobjects[v_n_bfs][1]
                        v_base_width = self.base_node_visual_attrs[v_n_bfs]["width"]
                        node_color_anims.append(n_v_dot.animate.set_fill(lvl_color).set_width(v_base_width * 1.1))
                        rgb_c = color_to_rgb(lvl_color); lbl_c = BLACK if sum(rgb_c)>1.5 else WHITE
                        node_color_anims.append(n_v_lbl.animate.set_color(lbl_c))
                        edge_mo_bfs = self.edge_mobjects.get((u_bfs, v_n_bfs))
                        if edge_mo_bfs:
                             edge_color_bfs = LEVEL_COLORS[self.levels[u_bfs]%len(LEVEL_COLORS)]
                             edge_highlight_anims_this_step.append(edge_mo_bfs.animate.set_color(edge_color_bfs).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
                        if v_n_bfs == self.sink_node: bfs_path_found_to_sink = True
                self.play(FadeOut(ind_u), run_time=0.15)
            
            if node_color_anims or edge_highlight_anims_this_step: self.play(AnimationGroup(*(node_color_anims + edge_highlight_anims_this_step), lag_ratio=0.1), run_time=0.6)
            if nodes_found_next_lvl_set:
                n_str = ", ".join(map(str, sorted(list(nodes_found_next_lvl_set))))
                l_px = Text(f"L{target_level}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[target_level%len(LEVEL_COLORS)])
                l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
                l_vg = VGroup(l_px,l_nx).arrange(RIGHT,buff=BUFF_VERY_SMALL)
                self.level_display_vgroup.add(l_vg)
                self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                if self.level_display_vgroup.width > max_level_text_width: self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                self.play(Write(l_vg)); self.wait(0.3)
            if not q_bfs : break # BFS queue is empty

        if self.levels[self.sink_node] == -1: # Sink not reached by BFS
            self.update_status_text(f"Sink T={self.sink_node} NOT Reached by BFS. Algorithm Terminates. Final Max Flow: {self.max_flow_value:.1f}", color=RED_C)
            self.wait(3)
        else: # Sink reached, Level Graph construction continues
            self.update_status_text(f"Sink T={self.sink_node} Reached at Level L{self.levels[self.sink_node]}. Level Graph (LG) Built.", color=GREEN_A)
            self.wait(0.5)
            self.update_status_text("Isolating LG: Highlighting valid forward edges, dimming others.", play_anim=True)
            lg_edge_anims = []; non_lg_edge_anims = []
            for (u_lg,v_lg), edge_mo_lg in self.edge_mobjects.items():
                res_cap_lg = self.capacities[(u_lg,v_lg)]-self.flow.get((u_lg,v_lg),0)
                is_lg_edge = (self.levels.get(u_lg,-1)!=-1 and self.levels.get(v_lg,-1)!=-1 and \
                                self.levels[v_lg]==self.levels[u_lg]+1 and \
                                res_cap_lg > 0 )
                if is_lg_edge:
                    edge_c = LEVEL_COLORS[self.levels[u_lg]%len(LEVEL_COLORS)]
                    lg_edge_anims.append(edge_mo_lg.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(edge_c))
                else:
                    non_lg_edge_anims.append(edge_mo_lg.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR))
            if non_lg_edge_anims + lg_edge_anims: self.play(AnimationGroup(*(non_lg_edge_anims + lg_edge_anims), lag_ratio=0.05), run_time=0.75)
            self.wait(1)
            self.update_status_text("Level Graph Isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True)
            self.wait(1)

            # Call DFS to find blocking flow in this LG
            flow_this_phase = self.animate_dfs_path_finding_phase()
            self.max_flow_value += flow_this_phase

            # --- TODO: Animate max flow calculation and display --- (This is part of it)
            self.update_phase_text(f"End of Dinitz Phase {self.current_phase_num}. Total Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
            self.wait(1.5)

            if flow_this_phase == 0:
                 self.update_status_text(f"No augmenting flow found in this LG. Max Flow: {self.max_flow_value:.1f}", color=YELLOW_C, play_anim=True)
            else: # flow_this_phase > 0
                 self.update_status_text(f"Blocking flow of {flow_this_phase:.1f} found. Current Max Flow: {self.max_flow_value:.1f}.", color=BLUE_A, play_anim=True)
            
            # For a full Dinitz, it would now check if it should loop for another phase (new BFS, etc.)
            # Here, we signify the end of this single visualized pass.
            self.update_status_text(f"Current Max Flow: {self.max_flow_value:.1f}. (Algorithm would re-BFS if further phases were run)", color=BLUE_B, play_anim=True)
            self.wait(3)

        # Fade out graph elements for clean end
        final_mobjects_to_keep_list_end = [self.main_title, self.current_section_title_mobj, self.phase_text_mobj, self.algo_status_mobj]
        mobjects_to_fade_out_finally = Group(*[m for m in self.mobjects if m not in final_mobjects_to_keep_list_end and m is not None])
        if mobjects_to_fade_out_finally.submobjects:
            self.play(FadeOut(mobjects_to_fade_out_finally), run_time=1.5)
        
        self.wait(2) # Hold final message