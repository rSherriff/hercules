from actions.actions import EnterMenuMainAction,ToggleFullScreenAction,SliderAction, ChangeVolumeAction
from ui.ui import UI, Button, Toggle, HorizontalSlider
from ui.ui_util_tiles import util_tiles

class MenuOptionsUI(UI):
    def __init__(self, section, tiles):
        super().__init__(section)

        bd = [18, 14, 14, 1]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.fullscreen_toggle = Toggle(x=bd[0], y=bd[1], width=bd[2],height=bd[3], 
                                is_on=self.section.engine.save_data["fullscreen"],
                                on_action=ToggleFullScreenAction(self.section.engine), 
                                off_action=ToggleFullScreenAction(self.section.engine), 
                                tiles=button_tiles, on_tiles=util_tiles[1:2,0:1], off_tiles=util_tiles[0:1,0:1],
                                response_x =13, response_y=0,
                                normal_bg=(191,191,191), highlight_bg=(128,128,128))

        self.elements.append(self.fullscreen_toggle)


        self.volume_slider = HorizontalSlider(19,19,13, util_tiles[2:3,0:1], SliderAction(self.section.engine,ChangeVolumeAction), value = self.section.engine.save_data["volume"])
        self.elements.append(self.volume_slider)

        bd = [21, 23, 9, 3]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.close_button = Button(x=bd[0], y=bd[1], width=bd[2],height=bd[3], click_action=EnterMenuMainAction(self.section.engine), tiles=button_tiles, normal_bg=(191,191,191), highlight_bg=(128,128,128))
        self.elements.append(self.close_button)


        