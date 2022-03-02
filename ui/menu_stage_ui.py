from actions.actions import  ChangeMenuStageAction, MenuHoverLevelAction, MenuSelectLevelAction
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

        self.tiles = tiles


    def setup_level_buttons(self, start_pos):
        self.elements = self.elements[:1]

        bd = [start_pos[0], start_pos[1], 34, 1]
        for i in range(0,6):
            button_tiles = self.tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
            self.level_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=MenuSelectLevelAction(self.section.engine, i), tiles=button_tiles)
            self.level_button.set_hover_action(MenuHoverLevelAction(self.section.engine, i))
            self.elements.append(self.level_button)

            bd[1] += 2

        