from ui.ui import UI, Button, Tooltip

from actions.actions import CloseConfirmationDialog


class ConfirmationUI(UI):
    def __init__(self, section, x, y, tiles):
        super().__init__(section, x, y)
        self.elements = list()

        bd = [11, 4, 7, 5]  # Button Dimensions
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.confirm_button = Button(x=bd[0], y=bd[1], width=bd[2],
                                height=bd[3], click_action=None, tiles=button_tiles)
        self.add_element(self.confirm_button)

        confirm_close_button = Button(x=bd[0], y=bd[1], width=bd[2], height=bd[3], click_action=CloseConfirmationDialog(
            self.section.engine), tiles=button_tiles)
        self.add_element(confirm_close_button)

        bd = [19, 4, 7, 5]
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        close_button = Button(x=bd[0], y=bd[1], width=bd[2], height=bd[3], click_action=CloseConfirmationDialog(
            self.section.engine), tiles=button_tiles)
        self.add_element(close_button)

    def reset(self, confirmation_action):
        self.confirm_button.set_action(confirmation_action)
