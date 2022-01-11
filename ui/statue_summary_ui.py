from actions.actions import CloseSummarySectionAction, HideSummarySectionAction
from ui.ui import UI, Button


class StatueSummaryUI(UI):
    def __init__(self, section):
        super().__init__(section)

        tiles = section.tiles["graphic"][2:8,26:29]
        button = Button(2, 26, 6, 3, HideSummarySectionAction(self.section.engine), tiles)
        self.elements.append(button)

        tiles = section.tiles["graphic"][37:47,26:29]
        button = Button(37, 26, 10, 3, CloseSummarySectionAction(self.section.engine), tiles)
        self.elements.append(button)