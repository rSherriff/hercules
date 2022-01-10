from actions.actions import Action, CloseSummarySectionAction
from ui.ui import UI, Button


class StatueEndedUI(UI):
    def __init__(self, section):
        super().__init__(section)

        self.summary_button = Button(37, 26, 10, 10, click_action=None, tiles=None)
        self.elements.append(self.summary_button)