import pygame

from base_classes import drawable, hitbox

class button(drawable, hitbox):
    def __init__(self, text, coords, size, screen, font, font_color, background):
        drawable.__init__(self, coords, size, screen, (0,0,0))
        hitbox.__init__(self, coords, size)

        self.background = background
        self.font = font
        self.text = text
        self.rendered_text = self.font.render(self.text, True, font_color)
        self.font_offset = 30
        self.clicked = False

    def draw(self):
        super().draw_frame(self.background)
        self.screen.blit(self.rendered_text, (self.x+self.font_offset, self.y))

    

