import tcod
from actions.actions import CloseNotificationDialog
from ui.notification_ui import NotificationUI

from sections.section import Section


class Notification(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int):
        super().__init__(engine, x, y, width, height, "notification_dialog.xp")

        self.text = ""
        self.ui = NotificationUI(self, x, y, self.tiles["graphic"])

    def setup(self, text, section):
        self.text = text
        close_action = CloseNotificationDialog(self.engine, section)
        self.ui.reset(close_action)

    def render(self, console):
        super().render(console)
        console.print_box(self.x,self.y+2,self.width,3,self.text, (255,255,255), alignment=tcod.CENTER)  
