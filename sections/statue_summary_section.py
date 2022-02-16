
import json
import math
from enum import Enum, auto
from random import randrange
from threading import Timer

import numpy as np
import tcod
from pygame import mixer
from tcod import Console
from ui.statue_summary_ui import StatueSummaryUI

from sections.section import Section


class SummaryState(Enum):
    INACTIVE = auto()
    BEGINING = auto()
    SCORING = auto()
    END = auto()

class StatueSummarySection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        super().__init__(engine, x, y, width, height, xp_filepath)      
        self.summary = None

        with open ( "game_data/summary_layout.json" ) as f:
            self.layout = json.load(f)

        self.crown_unlocked_console = self.fill_crown_console("crown_unlocked")
        self.crown_empty_console = self.fill_crown_console("crown_empty")
        self.crown_locked_console = self.fill_crown_console("crown_locked")

        self.ui = StatueSummaryUI(self)

        self.crown_award_sounds = list()
        self.crown_award_sounds.append(mixer.Sound('Sounds/chisel1.wav'))
        self.crown_award_sounds.append(mixer.Sound('Sounds/chisel2.wav'))
        self.crown_award_sounds.append(mixer.Sound('Sounds/chisel3.wav'))
        self.crown_award_sounds.append(mixer.Sound('Sounds/chisel4.wav'))
        self.crown_award_sounds.append(mixer.Sound('Sounds/chisel5.wav'))

        self.reset()

    def reset(self):
        self.state = SummaryState.INACTIVE
        self.crowns_awarded = 0
        self.new_crowns = 0
        self.scoring_time = 0
        self.time_in_scoring = 0
        self.time_each_scoring = 1
        self.sounds_to_play = 0

    def update(self):
        pass
    
    def render(self, console):
        if self.state == SummaryState.BEGINING:
            self.render_begining(console)
        elif self.state == SummaryState.SCORING:
            self.render_scoring(console)
        elif self.state == SummaryState.END:
            self.render_end(console)

    def render_begining(self, console):
        self.render_static_info(console)
        self.render_crowns(console, self.crowns_awarded - self.new_crowns)
        self.render_total(console, self.engine.get_total_awarded_crowns() - self.new_crowns, 0)             

    def render_scoring(self, console):
        self.render_static_info(console)

        self.time_in_scoring += self.engine.get_delta_time()
        if self.time_in_scoring >= self.scoring_time:
            self.state == SummaryState.END
            self.render_end(console)
            return

        num_empty = math.ceil(self.time_in_scoring) + (self.crowns_awarded - self.new_crowns)
        num_crown = self.crowns_awarded - num_empty
        x,y= self.get_crown_position(num_crown)
        
        line = tcod.los.bresenham((x, y), (self.layout["total_x"], self.layout["total_y"])).tolist()
        point_to_print = line[int(len(line) * (self.time_in_scoring - math.floor(self.time_in_scoring)))]

        if self.sounds_to_play != num_crown:
            self.sounds_to_play -= 1
            self.crown_award_sounds[randrange(0,len(self.crown_award_sounds))].play()

        self.crown_unlocked_console.blit(console, dest_x=point_to_print[0], dest_y=point_to_print[1], width=self.layout["crown_width"], height=self.layout["crown_height"])

        self.render_crowns(console, num_empty)
        self.render_total(console, (self.engine.get_total_awarded_crowns() - self.crowns_awarded) + num_empty - 1, math.ceil(self.time_in_scoring) - 1)

    def render_end(self, console):
        self.render_static_info(console)
        self.render_crowns(console, self.crowns_awarded)
        self.render_total(console, self.engine.get_total_awarded_crowns(), self.new_crowns)

    def render_static_info(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        temp_console.print(0,0, self.summary.level["name"], (255,255,255))  
        temp_console.blit(console, dest_x=self.layout["title_x"], dest_y=self.layout["title_y"], width=len(self.summary.level["name"]), height=1)        

        temp_console.print(0,0, str(self.summary.faults), (255,255,255))
        temp_console.blit(console, dest_x=self.layout["faults_x"], dest_y=self.layout["faults_y"], width=len(str(self.summary.faults)), height=1)        

        cw = self.layout["crown_width"]
        ch = self.layout["crown_height"]

        temp_console.clear()
        bgw = cw * self.layout["num_crown_col"]
        bgh = ch * int(self.layout["num_crown_col"]/self.summary.level["num_crowns"])
        temp_console.draw_rect(0,0, bgw,bgh,ch = ord(" "), fg = (0,0,0))
        temp_console.blit(console,  dest_x=self.layout["crown_start_x"], dest_y=self.layout["crown_start_y"], width=bgw, height=bgh)

    def render_crowns(self, console, num_empty):
        cw = self.layout["crown_width"]
        ch = self.layout["crown_height"]

        for crown in range(0,self.summary.level["num_crowns"]):
            x,y= self.get_crown_position(crown)

            if crown >= self.crowns_awarded:
                self.crown_locked_console.blit(console, dest_x=x, dest_y=y, width=cw, height=ch)
            elif crown <= self.crowns_awarded and crown >= (self.crowns_awarded - num_empty):
                self.crown_empty_console.blit(console, dest_x=x, dest_y=y, width=cw, height=ch)
            else:
                self.crown_unlocked_console.blit(console, dest_x=x, dest_y=y, width=cw, height=ch)

    def render_total(self, console, total, new):
        temp_console = Console(width=5, height=1, order="F")

        temp_console.print(0,0, str(total), (255,255,255))  
        temp_console.blit(console, dest_x=self.layout["total_x"], dest_y=self.layout["total_y"], width=5, height=1)   

        temp_console.clear()
        temp_console.print(0,0, str(new), (255,255,255))  
        temp_console.blit(console, dest_x=self.layout["new_x"], dest_y=self.layout["new_y"], width=5, height=1)   

    def setup(self, summary):
        if self.state == SummaryState.INACTIVE:
            self.summary = summary
            self.state = SummaryState.BEGINING

            self.crowns_awarded = self.summary.level["num_crowns"]
            for allowed_fault in self.summary.level["allowed_faults"]:
                if self.summary.faults >= allowed_fault:
                    self.crowns_awarded -= 1
                else:
                    break
            self.crowns_awarded = max(self.crowns_awarded, self.engine.get_awarded_crowns(self.summary.level["name"]))

            self.new_crowns = max(0,self.crowns_awarded - self.engine.get_awarded_crowns(self.summary.level["name"]))
            self.scoring_time = self.new_crowns * self.time_each_scoring
            self.time_in_scoring = 0

            self.engine.award_crowns(self.new_crowns, self.crowns_awarded, self.summary.level["name"])

            self.sounds_to_play = self.crowns_awarded

            Timer(2.0, self.display_scores).start()

    def close(self):
        self.reset()

    def display_scores(self):
        self.state = SummaryState.SCORING

    def mousedown(self,button,x,y):
        pass

    def keydown(self, key):
        pass

    def fill_crown_console(self, crown_string):
        console =  Console(width=self.layout["crown_width"], height=self.layout["crown_height"], order="F")
        console.tiles_rgb[0:self.layout["crown_width"],0:self.layout["crown_height"]] = self.tiles[self.layout[crown_string+"_x"]:self.layout[crown_string+"_x"]+self.layout["crown_width"],
                                                                                                            self.layout[crown_string+"_y"]:self.layout[crown_string+"_y"]+self.layout["crown_height"]]["graphic"]
        return console

    def get_crown_position(self, num_crown):
        cw = self.layout["crown_width"]
        ch = self.layout["crown_height"]

        x = self.layout["crown_start_x"] + ((num_crown %  self.layout["num_crown_col"]) * cw)
        x += num_crown %  self.layout["num_crown_col"]

        y = self.layout["crown_start_y"] + (math.floor(num_crown / self.layout["num_crown_col"]) * ch) 
        y += math.floor(num_crown / self.layout["num_crown_col"])

        return x, y
