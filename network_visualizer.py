from manim import *
from typing import Dict, List, Tuple
from .dinitz_config import DinitzConfig
from .network_data import NetworkData

class NetworkVisualizer:
    """Handles visualization of the network graph"""
    
    def __init__(self, scene, config: DinitzConfig, network_data: NetworkData):
        self.scene = scene
        self.config = config
        self.network_data = network_data
        
        # Mobject storage
        self.node_mobjects = {}
        self.edge_mobjects = {}
        self.edge_capacity_text_mobjects = {}
        self.edge_flow_val_text_mobjects = {}
        self.edge_slash_text_mobjects = {}
        self.source_ring_mobj = None
        self.sink_ring_mobj = None
        self.network_display_group = None
        
        # Manual label offsets for better positioning
        self.manual_label_offsets = {
            (3,4): DOWN*0.1, (6,8): DOWN*0.1, (5,8): UP*0.15, (1,3): DOWN*0.15, (4,6): UP*0.15,
            (1,2): LEFT*0.05+UP*0.05, (1,4): LEFT*0.05+DOWN*0.05, (6,9): DOWN*0.05+RIGHT*0.05,
            (2,5): RIGHT*0.05+UP*0.05, (3,5): RIGHT*0.05+DOWN*0.05, (5,7): LEFT*0.05+UP*0.05, (8,10): UP*0.1
        }
    
    def create_nodes(self) -> VGroup:
        """Create and animate node creation"""
        nodes_vgroup = VGroup()
        
        for v_id in self.network_data.vertices:
            dot = Dot(
                point=self.network_data.layout[v_id], 
                radius=self.config.NODE_RADIUS, 
                color=self.config.DEFAULT_NODE_COLOR, 
                z_index=2, 
                stroke_color=BLACK, 
                stroke_width=self.config.NODE_STROKE_WIDTH
            )
            label = Text(
                str(v_id), 
                font_size=self.config.NODE_LABEL_FONT_SIZE, 
                weight=BOLD
            ).move_to(dot.get_center()).set_z_index(3)
            
            self.node_mobjects[v_id] = VGroup(dot, label)
            nodes_vgroup.add(self.node_mobjects[v_id])
        
        self.scene.play(
            LaggedStart(
                *[GrowFromCenter(self.node_mobjects[vid]) for vid in self.network_data.vertices], 
                lag_ratio=0.05
            ), 
            run_time=self.config.SLOW_ANIMATION_TIME
        )
        
        return nodes_vgroup
    
    def create_edges(self) -> VGroup:
        """Create and animate edge creation"""
        edges_vgroup = VGroup()
        edge_grow_anims = []
        
        for u, v, cap in self.network_data.edges:
            n_u_dot = self.node_mobjects[u][0]
            n_v_dot = self.node_mobjects[v][0]
            
            arrow = Arrow(
                n_u_dot.get_center(), 
                n_v_dot.get_center(), 
                buff=self.config.NODE_RADIUS, 
                stroke_width=self.config.EDGE_STROKE_WIDTH, 
                color=self.config.DEFAULT_EDGE_COLOR, 
                max_tip_length_to_length_ratio=0.2, 
                tip_length=self.config.ARROW_TIP_LENGTH, 
                z_index=0
            )
            
            self.edge_mobjects[(u, v)] = arrow
            edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        
        self.scene.play(
            LaggedStart(*edge_grow_anims, lag_ratio=0.05), 
            run_time=self.config.SLOW_ANIMATION_TIME
        )
        
        return edges_vgroup
    
    def create_capacity_labels(self) -> VGroup:
        """Create and animate capacity labels"""
        cap_labels_vgroup = VGroup()
        cap_write_anims = []
        
        for u, v, cap in self.network_data.edges:
            arrow = self.edge_mobjects[(u, v)]
            perp_dir = rotate_vector(arrow.get_unit_vector(), TAU/4)
            pos = arrow.get_center() + perp_dir * 0.30
            
            if (u, v) in self.manual_label_offsets:
                pos = arrow.get_center() + self.manual_label_offsets[(u, v)] + perp_dir * 0.1
            
            cap_text = Text(
                str(cap), 
                font_size=self.config.EDGE_CAPACITY_LABEL_FONT_SIZE, 
                color=self.config.LABEL_TEXT_COLOR
            ).move_to(pos).set_z_index(1)
            
            self.edge_capacity_text_mobjects[(u, v)] = cap_text
            cap_labels_vgroup.add(cap_text)
            cap_write_anims.append(Write(cap_text))
        
        if cap_write_anims:
            self.scene.play(
                LaggedStart(*cap_write_anims, lag_ratio=0.05), 
                run_time=self.config.SLOW_ANIMATION_TIME
            )
        
        return cap_labels_vgroup
    
    def create_flow_labels(self) -> VGroup:
        """Create and animate flow labels (0/capacity format)"""
        flow_prefixes_vgroup = VGroup()
        flow_prefix_anims = []
        
        for u, v, cap in self.network_data.edges:
            cap_text_mobj = self.edge_capacity_text_mobjects[(u, v)]
            
            flow_val_mobj = Text(
                "0", 
                font_size=self.config.EDGE_FLOW_PREFIX_FONT_SIZE, 
                color=self.config.LABEL_TEXT_COLOR
            )
            slash_mobj = Text(
                "/", 
                font_size=self.config.EDGE_FLOW_PREFIX_FONT_SIZE, 
                color=self.config.LABEL_TEXT_COLOR
            )
            
            slash_mobj.next_to(cap_text_mobj, LEFT, buff=self.config.BUFF_VERY_SMALL, aligned_edge=DOWN)
            flow_val_mobj.next_to(slash_mobj, LEFT, buff=self.config.BUFF_VERY_SMALL, aligned_edge=DOWN)
            
            self.edge_flow_val_text_mobjects[(u, v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u, v)] = slash_mobj
            
            flow_prefixes_vgroup.add(flow_val_mobj, slash_mobj)
            flow_prefix_anims.extend([Write(flow_val_mobj), Write(slash_mobj)])
        
        if flow_prefix_anims:
            self.scene.play(
                LaggedStart(*flow_prefix_anims, lag_ratio=0.03), 
                run_time=self.config.SLOW_ANIMATION_TIME
            )
        
        return flow_prefixes_vgroup
    
    def create_source_sink_rings(self, scale_factor: float = 1.0):
        """Create rings around source and sink nodes"""
        s_dot = self.node_mobjects[self.network_data.source][0]
        t_dot = self.node_mobjects[self.network_data.sink][0]
        
        scaled_s_radius = (s_dot.width / 2) * scale_factor
        scaled_t_radius = (t_dot.width / 2) * scale_factor

        self.source_ring_mobj = Circle(
            radius=scaled_s_radius + self.config.RING_RADIUS_OFFSET, 
            color=self.config.RING_COLOR, 
            stroke_width=self.config.RING_STROKE_WIDTH
        ).move_to(s_dot.get_center()).set_z_index(self.config.RING_Z_INDEX)
        
        self.sink_ring_mobj = Circle(
            radius=scaled_t_radius + self.config.RING_RADIUS_OFFSET, 
            color=self.config.RING_COLOR, 
            stroke_width=self.config.RING_STROKE_WIDTH
        ).move_to(t_dot.get_center()).set_z_index(self.config.RING_Z_INDEX)
        
        self.scene.play(
            Create(self.source_ring_mobj), 
            Create(self.sink_ring_mobj), 
            run_time=0.75
        )
    
    def build_complete_network(self, scale_factor: float = 1.6) -> VGroup:
        """Build the complete network visualization"""
        nodes_vgroup = self.create_nodes()
        edges_vgroup = self.create_edges()
        cap_labels_vgroup = self.create_capacity_labels()
        flow_prefixes_vgroup = self.create_flow_labels()
        
        self.network_display_group = VGroup(
            nodes_vgroup, edges_vgroup, cap_labels_vgroup, flow_prefixes_vgroup
        )
        
        # Scale and position the network
        temp_scaled_network = self.network_display_group.copy().scale(scale_factor)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network.height / 2) + self.config.BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        
        self.scene.play(
            self.network_display_group.animate.scale(scale_factor).move_to(target_position)
        )
        
        self.create_source_sink_rings(scale_factor)
        
        return self.network_display_group
    
    def update_flow_display(self, u: int, v: int, new_flow: int):
        """Update the flow display for a specific edge"""
        if (u, v) in self.edge_flow_val_text_mobjects:
            old_flow_text = self.edge_flow_val_text_mobjects[(u, v)]
            new_flow_text = Text(
                str(new_flow), 
                font_size=self.config.EDGE_FLOW_PREFIX_FONT_SIZE, 
                color=self.config.LABEL_TEXT_COLOR
            ).move_to(old_flow_text.get_center())
            
            self.scene.play(Transform(old_flow_text, new_flow_text))
            self.edge_flow_val_text_mobjects[(u, v)] = new_flow_text
    
    def highlight_node(self, node_id: int, color, scale: float = 1.1):
        """Highlight a specific node"""
        node_dot = self.node_mobjects[node_id][0]
        node_label = self.node_mobjects[node_id][1]
        
        animations = [node_dot.animate.set_color(color).scale(scale)]
        
        # Adjust label color based on background
        rgb_c = color_to_rgb(color)
        label_color = BLACK if sum(rgb_c) > 1.5 else WHITE
        animations.append(node_label.animate.set_color(label_color))
        
        return animations
    
    def highlight_edge(self, u: int, v: int, color, width: float = None):
        """Highlight a specific edge"""
        if (u, v) in self.edge_mobjects:
            edge = self.edge_mobjects[(u, v)]
            width = width or self.config.LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH
            return edge.animate.set_color(color).set_stroke(width=width)
        return None
    
    def dim_edge(self, u: int, v: int):
        """Dim a specific edge"""
        if (u, v) in self.edge_mobjects:
            edge = self.edge_mobjects[(u, v)]
            return edge.animate.set_stroke(opacity=self.config.DIMMED_OPACITY, color=self.config.DIMMED_COLOR)
        return None