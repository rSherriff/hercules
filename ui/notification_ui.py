from ui.ui import UI, Button, Tooltip

from actions.actions import  CloseNotificationDialog


class NotificationUI(UI):
    def __init__(self, section, x, y, tiles):
        super().__init__(section, x, y)
        self.elements = list()

        bd = [15, 5, 7, 3]
        button_tiles = tiles[bd[0]:bd[0] + bd[2], bd[1]:bd[1] + bd[3]]
        close_button = Button(x=bd[0], y=bd[1], width=bd[2], height=bd[3], click_action=CloseNotificationDialog(
            self.section.engine, None), tiles=button_tiles)
        self.add_element(close_button)

    def reset(self, confirmation_action):
        self.elements[0].set_action(confirmation_action)
