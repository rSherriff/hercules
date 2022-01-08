
import numpy as np
import tcod
from tcod import Console

from sections.section import Section
from ui.statue_summary_ui import StatueSummaryUI


class StatueSummarySection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      
        self.summary = None

        self.ui = StatueSummaryUI(self)

    def update(self):
        pass
    
    def render(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        temp_console.print(1,1, self.summary.level["name"], (255,255,255))
        temp_console.blit(console, src_x=1, src_y=1, dest_x=1, dest_y=1, width=25, height=1)           

        temp_console.print(1,2, "Mistakes: " + str(self.summary.mistakes), (255,255,255))
        temp_console.blit(console, src_x=1, src_y=2, dest_x=1, dest_y=2, width=12, height=1)

    def setup(self, summary):
        self.summary = summary

    def mousedown(self,button,x,y):
        pass

    def keydown(self, key):
        pass
