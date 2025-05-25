from manim import *
import collections

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.18

# Font Sizes - Standardized
MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28
PHASE_TEXT_FONT_SIZE = 22
STATUS_TEXT_FONT_SIZE = 20
NODE_LABEL_FONT_SIZE = 16 
EDGE_CAPACITY_LABEL_FONT_SIZE = 15 
EDGE_FLOW_PREFIX_FONT_SIZE = 15  
LEVEL_TEXT_FONT_SIZE = 18

MAIN_TITLE_SMALL_SCALE = 0.65

# Buffs for spacing
BUFF_VERY_SMALL = 0.05 
BUFF_SMALL = 0.1
BUFF_MED = 0.25
BUFF_LARGE = 0.4 

# Colors
LEVEL_COLORS = [RED_D, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK] 
DEFAULT_NODE_COLOR = BLUE_E 
DEFAULT_EDGE_COLOR = GREY_C 
LABEL_TEXT_COLOR = DARK_GREY 
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 4.5
DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

TOP_CENTER_ANCHOR = UP * (config.frame_height / 2 - BUFF_MED)

class DinitzAlgorithmVisualizer(Scene):
    def setup_titles_and_placeholders(self):
        self.main_title = Text("Visualizing Dinitz's Algorithm", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.move_to(TOP_CENTER_ANCHOR)
        self.play(Write(self.main_title), run_time=1)
        self.wait(0.5)
        self.play(self.main_title.animate.scale(MAIN_TITLE_SMALL_SCALE).to_corner(UL, buff=BUFF_SMALL*1.5))
        self.wait(0.2)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD)
        self.current_section_title_mobj.move_to(UP * (config.frame_height/2 * 0.75) ) 
        self.add(self.current_section_title_mobj)

        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE) 
        self.algo_status_mobj.next_to(self.current_section_title_mobj, DOWN, buff=BUFF_MED)
        self.add(self.algo_status_mobj) 
        self.algo_status_text_initialized_flag = False 

        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD)
        self.phase_text_mobj.next_to(self.current_section_title_mobj, DOWN, buff=BUFF_MED) 

    def update_section_title(self, text_str, play_anim=True): # Added play_anim flag
        new_title_mobj = Text(text_str, font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD)
        new_title_mobj.move_to(self.current_section_title_mobj.get_center()) 
        
        current_mobj_to_transform = self.current_section_title_mobj
        if play_anim:
            self.play(Transform(current_mobj_to_transform, new_title_mobj))
        else:
            self.remove(current_mobj_to_transform)
            self.add(new_title_mobj)
        self.current_section_title_mobj = new_title_mobj # Update reference to the new mobject state
        
        # Ensure subsequent texts are repositioned if necessary
        self.phase_text_mobj.next_to(self.current_section_title_mobj, DOWN, buff=BUFF_MED, aligned_edge=LEFT)
        self.algo_status_mobj.next_to(self.phase_text_mobj, DOWN, buff=BUFF_SMALL, aligned_edge=LEFT) # Or next_to section_title/phase_text

    def update_status_text(self, text_str, color=WHITE, play_anim=True, ref_mobj=None, buff=BUFF_MED, aligned_edge=LEFT):
        if ref_mobj is None: ref_mobj = self.phase_text_mobj # Default to placing below phase text
        
        new_text_mobj = Text(text_str, font_size=STATUS_TEXT_FONT_SIZE, color=color)
        new_text_mobj.next_to(ref_mobj, DOWN, buff=buff, aligned_edge=aligned_edge)
        
        current_mobj_to_transform = self.algo_status_mobj
        if play_anim:
            self.play(Transform(current_mobj_to_transform, new_text_mobj))
        else:
            self.remove(current_mobj_to_transform)
            self.add(new_text_mobj)
        self.algo_status_mobj = new_text_mobj # Update reference

    def construct(self):
        self.setup_titles_and_placeholders()

        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11))
        self.edges_with_capacity_list = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        self.capacities = collections.defaultdict(int); self.flow = collections.defaultdict(int); 
        self.adj = collections.defaultdict(list) 
        for u,v,cap in self.edges_with_capacity_list: self.capacities[(u,v)]=cap; self.adj[u].append(v)
        
        self.graph_layout = {
            1: [-3,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }
        self.node_mobjects = {}; self.edge_mobjects = {}; 
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {}; 
        self.edge_slash_text_mobjects = {}   

        self.update_section_title("1. Building the Network")

        nodes_vgroup = VGroup() 
        self.update_status_text("Nodes Appear", ref_mobj=self.current_section_title_mobj)
        for i, v_id in enumerate(self.vertices_data):
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)
        
        edges_vgroup = VGroup()
        self.update_status_text("Edges Form Connections", ref_mobj=self.current_section_title_mobj)
        edge_grow_anims = []
        for u,v,cap in self.edges_with_capacity_list:
            n_u_dot = self.node_mobjects[u][0]; n_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS, stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow; edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)

        cap_labels_vgroup = VGroup()
        self.update_status_text("Capacities Defined", ref_mobj=self.current_section_title_mobj)
        cap_write_anims = []
        manual_label_offsets = {
            (3,4): DOWN*0.1, (6,8): DOWN*0.1, (5,8): UP*0.15, (1,3): DOWN*0.15, (4,6): UP*0.15,
            (1,2): LEFT*0.05+UP*0.05, (1,4): LEFT*0.05+DOWN*0.05, (6,9):DOWN*0.05+RIGHT*0.05,
            (2,5): RIGHT*0.05+UP*0.05, (3,5): RIGHT*0.05+DOWN*0.05, (5,7):LEFT*0.05+UP*0.05, (8,10): UP*0.1
        }
        for u,v,cap in self.edges_with_capacity_list:
            arrow = self.edge_mobjects[(u,v)]
            perp_dir = rotate_vector(arrow.get_unit_vector(), TAU/4)
            pos = arrow.get_center() + perp_dir * 0.30 
            if (u,v) in manual_label_offsets: pos = arrow.get_center() + manual_label_offsets[(u,v)] + perp_dir * 0.1
            cap_text = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR).move_to(pos).set_z_index(1)
            self.edge_capacity_text_mobjects[(u,v)] = cap_text; cap_labels_vgroup.add(cap_text)
            cap_write_anims.append(Write(cap_text))
        self.play(LaggedStart(*cap_write_anims, lag_ratio=0.05), run_time=1.5)

        flow_prefixes_vgroup = VGroup()
        self.update_status_text("Initial Flow: 0 / Capacity", ref_mobj=self.current_section_title_mobj)
        flow_prefix_anims_group = []
        for u,v,cap in self.edges_with_capacity_list:
            cap_text_mobj = self.edge_capacity_text_mobjects[(u,v)]
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj.next_to(cap_text_mobj, LEFT, buff=BUFF_VERY_SMALL, aligned_edge=DOWN)
            flow_val_mobj.next_to(slash_mobj, LEFT, buff=BUFF_VERY_SMALL, aligned_edge=DOWN)
            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            flow_prefixes_vgroup.add(flow_val_mobj, slash_mobj)
            flow_prefix_anims_group.append(Write(flow_val_mobj))
            flow_prefix_anims_group.append(Write(slash_mobj))
        self.play(LaggedStart(*flow_prefix_anims_group, lag_ratio=0.03), run_time=1.5)
        
        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, cap_labels_vgroup, flow_prefixes_vgroup)
        self.play(self.network_display_group.animate.scale(0.75).to_corner(DL, buff=BUFF_MED))
        # Corrected line: use self.algo_status_mobj
        self.play(FadeOut(self.algo_status_mobj)); self.algo_status_text_initialized_flag = False 
        self.wait(1)

        # --- Part B: Dynamic Dinitz Algorithm Animation ---
        self.update_section_title("2. Dinitz Algorithm Execution")
        self.levels = {v_id: -1 for v_id in self.vertices_data}; self.ptr = {v_id: 0 for v_id in self.vertices_data} 

        # Re-Add phase_text_mobj if it was faded or ensure it's correctly positioned and shown
        self.phase_text_mobj = Text("Phase 1", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD) # Recreate or ensure visible
        self.phase_text_mobj.next_to(self.current_section_title_mobj, DOWN, buff=BUFF_MED, aligned_edge=LEFT)
        self.play(Write(self.phase_text_mobj))
        self.update_status_text("Building Level Graph (BFS from S=1)", ref_mobj=self.phase_text_mobj)


        q_bfs = collections.deque(); self.levels = {v_id: -1 for v_id in self.vertices_data} 
        current_bfs_level_num = 0; self.levels[self.source_node] = current_bfs_level_num; q_bfs.append(self.source_node) 
        level_display_vgroup = VGroup().to_corner(DR, buff=BUFF_MED); self.add(level_display_vgroup)

        s_dot = self.node_mobjects[self.source_node][0]
        self.play(s_dot.animate.set_color(LEVEL_COLORS[0]).scale(1.1), run_time=0.5)
        l_p0 = Text(f"L{current_bfs_level_num}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
        l_n0 = Text(f" {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
        l0_vg = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL).align_to(level_display_vgroup,UP+LEFT)
        level_display_vgroup.add(l0_vg); self.play(Write(l0_vg))

        while q_bfs: 
            nodes_to_process = list(q_bfs); q_bfs.clear() 
            if not nodes_to_process: break
            target_level = self.levels[nodes_to_process[0]] + 1
            nodes_found_next_lvl_set = set(); node_color_anims = []

            for u in nodes_to_process: 
                ind_u = SurroundingRectangle(self.node_mobjects[u],color=YELLOW_C,buff=0.02,stroke_width=1.5, corner_radius=0.05)
                self.play(Create(ind_u), run_time=0.05)
                for v_n in self.adj[u]: 
                    res_cap = self.capacities[(u,v_n)]-self.flow.get((u,v_n),0)
                    if res_cap > 0 and self.levels[v_n] == -1: 
                        self.levels[v_n] = target_level; nodes_found_next_lvl_set.add(v_n); q_bfs.append(v_n) 
                        lvl_color = LEVEL_COLORS[target_level % len(LEVEL_COLORS)]
                        n_v_dot = self.node_mobjects[v_n][0]; n_v_lbl = self.node_mobjects[v_n][1]
                        node_color_anims.append(n_v_dot.animate.set_color(lvl_color).scale(1.1))
                        rgb_c = color_to_rgb(lvl_color); lbl_c = BLACK if sum(rgb_c)>1.5 else WHITE 
                        node_color_anims.append(n_v_lbl.animate.set_color(lbl_c))
                self.play(FadeOut(ind_u), run_time=0.05)
            
            if node_color_anims: self.play(*node_color_anims, run_time=0.4) # Reduced run_time

            edge_color_anims_lvl_links = []
            if nodes_found_next_lvl_set:
                for u_prev in nodes_to_process: 
                    for v_new in nodes_found_next_lvl_set: 
                        if v_new in self.adj[u_prev] and self.levels[v_new] == self.levels[u_prev]+1:
                            res_cap = self.capacities[(u_prev,v_new)]-self.flow.get((u_prev,v_new),0)
                            if res_cap > 0 :
                                edge_mo = self.edge_mobjects[(u_prev,v_new)]
                                edge_c = LEVEL_COLORS[self.levels[u_prev]%len(LEVEL_COLORS)] 
                                edge_color_anims_lvl_links.append(edge_mo.animate.set_color(edge_c).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
            if edge_color_anims_lvl_links: self.play(*edge_color_anims_lvl_links, run_time=0.4) # Reduced run_time

            if nodes_found_next_lvl_set:
                n_str = ", ".join(map(str, sorted(list(nodes_found_next_lvl_set))))
                l_px = Text(f"L{target_level}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[target_level%len(LEVEL_COLORS)])
                l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE) 
                l_vg = VGroup(l_px,l_nx).arrange(RIGHT,buff=BUFF_VERY_SMALL).next_to(level_display_vgroup[-1],DOWN,aligned_edge=LEFT,buff=BUFF_SMALL)
                level_display_vgroup.add(l_vg); self.play(Write(l_vg)); self.wait(0.3) # Reduced wait
            if not q_bfs: break
        
        final_bfs_stat_str = ""; final_bfs_stat_color = WHITE
        if self.levels[self.sink_node] == -1:
            final_bfs_stat_str = "Sink NOT Reached! Algorithm Terminates."; final_bfs_stat_color = RED
        else:
            final_bfs_stat_str = f"Sink Reached at L{self.levels[self.sink_node]}. Level Graph Built."; final_bfs_stat_color = GREEN
        self.update_status_text(final_bfs_stat_str, color=final_bfs_stat_color, ref_mobj=self.phase_text_mobj)
        if self.levels[self.sink_node] == -1: self.wait(3); self.play(*[FadeOut(mob) for mob in self.mobjects]); return 

        self.update_status_text("Isolating Level Graph Edges...", ref_mobj=self.phase_text_mobj)
        lg_edge_anims = []; non_lg_edge_anims = []
        for (u,v), edge_mo in self.edge_mobjects.items():
            is_lg_edge = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                          self.levels[v]==self.levels[u]+1 and \
                          (self.capacities[(u,v)]-self.flow.get((u,v),0)>0) ) 
            if is_lg_edge:
                lg_edge_anims.append(edge_mo.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]))
            else:
                non_lg_edge_anims.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR))
        if non_lg_edge_anims: self.play(*non_lg_edge_anims, run_time=0.5) # Reduced
        if lg_edge_anims: self.play(*lg_edge_anims, run_time=0.5) 
        self.wait(1)
        self.update_status_text("Level Graph Isolated. Ready for DFS.", color=GREEN, ref_mobj=self.phase_text_mobj)
        
        self.wait(3) # Shortened wait before cleanup
        mobjects_to_fade = Group(*self.mobjects)
        if mobjects_to_fade.submobjects: self.play(FadeOut(mobjects_to_fade))
        self.wait(1)