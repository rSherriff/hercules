from actions.actions import CloseSummarySectionAction, HideSummarySectionAction
from ui.ui import UI, Button


class StatueSummaryUI(UI):
    def __init__(self, section):
        super().__init__(section)

        tiles = section.tiles["graphic"][2:12,10:20]
        close_button = Button(2, 10, 10, 10, CloseSummarySectionAction(self.section.engine), tiles)
        self.elements.append(close_button)

        tiles = section.tiles["graphic"][2:12,10:20]
        close_button = Button(20, 10, 10, 10, HideSummarySectionAction(self.section.engine), tiles)
        self.elements.append(close_button)