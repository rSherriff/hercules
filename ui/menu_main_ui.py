from actions.actions import EscapeAction, EnterStageSelectAction, EnterOptionsAction
from ui.ui import UI, Button


class MenuMainUI(UI):
    def __init__(self, section, tiles, demo):
        super().__init__(section)

        bd = [21, 16, 9, 3]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.start_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=EnterStageSelectAction(self.section.engine), tiles=button_tiles, normal_bg=(191,191,191), highlight_bg=(128,128,128))
        self.elements.append(self.start_button)

        if not demo:

            bd = [21, 20, 9, 3]  # Button Dimensions
            button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
            self.start_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=EnterOptionsAction(self.section.engine), tiles=button_tiles, normal_bg=(191,191,191), highlight_bg=(128,128,128))
            self.elements.append(self.start_button)

            bd = [21, 24, 9, 3]  # Button Dimensions
            button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
            self.quit_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=EscapeAction(self.section.engine), tiles=button_tiles, normal_bg=(191,191,191), highlight_bg=(128,128,128))
            self.elements.append(self.quit_button)
        