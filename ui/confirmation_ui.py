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

        self.confirm_close_button = Button(x=bd[0], y=bd[1], width=bd[2], height=bd[3], click_action=CloseConfirmationDialog(
            self.section.engine, None), tiles=button_tiles)
        self.add_element(self.confirm_close_button)

        bd = [19, 4, 7, 5]
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        self.close_button = Button(x=bd[0], y=bd[1], width=bd[2], height=bd[3], click_action=CloseConfirmationDialog(
            self.section.engine, None), tiles=button_tiles)
        self.add_element(self.close_button)

    def reset(self, confirmation_action, section):
        self.confirm_button.set_action(confirmation_action)

        close_action=CloseConfirmationDialog(self.section.engine, section)
        self.confirm_close_button.set_action(close_action)
        self.close_button.set_action(close_action)
