from actions.actions import  ChangeMenuStageAction
from ui.ui import UI, Button


class MenuStageUI(UI):
    def __init__(self, section, tiles):
        super().__init__(section)

        bd = [1, 23, 4, 1]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.left_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=ChangeMenuStageAction(self.section.engine, -1), tiles=button_tiles)
        self.elements.append(self.left_button)

        
        bd = [46, 23, 4, 1]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.right_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=ChangeMenuStageAction(self.section.engine, 1), tiles=button_tiles)
        self.elements.append(self.right_button)
        