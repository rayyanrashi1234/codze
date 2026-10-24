# ui_components.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation

class GlassCard(BoxLayout):
    """A semi-transparent card with a subtle neon border"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 15
        self.spacing = 10
        with self.canvas.before:
            Color(0.12, 0.15, 0.20, 0.85) # Dark slate background
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15,])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        with self.canvas.after:
            Color(0.4, 0.98, 0.94, 0.3) # Cyan border
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[15,], width=1.5)
        self.bind(pos=self.update_border, size=self.update_border)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_border(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size

class NeonButton(Button):
    """A glowing button with custom colors"""
    def __init__(self, color_hex="#66FCF1", **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = (1, 1, 1, 1)
        self.font_size = '15sp'
        self.bold = True
        
        # Parse hex color to RGB
        r = int(color_hex[1:3], 16) / 255.0
        g = int(color_hex[3:5], 16) / 255.0
        b = int(color_hex[5:7], 16) / 255.0
        
        with self.canvas.before:
            Color(r, g, b, 0.15)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10,])
            Color(r, g, b, 1)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 10), width=1.5)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], 10)

class PulseDot(Widget):
    """A pulsing circle to indicate live status"""
    def __init__(self, color_hex="#00FF00", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (15, 15)
        
        r = int(color_hex[1:3], 16) / 255.0
        g = int(color_hex[3:5], 16) / 255.0
        b = int(color_hex[5:7], 16) / 255.0
        
        with self.canvas:
            Color(r, g, b, 0.4)
            self.glow = Ellipse(pos=self.pos, size=self.size)
            Color(r, g, b, 1)
            self.dot = Ellipse(pos=self.pos, size=self.size)
            
        self.bind(pos=self.update_pos)
        self.start_pulse()
        
    def update_pos(self, *args):
        self.glow.pos = self.pos
        self.dot.pos = self.pos
        
    def start_pulse(self):
        anim = Animation(size=(25, 25), pos=(self.x - 5, self.y - 5), duration=0.8) + \
               Animation(size=(15, 15), pos=self.pos, duration=0.8)
        anim.repeat = True
        anim.start(self.glow)