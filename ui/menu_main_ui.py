from actions.actions import EscapeAction, EnterStageSelectAction
from ui.ui import UI, Button


class MenuMainUI(UI):
    def __init__(self, section, tiles):
        super().__init__(section)

        bd = [21, 16, 9, 5]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.start_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=EnterStageSelectAction(self.section.engine), tiles=button_tiles)
        self.elements.append(self.start_button)

        
        bd = [21, 22, 9, 5]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.quit_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=EscapeAction(self.section.engine), tiles=button_tiles)
        self.elements.append(self.quit_button)
        