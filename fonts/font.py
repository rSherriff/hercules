
from image import Image

class Font():
    def __init__(self, filepath):

        #All numbers are set up fro a font just consisting of numbers!
        self.width = 39
        self.height = 6

        self.char_width = 3
        self.char_height = 6

        self.font_image = Image(self.width, self.height, "images/" + filepath + ".xp")

    def get_character(self, char):
        char = ord(char)
        if char >= ord('0') and char <= ord('9'):
            index = char - 48 #48 is character 0
            index *= self.char_width
            return self.font_image.tiles[index : index + self.char_width, 0 : self.char_height]["graphic"]
        if char == ord('-'):
            return self.font_image.tiles[30 : 30 + self.char_width, 0 : self.char_height]["graphic"]
