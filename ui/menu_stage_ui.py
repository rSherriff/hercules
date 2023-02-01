from actions.actions import  ChangeMenuStageAction, MenuHoverLevelAction, MenuSelectLevelAction
from ui.ui import UI, Button


class MenuStageUI(UI):
    def __init__(self, section, tiles):
        super().__init__(section)

        self.stage_buttons = []

        bd = [1, 23, 4, 1]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        left_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=ChangeMenuStageAction(self.section.engine, -1), tiles=button_tiles)
        self.stage_buttons.append(left_button)

        
        bd = [46, 23, 4, 1]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        right_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=ChangeMenuStageAction(self.section.engine, 1), tiles=button_tiles)
        self.stage_buttons.append(right_button)

        self.tiles = tiles


    def setup_level_buttons(self, start_pos, demo):
        self.elements.clear()

        if not demo:
            self.elements += self.stage_buttons

        bd = [start_pos[0], start_pos[1], 34, 1]
        for i in range(0,6):
            button_tiles = self.tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
            level_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=MenuSelectLevelAction(self.section.engine, i), tiles=button_tiles)
            level_button.set_hover_action(MenuHoverLevelAction(self.section.engine, i))
            self.elements.append(level_button)

            bd[1] += 2

        