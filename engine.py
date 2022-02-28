from __future__ import annotations

import json
import os
import random
from enum import Enum, auto
from threading import Timer

import tcod
from playsound import playsound
from pygame import mixer
from tcod.console import Console

from application_path import get_app_path
from effects.melt_effect import MeltWipeEffect, MeltWipeEffectType
from fonts.font_manager import FontManager
from input_handlers import EventHandler, MainGameEventHandler
from sections.confirmation import Confirmation
from sections.intro_section import IntroSection
from sections.menu_section import MenuSection
from sections.statue_section import StatueSection
from sections.statue_summary_section import StatueSummarySection
from utils.delta_time import DeltaTime


class GameState(Enum):
    INTRO = auto()
    MENU = auto()
    IN_GAME = auto()

class Engine:
    def __init__(self, teminal_width: int, terminal_height: int):

        mixer.init()
        mixer.music.set_volume(0.5)

        self.screen_width = teminal_width
        self.screen_height = terminal_height
        self.delta_time = DeltaTime()

        self.player = None

        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.mouse_location = (0, 0)

        self.setup_effects()
        self.setup_sections()

        self.tick_length = 2
        self.time_since_last_tick = -2

        self.state = GameState.INTRO

        self.font_manager = FontManager()
        self.font_manager.add_font("number_font")

        self.in_music_queue = False

        self.save_data = None
        if os.path.isfile("game_data/game_save.json"):
            with open("game_data/game_save.json") as f:
                self.save_data = json.load(f)
        else:
            self.save_data = dict()
            self.save_data["total_crowns"] = 0

        self.stage_music = {}
        with open ( "game_data/levels.json" ) as f:
            data = json.load(f)

            self.intro_sections["introSection"].load_splashes(data["intro_splashes"])

            for stage in data["stages"]:
                self.stage_music[stage["name"]] = {}
                self.stage_music[stage["name"]]["music"] = stage["music"]
                self.stage_music[stage["name"]]["music_volume"] = stage["music_volume"]


    def render(self, root_console: Console) -> None:
        """ Renders the game to console """
        for section_key, section_value in self.get_active_sections():
            if section_key not in self.disabled_sections:
                section_value.render(root_console)

        if self.full_screen_effect.in_effect == True:
            self.full_screen_effect.render(root_console)
        else:
            self.full_screen_effect.set_tiles(root_console.tiles_rgb)

        #root_console.print(40, 1, str(self.mouse_location), (255,255,255))

    def update(self):
        """ Engine update tick """
        for _, section in self.get_active_sections():
            section.update()

        self.delta_time.update_delta_time()

        if self.is_in_game():
            self.time_since_last_tick += self.get_delta_time()

            self.tick_length -= 0.0002
            if self.time_since_last_tick > self.tick_length and self.state == self.is_in_game():
                self.time_since_last_tick = 0

        if self.in_music_queue and not mixer.music.get_busy():
            self.advance_music_queue()


    def late_update(self):
       for _, section in self.get_active_sections():
            section.late_update()

    def is_in_game(self):
        return self.state == GameState.IN_GAME

    def handle_events(self, context: tcod.context.Context):
        self.event_handler.handle_events(context, discard_events=self.full_screen_effect.in_effect)

    def setup_effects(self):
        self.full_screen_effect = MeltWipeEffect(self, 0, 0, self.screen_width, self.screen_height, MeltWipeEffectType.RANDOM, 20)

    def setup_sections(self):
        self.intro_sections = {}
        self.intro_sections["introSection"] = IntroSection(self,0,0,self.screen_width, self.screen_height)

        self.menu_sections = {}
        self.menu_sections["Menu"] = MenuSection(self,0,0,self.screen_width, self.screen_height)

        self.game_sections = {}
        self.game_sections["statueSection"] = StatueSection(self, 0,0,self.screen_width, self.screen_height)
        self.game_sections["statueSummarySection"] = StatueSummarySection(self, 0,0,self.screen_width, self.screen_height, "summary_section.xp")
        self.game_sections["confirmationDialog"] = Confirmation(self, 7, 9, 36, 10)

        self.completion_sections = {}

        self.disabled_sections = ["confirmationDialog", "notificationDialog", "statueSummarySection"]

    def get_active_sections(self):
        if self.state == GameState.INTRO:
            return self.intro_sections.items()
        elif self.state == GameState.MENU:
            return self.menu_sections.items()
        elif self.is_in_game():
            return self.game_sections.items()
        elif self.state == GameState.COMPLETE:
            return self.completion_sections.items()

    def get_active_ui_sections(self):
        if self.state == GameState.INTRO:
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.intro_sections.items())).items()
        elif self.state == GameState.MENU:
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.menu_sections.items())).items()
        elif self.is_in_game():
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.game_sections.items())).items()
        elif self.state == GameState.COMPLETE:
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.completion_sections.items())).items()

    def enable_section(self, section):
        if section in self.disabled_sections:
            self.disabled_sections.remove(section)

    def disable_section(self, section):
        if section not in self.disabled_sections:
            self.disabled_sections.append(section)

    def load_level(self):
        self.enable_section("statueSection")
        self.game_sections["statueSection"].load_level(self.stage, self.level)

    def select_level(self, stage, level):
        self.change_state(GameState.IN_GAME)
        self.full_screen_effect.start()
        self.stage = stage
        self.level = level
        Timer(2,self.load_level).start()

    def level_complete(self, summary):
        self.open_summary_section(summary)
        self.full_screen_effect.start()

    def leave_level(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()
        self.disable_section("statueSection")
        self.game_sections["statueSection"].reset()
        self.end_music_queue(2000)

    def queue_music(self, stage):
        music = self.stage_music[stage]["music"]
        volume = self.stage_music[stage]["music_volume"]
        if len(music) > 0:
            random.shuffle(music)
            mixer.music.set_volume(volume)
            self.current_music_index = 0
            self.music_queue = music
            self.advance_music_queue()
            self.in_music_queue = True
        
    def advance_music_queue(self):
        print("Playing: " + self.music_queue[self.current_music_index])
        mixer.music.load("sounds/music/" + self.music_queue[self.current_music_index])
        self.current_music_index += 1

        if self.current_music_index >= len(self.music_queue):
            self.current_music_index = 0

        self.play_music()

    def play_music(self):
        mixer.music.play()

    def end_music_queue(self, fadeout_time):
        mixer.music.fadeout(fadeout_time)
        self.in_music_queue = False

    def open_menu(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()

    def award_crowns(self, num_crowns, total_level_crowns, level_name):
        with open("game_data/game_save.json", "w") as f:
            self.save_data["total_crowns"] += num_crowns
            if not level_name in self.save_data or self.save_data[level_name] < total_level_crowns:
                self.save_data[level_name] = total_level_crowns
            
            json.dump(self.save_data, f, indent=2)

    def get_awarded_crowns(self, level_name):
        if level_name in self.save_data:
            return self.save_data[level_name]
        else:
            return 0

    def change_state(self, new_state):
        old_state = self.state

        self.state = new_state
   
    def get_total_awarded_crowns(self):
        return self.save_data["total_crowns"]

    def get_delta_time(self):
        return self.delta_time.get_delta_time()

    def quit(self):
        raise SystemExit()

    def open_confirmation_dialog(self, text, confirmation_action):
        self.game_sections["confirmationDialog"].setup(
            text, confirmation_action)
        self.enable_section("confirmationDialog")

    def close_confirmation_dialog(self):
        self.disable_section("confirmationDialog")

    def is_confirmation_dialog_open(self):
        return "confirmationDialog" not in self.disabled_sections

    def open_notification_dialog(self, text):
        self.game_sections["notificationDialog"].setup(text)
        self.enable_section("notificationDialog")

    def close_notification_dialog(self):
        self.disable_section("notificationDialog")

    def open_summary_section(self, summary):
        self.game_sections["statueSummarySection"].setup(summary)
        self.enable_section("statueSummarySection")
        self.disable_section("statueSection")

    def hide_summary_section(self):
        self.disable_section("statueSummarySection")
        self.enable_section("statueSection")
        self.full_screen_effect.start()

    def close_summary_section(self):
        self.game_sections["statueSummarySection"].close()
        self.disable_section("statueSummarySection")
        self.state = GameState.MENU
        self.full_screen_effect.start()


    def is_ui_paused(self):
        return self.full_screen_effect.in_effect

    def end_intro(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()
