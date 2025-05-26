from manim import *

class DinitzConfig:
    """Configuration class for Dinitz algorithm visualization"""
    
    # Visual Constants
    NODE_RADIUS = 0.28
    NODE_STROKE_WIDTH = 1.5
    EDGE_STROKE_WIDTH = 3.5
    ARROW_TIP_LENGTH = 0.18
    
    # Font Sizes
    MAIN_TITLE_FONT_SIZE = 38
    SECTION_TITLE_FONT_SIZE = 28
    PHASE_TEXT_FONT_SIZE = 22
    STATUS_TEXT_FONT_SIZE = 20
    NODE_LABEL_FONT_SIZE = 16
    EDGE_CAPACITY_LABEL_FONT_SIZE = 15
    EDGE_FLOW_PREFIX_FONT_SIZE = 15
    LEVEL_TEXT_FONT_SIZE = 18
    
    # Layout
    MAIN_TITLE_SMALL_SCALE = 0.65
    BUFF_VERY_SMALL = 0.05
    BUFF_SMALL = 0.1
    BUFF_MED = 0.25
    BUFF_LARGE = 0.4
    BUFF_XLARGE = 0.6
    
    # Colors
    RING_COLOR = YELLOW_C
    RING_STROKE_WIDTH = 3.5
    RING_RADIUS_OFFSET = 0.1
    RING_Z_INDEX = 4
    
    LEVEL_COLORS = [RED_D, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK]
    DEFAULT_NODE_COLOR = BLUE_E
    DEFAULT_EDGE_COLOR = GREY_C
    LABEL_TEXT_COLOR = DARK_GREY
    LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 4.5
    DIMMED_OPACITY = 0.20
    DIMMED_COLOR = GREY_BROWN
    
    # Animation
    DEFAULT_ANIMATION_TIME = 1.0
    FAST_ANIMATION_TIME = 0.5
    SLOW_ANIMATION_TIME = 1.5
    
    @property
    def TOP_CENTER_ANCHOR(self):
        return UP * (config.frame_height / 2 - self.BUFF_MED)