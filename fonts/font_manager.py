from fonts.font import Font

class FontManager():
    def __init__(self):
        self.fonts = {}

    def add_font(self, fontname):
        self.fonts[fontname] = Font(fontname)

    def get_font(self, fontname):
        return self.fonts[fontname]