from __future__ import annotations

import abc
import json
import os
import random
from collections import OrderedDict
from enum import Enum, auto

import tcod
from pygame import mixer
from tcod.console import Console

from actions.actions import OpenNotificationDialog
from application_path import get_app_path
from effects.lfsr_effect import LFSREffect
from effects.melt_effect import MeltWipeEffect, MeltWipeEffectType
from fonts.font_manager import FontManager
from input_handlers import EventHandler, MainGameEventHandler
from sections.confirmation import Confirmation
from sections.intro_section import IntroSection
from sections.menu_section import MenuSection
from sections.notification import Notification
from sections.statue_section import StatueSection
from sections.statue_summary_section import StatueSummarySection
from utils.delta_time import DeltaTime


class GameState(Enum):
    INTRO = auto()
    MENU = auto()
    IN_GAME = auto()

class Engine(abc.ABC):
    def __init__(self, save_path, teminal_width: int, terminal_height: int):

        mixer.init()

        self.save_path = save_path

        self.save_data = None
        if os.path.isfile(self.save_path):
            with open(self.save_path) as f:
                self.save_data = json.load(f)
                self.set_mixer_volume(self.save_data["volume"])
        else:
            self.create_new_save_data()

        self.demo = True

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
        self.load_fonts()

        self.in_stage_music_queue = False
        self.playing_menu_music = False

        levels_path = "game_data/levels_demo.json" if self.demo else "game_data/levels.json"
        with open ( levels_path ) as f:
            data = json.load(f)

            self.intro_sections["introSection"].load_splashes(data["intro_splashes"])

            self.load_initial_data(data)
            
    def create_new_save_data(self):
        self.save_data = dict()
        self.save_data["fullscreen"] = True
        self.save_data["volume"] = 0.5
        self.set_mixer_volume(self.save_data["volume"])

    @abc.abstractmethod
    def load_initial_data(self, data):
        pass

    @abc.abstractmethod
    def load_fonts(self):
        pass

    def render(self, root_console: Console) -> None:
        """ Renders the game to console """
        for section_key, section_value in self.get_active_sections():
            if section_key not in self.disabled_sections:
                section_value.render(root_console)

        if self.full_screen_effect.in_effect == True:
            self.full_screen_effect.render(root_console)
        elif self.lfsr_screen_effect.in_effect == True:
            self.lfsr_screen_effect.render(root_console)
        else:
            self.full_screen_effect.set_tiles(root_console.tiles_rgb)
            self.lfsr_screen_effect.set_tiles(root_console.tiles_rgb)

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

        if self.in_stage_music_queue and not mixer.music.get_busy():
            self.advance_music_queue()

    def late_update(self):
       for _, section in self.get_active_sections():
            section.late_update()

    def is_in_game(self):
        return self.state == GameState.IN_GAME

    def handle_events(self, context: tcod.context.Context):
        self.event_handler.handle_events(context, discard_events=self.is_ui_paused())

    def setup_effects(self):
        self.full_screen_effect = MeltWipeEffect(self, 0, 0, self.screen_width, self.screen_height, MeltWipeEffectType.RANDOM, 20)
        self.lfsr_screen_effect = LFSREffect(self, 0, 0, self.screen_width, self.screen_height)

    #@abc.abstractmethod
    def setup_sections(self): #move
        self.intro_sections = OrderedDict()
        self.intro_sections["introSection"] = IntroSection(self,0,0,self.screen_width, self.screen_height)

        self.menu_sections = OrderedDict()
        self.menu_sections["Menu"] = MenuSection(self,0,0,self.screen_width, self.screen_height)

        self.game_sections = OrderedDict()
        self.game_sections["statueSection"] = StatueSection(self, 0,0,self.screen_width, self.screen_height)
        self.game_sections["statueSummarySection"] = StatueSummarySection(self, 0,0,self.screen_width, self.screen_height, "summary_section.xp")
        
        self.misc_sections = OrderedDict()
        self.misc_sections["notificationDialog"] = Notification(self, 7, 9, 37, 10)
        self.misc_sections["confirmationDialog"] = Confirmation(self, 7, 9, 37, 10)

        self.completion_sections = OrderedDict()

        self.disabled_sections = ["confirmationDialog", "notificationDialog", "statueSummarySection"]
        self.disabled_ui_sections = ["confirmationDialog", "notificationDialog", "statueSummarySection"]

    def get_active_sections(self):
        sections = OrderedDict()
        if self.state == GameState.INTRO:
            sections = self.intro_sections
        elif self.state == GameState.MENU:
            sections = self.menu_sections
        elif self.is_in_game():
            sections = self.game_sections

        sections |= self.misc_sections
        return sections.items()

    def get_active_ui_sections(self):
        sections = OrderedDict()
        if self.state == GameState.INTRO:
            sections = dict(filter(lambda elem: elem[0] not in self.disabled_ui_sections, self.intro_sections.items()))
        elif self.state == GameState.MENU:
            sections =  dict(filter(lambda elem: elem[0] not in self.disabled_ui_sections, self.menu_sections.items()))
        elif self.is_in_game():
            sections =  dict(filter(lambda elem: elem[0] not in self.disabled_ui_sections, self.game_sections.items()))

        sections |= (dict(filter(lambda elem: elem[0] not in self.disabled_ui_sections, self.misc_sections.items())))
        return sections.items()

    def enable_section(self, section):
        if section in self.disabled_sections:
            self.disabled_sections.remove(section)
            self.enable_ui_section(section)

    def disable_section(self, section):
        if section not in self.disabled_sections:
            self.disabled_sections.append(section)
            self.disable_ui_section(section)

    def enable_ui_section(self, section):
        if section in self.disabled_ui_sections:
            self.disabled_ui_sections.remove(section)

    def disable_ui_section(self, section):
        if section not in self.disabled_ui_sections:
            self.disabled_ui_sections.append(section)

    def queue_music(self, stage):
        music = self.stage_music[stage]["music"]
        volume = self.stage_music[stage]["music_volume"]
        if len(music) > 0:
            random.shuffle(music)
            mixer.music.set_volume(self.save_data["volume"])
            self.current_music_index = 0
            self.music_queue = music
            self.advance_music_queue()
            self.in_stage_music_queue = True
        
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
        self.in_stage_music_queue = False

    def play_music_file(self, file):
        if not self.in_stage_music_queue:
            mixer.music.load("sounds/music/" + file)
            mixer.music.play()

    def play_menu_music(self, file=""):
        if not self.playing_menu_music:
            self.playing_menu_music = True
            if len(file) > 0:
                self.menu_music = file
            mixer.music.load("sounds/music/" + self.menu_music)
            mixer.music.play()

    def open_menu(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()

    def change_state(self, new_state):
        old_state = self.state

        self.state = new_state
   
    def get_delta_time(self):
        return self.delta_time.get_delta_time()

    def quit(self):
        raise SystemExit()

    def toggle_fullscreen(self):
        with open(self.save_path, "w") as f:
            self.save_data["fullscreen"] = not self.save_data["fullscreen"]
            json.dump(self.save_data, f, indent=2)

        OpenNotificationDialog(self, "The game must be restarted for this option to take effect.", "Menu").perform()
            
    def open_confirmation_dialog(self, text, confirmation_action, section):
        self.misc_sections["confirmationDialog"].setup(text, confirmation_action, section)
        self.enable_section("confirmationDialog")
        self.disable_ui_section(section)

    def close_confirmation_dialog(self, section):
        self.disable_section("confirmationDialog")
        self.enable_ui_section(section)

    def is_confirmation_dialog_open(self):
        return "confirmationDialog" not in self.disabled_sections

    def open_notification_dialog(self, text, section):
        self.misc_sections["notificationDialog"].setup(text, section)
        self.enable_section("notificationDialog")
        self.disable_ui_section(section)

    def close_notification_dialog(self, section):
        self.disable_section("notificationDialog")
        self.enable_ui_section(section)

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
        self.play_menu_music()

    def is_ui_paused(self):
        return self.full_screen_effect.in_effect or self.lfsr_screen_effect.in_effect

    def end_intro(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()

    def start_lfsr_effect(self):
        self.lfsr_screen_effect.start()

    def set_mixer_volume(self, volume):
        mixer.music.set_volume(volume)
        with open(self.save_path, "w") as f:
            self.save_data["volume"] = volume
            json.dump(self.save_data, f, indent=2)

    def is_demo(self):
        return self.demo
