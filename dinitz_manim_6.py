from manim import *
import collections

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.18
EDGE_OFFSET_AMOUNT = 0.12 # Offset for parallel edges

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 # For text below main title
PHASE_TEXT_FONT_SIZE = 22    # For text below section title
STATUS_TEXT_FONT_SIZE = 20   # For text below phase title
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
LEVEL_TEXT_FONT_SIZE = 18
REVERSE_EDGE_FLOW_ONLY_FONT_SIZE = 10 # Smaller font for reverse edge flow

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

# Visuals for purely reverse edges (not in original graph)
REVERSE_EDGE_COLOR = GREY_B
REVERSE_EDGE_OPACITY = 0.25 # Base opacity when active but not in LG
REVERSE_EDGE_STROKE_WIDTH_FACTOR = 0.6
REVERSE_LABEL_OPACITY = 0.4 # Base opacity for labels of active reverse edges
REVERSE_EDGE_Z_INDEX = -1 # Behind forward edges

TOP_CENTER_ANCHOR = UP * (config.frame_height / 2 - BUFF_SMALL)

class DinitzAlgorithmVisualizer(Scene):

    def setup_titles_and_placeholders(self):
        # Initializes the main title and placeholders for other informational text.
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
        # Helper function to animate transitions between old and new text mobjects.
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
        # Generic function to update one of the informational text mobjects.
        old_mobj = getattr(self, text_attr_name)
        was_placeholder = (old_mobj.text == "") 

        new_mobj = Text(new_text_str, font_size=font_size, weight=weight, color=color)

        try:
            idx = self.info_texts_group.submobjects.index(old_mobj)
            self.info_texts_group.remove(old_mobj)
            if was_placeholder and old_mobj in self.mobjects:
                self.remove(old_mobj)
            self.info_texts_group.insert(idx, new_mobj)
        except ValueError: 
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

        if u == self.sink_node: 
            self.play(FadeOut(highlight_ring), run_time=0.15) 
            self.dfs_traversal_highlights.remove(highlight_ring)
            return pushed 

        while self.ptr[u] < len(self.adj[u]):
            v_candidate = self.adj[u][self.ptr[u]] 

            res_cap_cand = self.capacities.get((u, v_candidate), 0) - self.flow.get((u, v_candidate), 0)
            edge_mo_cand = self.edge_mobjects.get((u,v_candidate)) 

            is_valid_lg_edge = (edge_mo_cand and \
                               self.levels.get(v_candidate, -1) == self.levels.get(u, -1) + 1 and \
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

                if tr > 0: 
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v, original_edge_color, original_edge_width, original_edge_opacity))
                    self.play(FadeOut(highlight_ring), run_time=0.15) 
                    self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr 

                self.play(
                    edge_mo_for_v.animate.set_color(original_edge_color).set_stroke(width=original_edge_width, opacity=original_edge_opacity),
                    run_time=0.3
                )
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.0, run_time=0.35)) 

            self.ptr[u] += 1 
        
        self.play(FadeOut(highlight_ring), run_time=0.15)
        self.dfs_traversal_highlights.remove(highlight_ring)
        return 0

    def animate_dfs_path_finding_phase(self):
        self.ptr = {v_id: 0 for v_id in self.vertices_data} 
        total_flow_this_phase = 0 
        path_count_this_phase = 0 
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1) 
        self.add(self.dfs_traversal_highlights)

        self.update_phase_text(f"Phase {self.current_phase_num}: Finding Augmenting Paths in LG (DFS)", color=ORANGE, play_anim=True)
        self.wait(0.5)

        while True: 
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Searching s->t path from S={self.source_node} in LG", play_anim=True)
            current_path_anim_info = [] 
            bottleneck_flow = self._dfs_recursive_find_path_anim(
                self.source_node, float('inf'), current_path_anim_info 
            )

            if bottleneck_flow == 0:
                self.update_status_text("No more s-t paths in current Level Graph.", color=YELLOW_C, play_anim=True)
                self.wait(1.5)
                break 

            total_flow_this_phase += bottleneck_flow
            self.update_status_text(f"Path s->t found! Bottleneck: {bottleneck_flow:.1f}. Augmenting flow.", color=GREEN_A, play_anim=True)

            path_highlight_anims = []
            current_path_anim_info.reverse() 
            for (u_path,v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                path_highlight_anims.append(
                    edge_mo_path.animate.set_color(GREEN_D).set_stroke(width=DFS_PATH_EDGE_WIDTH, opacity=1.0)
                )
            if path_highlight_anims:
                self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.15, run_time=0.8))
            self.wait(0.6)

            # --- Augmentation Step 1: Update flow data and prepare text transforms ---
            text_transform_animations = []
            
            for (u,v), edge_mo, _, _, _ in current_path_anim_info:
                # Update flow data
                self.flow[(u,v)] = self.flow.get((u,v), 0) + bottleneck_flow
                self.flow[(v,u)] = self.flow.get((v,u), 0) - bottleneck_flow 

                # Prepare transform for forward edge (u,v)
                is_original_forward_uv = (u,v) in self.original_edge_tuples
                current_flow_mobj_uv = self.edge_flow_val_text_mobjects.get((u,v))
                if current_flow_mobj_uv: # Should always exist if edge_mo exists
                    new_flow_val_uv = self.flow[(u,v)]
                    new_flow_str_uv = f"{new_flow_val_uv:.0f}" if abs(new_flow_val_uv - round(new_flow_val_uv)) < 0.01 else f"{new_flow_val_uv:.1f}"
                    
                    target_uv_text = current_flow_mobj_uv.copy().set_text(new_flow_str_uv)
                    # Ensure font size is correct if it's a pure reverse edge being used forward
                    if not is_original_forward_uv: 
                        target_uv_text.set_font_size(REVERSE_EDGE_FLOW_ONLY_FONT_SIZE)
                        if hasattr(self, 'scaled_reverse_flow_text_height') and self.scaled_reverse_flow_text_height:
                            target_uv_text.set_height(self.scaled_reverse_flow_text_height)
                    
                    text_transform_animations.append(Transform(current_flow_mobj_uv, target_uv_text))

                # Prepare transform for reverse edge (v,u)
                if (v,u) in self.edge_mobjects:
                    current_flow_mobj_vu = self.edge_flow_val_text_mobjects.get((v,u))
                    if current_flow_mobj_vu:
                        new_flow_val_vu = self.flow[(v,u)]
                        new_flow_str_vu = f"{new_flow_val_vu:.0f}" if abs(new_flow_val_vu - round(new_flow_val_vu)) < 0.01 else f"{new_flow_val_vu:.1f}"
                        
                        target_vu_text = current_flow_mobj_vu.copy().set_text(new_flow_str_vu)
                        is_pure_reverse_vu = (v,u) not in self.original_edge_tuples
                        if is_pure_reverse_vu:
                            target_vu_text.set_font_size(REVERSE_EDGE_FLOW_ONLY_FONT_SIZE)
                            if hasattr(self, 'scaled_reverse_flow_text_height') and self.scaled_reverse_flow_text_height:
                                target_vu_text.set_height(self.scaled_reverse_flow_text_height)
                        
                        text_transform_animations.append(Transform(current_flow_mobj_vu, target_vu_text))
            
            # --- Augmentation Step 2: Play text transformations ---
            if text_transform_animations:
                self.play(*text_transform_animations, run_time=0.7) # Play simultaneously
                self.wait(0.3) # Brief pause after text updates

            # --- Augmentation Step 3: Update edge visual styles (colors, opacities) ---
            edge_style_animations = []
            for (u,v), edge_mo, orig_color, orig_width, orig_opacity in current_path_anim_info:
                # Forward edge (u,v) style update
                res_cap_after_uv = self.capacities.get((u,v),0) - self.flow.get((u,v),0)
                is_still_lg_uv = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                                    self.levels[v]==self.levels[u]+1 and res_cap_after_uv > 0)
                label_component_uv = self.edge_label_groups.get((u,v))

                if not is_still_lg_uv: 
                    edge_style_animations.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR, width=EDGE_STROKE_WIDTH))
                    if label_component_uv: edge_style_animations.append(label_component_uv.animate.set_opacity(DIMMED_OPACITY))
                else: 
                    edge_style_animations.append(edge_mo.animate.set_color(LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0)) # Path was highlighted, so opacity is 1
                    if label_component_uv: edge_style_animations.append(label_component_uv.animate.set_opacity(1.0))

                # Reverse edge (v,u) style update
                if (v,u) in self.edge_mobjects:
                    rev_edge_mo_vu = self.edge_mobjects[(v,u)]
                    res_cap_vu = self.capacities.get((v,u),0) - self.flow[(v,u)] 
                    is_rev_edge_in_lg = (self.levels.get(v,-1)!=-1 and self.levels.get(u,-1)!=-1 and \
                                         self.levels[u]==self.levels[v]+1 and res_cap_vu > 0)
                    label_component_vu = self.edge_label_groups.get((v,u))
                    
                    target_op_vu, target_lbl_op_vu = 0, 0
                    target_color_vu = self.base_edge_visual_attrs.get((v,u), {}).get("color", REVERSE_EDGE_COLOR)
                    target_width_vu = self.base_edge_visual_attrs.get((v,u), {}).get("stroke_width", EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR)

                    if is_rev_edge_in_lg:
                        target_op_vu, target_lbl_op_vu = 1.0, 1.0
                        target_color_vu = LEVEL_COLORS[self.levels[v]%len(LEVEL_COLORS)]
                        target_width_vu = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH
                    elif res_cap_vu > 0: 
                        target_op_vu = REVERSE_EDGE_OPACITY 
                        target_lbl_op_vu = REVERSE_LABEL_OPACITY
                    
                    edge_style_animations.append(rev_edge_mo_vu.animate.set_opacity(target_op_vu).set_color(target_color_vu).set_stroke(width=target_width_vu))
                    if label_component_vu: 
                        current_label_op_vu = None
                        if isinstance(label_component_vu, Text): current_label_op_vu = label_component_vu.get_opacity()
                        elif isinstance(label_component_vu, VGroup) and label_component_vu.submobjects:
                            current_label_op_vu = label_component_vu.submobjects[0].get_opacity()
                        
                        if current_label_op_vu is None or abs(current_label_op_vu - target_lbl_op_vu) > 0.01:
                             edge_style_animations.append(label_component_vu.animate.set_opacity(target_lbl_op_vu))
            
            if edge_style_animations:
                self.play(*edge_style_animations, run_time=1.0)
                self.wait(0.5)


            self.update_status_text(f"Augmented. Flow this phase: {total_flow_this_phase:.1f}. Searching for next s-t path...", color=WHITE, play_anim=True)
            self.wait(1.0)

        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
            self.remove(self.dfs_traversal_highlights) 
        return total_flow_this_phase 

    def construct(self):
        self.setup_titles_and_placeholders()
        self.scaled_flow_text_height = None 
        self.scaled_reverse_flow_text_height = None 

        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11)) 
        self.edges_with_capacity_list = [ 
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        
        self.capacities = collections.defaultdict(int) 
        self.flow = collections.defaultdict(int)       
        self.adj = collections.defaultdict(list)       
        self.original_edge_tuples = set([(u,v) for u,v,c in self.edges_with_capacity_list])


        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            if v not in self.adj[u]: 
                self.adj[u].append(v)
            if u not in self.adj[v]: 
                self.adj[v].append(u)

        self.graph_layout = {
            1: [-4,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }

        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {} 
        self.edge_label_groups = {} 
        self.base_label_visual_attrs = {} 

        self.desired_large_scale = 1.6 
        self.update_section_title("1. Building the Network", play_anim=False) 

        nodes_vgroup = VGroup() 
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)

        edges_vgroup = VGroup() 
        edge_grow_anims = []
        
        for u,v,cap in self.edges_with_capacity_list:
            start_node_center = self.node_mobjects[u][0].get_center()
            end_node_center = self.node_mobjects[v][0].get_center()
            
            direction_vec = end_node_center - start_node_center
            if np.linalg.norm(direction_vec) == 0: direction_vec = RIGHT 
            unit_direction = normalize(direction_vec)
            perpendicular = rotate_vector(unit_direction, PI/2)
            
            current_offset_vector = perpendicular * EDGE_OFFSET_AMOUNT
            
            arrow_start = start_node_center + current_offset_vector
            arrow_end = end_node_center + current_offset_vector
            
            arrow = Arrow(arrow_start, arrow_end, buff=NODE_RADIUS, 
                          stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, 
                          max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow
            edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        
        if edge_grow_anims: 
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
            self.base_label_visual_attrs[(u,v)] = {"opacity": flow_val_mobj.get_opacity()}

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj)
            label_group.arrange(RIGHT, buff=BUFF_VERY_SMALL) 
            label_group.move_to(arrow.get_center()) 
            label_group.rotate(arrow.get_angle())   
            label_offset_distance = 0.25 
            label_offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * label_offset_distance
            label_group.shift(label_offset_vector)
            label_group.set_z_index(1) 
            self.edge_label_groups[(u,v)] = label_group 
            all_edge_labels_vgroup.add(label_group)
            
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))

        for u_start_rev in self.vertices_data:
            for v_end_rev in self.adj[u_start_rev]: 
                edge_tuple_rev = (u_start_rev, v_end_rev)
                if edge_tuple_rev not in self.original_edge_tuples: 
                    if edge_tuple_rev in self.edge_mobjects: continue 

                    start_node_center = self.node_mobjects[u_start_rev][0].get_center()
                    end_node_center = self.node_mobjects[v_end_rev][0].get_center()

                    direction_vec = end_node_center - start_node_center
                    if np.linalg.norm(direction_vec) == 0: direction_vec = RIGHT
                    unit_direction = normalize(direction_vec)
                    perpendicular = rotate_vector(unit_direction, PI/2)
                    current_offset_vector = perpendicular * (-EDGE_OFFSET_AMOUNT) 

                    arrow_start = start_node_center + current_offset_vector
                    arrow_end = end_node_center + current_offset_vector

                    rev_arrow = Arrow(arrow_start, arrow_end, buff=NODE_RADIUS,
                                      stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR, 
                                      color=REVERSE_EDGE_COLOR,
                                      max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH * 0.8,
                                      z_index=REVERSE_EDGE_Z_INDEX) 
                    rev_arrow.set_opacity(0) 
                    self.edge_mobjects[edge_tuple_rev] = rev_arrow
                    edges_vgroup.add(rev_arrow) 

                    flow_val_mobj_rev = Text("0", font_size=REVERSE_EDGE_FLOW_ONLY_FONT_SIZE, color=LABEL_TEXT_COLOR)
                    flow_val_mobj_rev.set_opacity(0) 

                    self.edge_flow_val_text_mobjects[edge_tuple_rev] = flow_val_mobj_rev
                    self.base_label_visual_attrs[edge_tuple_rev] = {"opacity": 0}

                    flow_val_mobj_rev.move_to(rev_arrow.get_center())
                    flow_val_mobj_rev.rotate(rev_arrow.get_angle())
                    label_offset_distance = 0.20 
                    label_offset_vector = rotate_vector(rev_arrow.get_unit_vector(), PI/2) * label_offset_distance
                    flow_val_mobj_rev.shift(label_offset_vector)
                    flow_val_mobj_rev.set_z_index(0) 
                    self.edge_label_groups[edge_tuple_rev] = flow_val_mobj_rev 
                    all_edge_labels_vgroup.add(flow_val_mobj_rev) 
        
        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2)

        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        
        if self.edge_flow_val_text_mobjects: 
            sample_key_options = list(self.original_edge_tuples)
            if sample_key_options: 
                first_edge_key = sample_key_options[0]
                sample_flow_mobj = self.edge_flow_val_text_mobjects[first_edge_key]
                self.scaled_flow_text_height = sample_flow_mobj.height 
            else: 
                 non_pure_reverse_keys = [k for k in self.edge_flow_val_text_mobjects.keys() if k in self.original_edge_tuples]
                 if non_pure_reverse_keys:
                      self.scaled_flow_text_height = self.edge_flow_val_text_mobjects[non_pure_reverse_keys[0]].height
                 else: 
                    dummy_text = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
                    self.scaled_flow_text_height = dummy_text.height * self.desired_large_scale
        else: 
            dummy_text = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text.height * self.desired_large_scale
        
        dummy_rev_text = Text("0", font_size=REVERSE_EDGE_FLOW_ONLY_FONT_SIZE)
        self.scaled_reverse_flow_text_height = dummy_rev_text.height * self.desired_large_scale


        self.base_node_visual_attrs = {} 
        for v_id, node_group in self.node_mobjects.items():
            dot = node_group[0]; label = node_group[1] 
            self.base_node_visual_attrs[v_id] = {
                "width": dot.get_width(), "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(), "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity(), "label_color": label.get_color() 
            }
        self.base_edge_visual_attrs = {} 
        for edge_key, edge_mo in self.edge_mobjects.items(): 
            is_pure_reverse = edge_key not in self.original_edge_tuples
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(), 
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": 0 if is_pure_reverse else edge_mo.get_stroke_opacity() 
            }
            if edge_key in self.edge_label_groups:
                 if edge_key not in self.base_label_visual_attrs: 
                    self.base_label_visual_attrs[edge_key] = {"opacity": self.edge_label_groups[edge_key].get_opacity()}


        s_dot = self.node_mobjects[self.source_node][0]; t_dot = self.node_mobjects[self.sink_node][0]
        source_ring = Circle(radius=s_dot.width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(s_dot.get_center()).set_z_index(RING_Z_INDEX)
        sink_ring = Circle(radius=t_dot.width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(t_dot.get_center()).set_z_index(RING_Z_INDEX)
        self.source_ring_mobj = source_ring; self.sink_ring_mobj = sink_ring
        self.play(Create(self.source_ring_mobj), Create(self.sink_ring_mobj), run_time=0.75)
        self.wait(1.0)
        self.update_status_text("", play_anim=False); self.wait(0.5) 

        self.update_section_title("2. Dinitz Algorithm Execution")
        self.current_phase_num = 0 
        self.max_flow_value = 0
        
        while True:
            self.current_phase_num += 1
            self.update_phase_text(f"Phase {self.current_phase_num}: Construct Level Graph (LG) using BFS", color=BLUE_B)
            self.update_status_text(f"Starting BFS from S={self.source_node} to find levels to T={self.sink_node}")
            self.wait(0.5)

            self.levels = {v_id: -1 for v_id in self.vertices_data} 
            q_bfs = collections.deque() 

            current_bfs_level_num = 0
            self.levels[self.source_node] = current_bfs_level_num
            q_bfs.append(self.source_node)
            
            if self.level_display_vgroup.submobjects:
                self.play(FadeOut(self.level_display_vgroup))
                self.remove(self.level_display_vgroup) 
                self.level_display_vgroup = VGroup().set_z_index(5).to_corner(UR, buff=BUFF_LARGE)
                self.add(self.level_display_vgroup)

            l_p0 = Text(f"L{current_bfs_level_num}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
            l_n0 = Text(f" {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
            l0_vg = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL)
            self.level_display_vgroup.add(l0_vg)
            self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
            self.play(Write(l0_vg))
            max_level_text_width = config.frame_width * 0.30 
            
            restore_anims = []
            for v_id, node_attrs in self.base_node_visual_attrs.items():
                node_dot = self.node_mobjects[v_id][0]; node_lbl = self.node_mobjects[v_id][1]
                restore_anims.append(node_dot.animate.set_width(node_attrs["width"])
                                                        .set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"])
                                                        .set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"]))
                restore_anims.append(node_lbl.animate.set_color(node_attrs["label_color"])) 
            
            for edge_key, edge_attrs in self.base_edge_visual_attrs.items():
                edge_mo = self.edge_mobjects.get(edge_key)
                if edge_mo:
                    restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"])
                                                       .set_stroke(width=edge_attrs["stroke_width"], opacity=edge_attrs["opacity"]))
                if edge_key in self.edge_label_groups:
                    label_base_attrs = self.base_label_visual_attrs.get(edge_key)
                    label_mobj_or_grp = self.edge_label_groups[edge_key]
                    if label_base_attrs: 
                        if isinstance(label_mobj_or_grp, VGroup):
                            for label_part_mo in label_mobj_or_grp.submobjects:
                                restore_anims.append(label_part_mo.animate.set_opacity(label_base_attrs["opacity"]))
                        else: 
                            restore_anims.append(label_mobj_or_grp.animate.set_opacity(label_base_attrs["opacity"]))

            if restore_anims:
                self.play(AnimationGroup(*restore_anims, lag_ratio=0.01, run_time=0.75))
            
            s_dot_obj = self.node_mobjects[self.source_node][0]; s_lbl_obj = self.node_mobjects[self.source_node][1]
            s_base_width = self.base_node_visual_attrs[self.source_node]["width"]
            self.play(
                self.source_ring_mobj.animate.set_opacity(1), self.sink_ring_mobj.animate.set_opacity(1),
                s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(s_base_width * 1.1), 
                s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE) 
            )

            while q_bfs:
                nodes_to_process_this_level = list(q_bfs); q_bfs.clear() 
                if not nodes_to_process_this_level: break 
                target_level = self.levels[nodes_to_process_this_level[0]] + 1
                nodes_found_next_lvl_set = set(); node_color_anims_bfs = []; edge_highlight_anims_bfs_step = [] 

                for u_bfs in nodes_to_process_this_level:
                    node_to_indicate = self.node_mobjects[u_bfs]
                    ind_u = SurroundingRectangle(node_to_indicate, color=YELLOW_C, buff=0.03, stroke_width=2.0, corner_radius=0.05)
                    self.play(Create(ind_u), run_time=0.15)

                    for v_n_bfs in self.adj[u_bfs]: 
                        res_cap_bfs = self.capacities.get((u_bfs,v_n_bfs),0) - self.flow.get((u_bfs,v_n_bfs),0)
                        edge_mo_bfs = self.edge_mobjects.get((u_bfs, v_n_bfs)) 

                        if res_cap_bfs > 0 and self.levels[v_n_bfs] == -1: 
                            self.levels[v_n_bfs] = target_level 
                            nodes_found_next_lvl_set.add(v_n_bfs)
                            q_bfs.append(v_n_bfs) 
                            
                            lvl_color = LEVEL_COLORS[target_level % len(LEVEL_COLORS)]
                            n_v_dot = self.node_mobjects[v_n_bfs][0]; n_v_lbl = self.node_mobjects[v_n_bfs][1]
                            v_base_width = self.base_node_visual_attrs[v_n_bfs]["width"]
                            node_color_anims_bfs.append(n_v_dot.animate.set_fill(lvl_color).set_width(v_base_width * 1.1))
                            rgb_c = color_to_rgb(lvl_color); lbl_c = BLACK if sum(rgb_c)>1.5 else WHITE 
                            node_color_anims_bfs.append(n_v_lbl.animate.set_color(lbl_c))
                            
                            if edge_mo_bfs: 
                                 edge_color_bfs = LEVEL_COLORS[self.levels[u_bfs]%len(LEVEL_COLORS)] 
                                 edge_highlight_anims_bfs_step.append(edge_mo_bfs.animate.set_color(edge_color_bfs).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=1.0))
                                 label_mobj_or_grp_bfs = self.edge_label_groups.get((u_bfs, v_n_bfs))
                                 if label_mobj_or_grp_bfs:
                                     if isinstance(label_mobj_or_grp_bfs, VGroup):
                                         for part in label_mobj_or_grp_bfs.submobjects:
                                             edge_highlight_anims_bfs_step.append(part.animate.set_opacity(1.0))
                                     else: 
                                         edge_highlight_anims_bfs_step.append(label_mobj_or_grp_bfs.animate.set_opacity(1.0))
                    
                    self.play(FadeOut(ind_u), run_time=0.15) 
                
                if node_color_anims_bfs or edge_highlight_anims_bfs_step: 
                    self.play(AnimationGroup(*(node_color_anims_bfs + edge_highlight_anims_bfs_step), lag_ratio=0.1), run_time=0.6)
                
                if nodes_found_next_lvl_set:
                    n_str = ", ".join(map(str, sorted(list(nodes_found_next_lvl_set))))
                    l_px = Text(f"L{target_level}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[target_level%len(LEVEL_COLORS)])
                    l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
                    l_vg = VGroup(l_px,l_nx).arrange(RIGHT,buff=BUFF_VERY_SMALL)
                    self.level_display_vgroup.add(l_vg)
                    self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                    if self.level_display_vgroup.width > max_level_text_width: 
                        self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                    self.play(Write(l_vg)); self.wait(0.3)
                
                if not q_bfs : break 

            if self.levels[self.sink_node] == -1: 
                self.update_status_text(f"Sink T={self.sink_node} NOT Reached by BFS. Algorithm Terminates. Final Max Flow: {self.max_flow_value:.1f}", color=RED_C)
                self.wait(3); break 
            else: 
                self.update_status_text(f"Sink T={self.sink_node} Reached at Level L{self.levels[self.sink_node]}. Level Graph (LG) Built.", color=GREEN_A)
                self.wait(0.5)
                self.update_status_text("Isolating LG: Highlighting valid forward edges, dimming others.", play_anim=True)
                
                lg_edge_anims_iso = []; non_lg_edge_anims_iso = []
                for (u_lg,v_lg), edge_mo_lg in self.edge_mobjects.items():
                    res_cap_lg = self.capacities.get((u_lg,v_lg),0)-self.flow.get((u_lg,v_lg),0)
                    is_lg_edge = (self.levels.get(u_lg,-1)!=-1 and self.levels.get(v_lg,-1)!=-1 and \
                                    self.levels[v_lg]==self.levels[u_lg]+1 and res_cap_lg > 0 )
                    
                    label_mobj_or_grp_iso = self.edge_label_groups.get((u_lg,v_lg))
                    is_pure_rev = (u_lg,v_lg) not in self.original_edge_tuples

                    target_opacity_iso = 0
                    target_label_opacity_iso = 0

                    if is_lg_edge:
                        target_opacity_iso = 1.0
                        target_label_opacity_iso = 1.0
                        edge_c = LEVEL_COLORS[self.levels[u_lg]%len(LEVEL_COLORS)] 
                        lg_edge_anims_iso.append(edge_mo_lg.animate.set_stroke(opacity=target_opacity_iso, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(edge_c))
                        if label_mobj_or_grp_iso:
                            if isinstance(label_mobj_or_grp_iso, VGroup):
                                for part in label_mobj_or_grp_iso.submobjects: lg_edge_anims_iso.append(part.animate.set_opacity(target_label_opacity_iso))
                            else:
                                lg_edge_anims_iso.append(label_mobj_or_grp_iso.animate.set_opacity(target_label_opacity_iso))
                    else: 
                        if is_pure_rev: 
                            target_opacity_iso = 0
                            target_label_opacity_iso = 0
                        else: 
                            target_opacity_iso = DIMMED_OPACITY
                            target_label_opacity_iso = DIMMED_OPACITY
                        
                        non_lg_edge_anims_iso.append(edge_mo_lg.animate.set_stroke(opacity=target_opacity_iso, color=DIMMED_COLOR if not is_pure_rev else REVERSE_EDGE_COLOR))
                        if label_mobj_or_grp_iso:
                            if isinstance(label_mobj_or_grp_iso, VGroup):
                                for part in label_mobj_or_grp_iso.submobjects: non_lg_edge_anims_iso.append(part.animate.set_opacity(target_label_opacity_iso))
                            else:
                                non_lg_edge_anims_iso.append(label_mobj_or_grp_iso.animate.set_opacity(target_label_opacity_iso))
                
                if non_lg_edge_anims_iso + lg_edge_anims_iso: 
                    self.play(AnimationGroup(*(non_lg_edge_anims_iso + lg_edge_anims_iso), lag_ratio=0.05), run_time=0.75)
                self.wait(1)
                self.update_status_text("Level Graph Isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True)
                self.wait(1)

                flow_this_phase = self.animate_dfs_path_finding_phase() 
                self.max_flow_value += flow_this_phase

                self.update_phase_text(f"End of Dinitz Phase {self.current_phase_num}. Total Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.wait(1.5)

                if flow_this_phase == 0:
                     self.update_status_text(f"No augmenting flow found in this LG. Max Flow: {self.max_flow_value:.1f}. Algorithm terminates.", color=YELLOW_C, play_anim=True)
                     self.wait(3); break 
                else: 
                     self.update_status_text(f"Blocking flow of {flow_this_phase:.1f} found. Current Max Flow: {self.max_flow_value:.1f}.", color=BLUE_A, play_anim=True)
                     self.wait(1.5) 
        
        self.update_section_title("3. Algorithm Complete", play_anim=True)
        final_mobjects_to_keep_list_end = [
            self.main_title, self.current_section_title_mobj, self.phase_text_mobj, 
            self.algo_status_mobj, self.level_display_vgroup 
        ]
        mobjects_to_fade_out_finally = Group()
        for mobj in self.mobjects:
            is_kept = any(mobj is kept_item or (isinstance(kept_item, VGroup) and mobj in kept_item.submobjects) for kept_item in final_mobjects_to_keep_list_end)
            if not is_kept and mobj is not None:
                 mobjects_to_fade_out_finally.add(mobj)
        
        if mobjects_to_fade_out_finally.submobjects:
            self.play(FadeOut(mobjects_to_fade_out_finally), run_time=1.5)
        self.wait(3)
