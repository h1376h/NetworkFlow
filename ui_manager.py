from manim import *
from .dinitz_config import DinitzConfig

class UIManager:
    """Manages UI elements like titles, status text, and level display"""
    
    def __init__(self, scene, config: DinitzConfig):
        self.scene = scene
        self.config = config
        self.main_title = None
        self.current_section_title_mobj = None
        self.phase_text_mobj = None
        self.algo_status_mobj = None
        self.info_texts_group = None
        self.level_display_vgroup = None
        self.fixed_info_texts_top_y = None
    
    def setup_titles_and_placeholders(self, title: str = "Visualizing Dinitz's Algorithm"):
        """Setup main title and placeholder texts"""
        # Main Title Setup
        self.main_title = Text(title, font_size=self.config.MAIN_TITLE_FONT_SIZE)
        self.main_title.move_to(self.config.TOP_CENTER_ANCHOR)
        self.scene.add(self.main_title)
        self.scene.play(Write(self.main_title), run_time=self.config.DEFAULT_ANIMATION_TIME)
        self.scene.wait(0.5)
        
        # Animate Main Title to Corner
        self.scene.play(
            self.main_title.animate.scale(self.config.MAIN_TITLE_SMALL_SCALE)
            .to_corner(UL, buff=self.config.BUFF_SMALL*1.5)
        )
        self.scene.wait(0.2)

        # Info Texts Setup
        self.current_section_title_mobj = Text("", font_size=self.config.SECTION_TITLE_FONT_SIZE, weight=BOLD)
        self.phase_text_mobj = Text("", font_size=self.config.PHASE_TEXT_FONT_SIZE, weight=BOLD)
        self.algo_status_mobj = Text("", font_size=self.config.STATUS_TEXT_FONT_SIZE)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj
        ).set_z_index(5)
        
        self.info_texts_group.arrange(DOWN, aligned_edge=LEFT, buff=self.config.BUFF_MED)
        
        self.fixed_info_texts_top_y = self.main_title.get_bottom()[1] - self.config.BUFF_LARGE
        current_center_y = self.fixed_info_texts_top_y - (self.info_texts_group.height / 2)
        self.info_texts_group.move_to(np.array([0, current_center_y, 0]))
        
        self.scene.add(self.info_texts_group)

        # Level display setup
        self.level_display_vgroup = VGroup().set_z_index(5)
        self.level_display_vgroup.to_corner(UR, buff=self.config.BUFF_LARGE)
        self.scene.add(self.level_display_vgroup)
    
    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        """Animate text updates"""
        old_text_had_actual_content = isinstance(old_mobj, Text) and old_mobj.text != ""
        animations_to_play = []
        
        if old_text_had_actual_content:
            animations_to_play.append(FadeOut(old_mobj, run_time=0.35))
        
        if new_text_content_str != "":
            animations_to_play.append(FadeIn(new_mobj, run_time=0.35, shift=ORIGIN))

        if animations_to_play:
            self.scene.play(*animations_to_play)
    
    def _update_text_generic(self, text_attr_name, new_text_str, font_size, weight, color, play_anim=True):
        """Generic text update method"""
        old_mobj = getattr(self, text_attr_name)
        was_placeholder = (old_mobj.text == "")

        new_mobj = Text(new_text_str, font_size=font_size, weight=weight, color=color)

        try:
            idx = self.info_texts_group.submobjects.index(old_mobj)
            self.info_texts_group.remove(old_mobj)
            
            if was_placeholder and old_mobj in self.scene.mobjects:
                self.scene.remove(old_mobj)
            
            self.info_texts_group.insert(idx, new_mobj)
        except ValueError:
            if old_mobj in self.scene.mobjects:
                self.scene.remove(old_mobj)
            self.info_texts_group.add(new_mobj)

        setattr(self, text_attr_name, new_mobj)
        
        self.info_texts_group.arrange(DOWN, aligned_edge=LEFT, buff=self.config.BUFF_MED)

        if hasattr(self, 'fixed_info_texts_top_y'):
            new_center_y = self.fixed_info_texts_top_y - (self.info_texts_group.height / 2)
            self.info_texts_group.move_to(np.array([0, new_center_y, 0]))
            self.scene.bring_to_front(self.info_texts_group)
        
        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_str)
        else:
            if not was_placeholder and old_mobj in self.scene.mobjects:
                self.scene.remove(old_mobj)
    
    def update_section_title(self, text_str, play_anim=True):
        self._update_text_generic("current_section_title_mobj", text_str, 
                                self.config.SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("phase_text_mobj", text_str, 
                                self.config.PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("algo_status_mobj", text_str, 
                                self.config.STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim)
    
    def add_level_display(self, level: int, nodes: List[int]):
        """Add level information to the display"""
        color = self.config.LEVEL_COLORS[level % len(self.config.LEVEL_COLORS)]
        nodes_str = ", ".join(map(str, sorted(nodes)))
        
        level_prefix = Text(f"L{level}:", font_size=self.config.LEVEL_TEXT_FONT_SIZE, color=color)
        level_nodes = Text(f" {{{nodes_str}}}", font_size=self.config.LEVEL_TEXT_FONT_SIZE, color=WHITE)
        level_group = VGroup(level_prefix, level_nodes).arrange(RIGHT, buff=self.config.BUFF_VERY_SMALL)
        
        self.level_display_vgroup.add(level_group)
        self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=self.config.BUFF_SMALL)
        self.level_display_vgroup.to_corner(UR, buff=self.config.BUFF_LARGE)
        
        # Adjust width if too wide
        max_width = config.frame_width * 0.30
        if self.level_display_vgroup.width > max_width:
            self.level_display_vgroup.stretch_to_fit_width(max_width)
            self.level_display_vgroup.to_corner(UR, buff=self.config.BUFF_LARGE)
        
        self.scene.play(Write(level_group))
        return level_group