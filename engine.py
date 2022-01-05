from __future__ import annotations

import json
from enum import Enum, auto
from threading import Timer

import tcod
from playsound import playsound
from tcod.console import Console

from application_path import get_app_path
from effects.melt_effect import MeltWipeEffect, MeltWipeEffectType
from input_handlers import EventHandler, MainGameEventHandler
from sections.statue_section import StatueSection
from utils.delta_time import DeltaTime
from sections.menu_section import MenuSection


class GameState(Enum):
    MENU = auto()
    IN_GAME = auto()
    GAME_OVER = auto()
    COMPLETE = auto()


class Engine:
    def __init__(self, teminal_width: int, terminal_height: int):

        self.screen_width = teminal_width
        self.screen_height = terminal_height
        self.delta_time = DeltaTime()

        self.player = None

        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.mouse_location = (0, 0)

        self.setup_effects()
        self.setup_sections()

        self.music_timer = Timer(77, self.play_music)
        self.play_music()

        self.tick_length = 2
        self.time_since_last_tick = -2

        self.state = GameState.MENU

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



    def late_update(self):
       for _, section in self.get_active_sections():
            section.late_update()

    def is_in_game(self):
        return self.state == GameState.IN_GAME

    def handle_events(self, context: tcod.context.Context):
        self.event_handler.handle_events(context, discard_events=self.full_screen_effect.in_effect or self.state == GameState.GAME_OVER)

    def setup_effects(self):
        self.full_screen_effect = MeltWipeEffect(self, 0, 0, self.screen_width, self.screen_height, MeltWipeEffectType.RANDOM, 20)

    def setup_sections(self):
        self.menu_sections = {}
        self.menu_sections["Menu"] = MenuSection(self,0,0,self.screen_width, self.screen_height)

        self.game_sections = {}
        self.game_sections["statueSection"] = StatueSection(self, 0,0,self.screen_width, self.screen_height)

        self.completion_sections = {}

        self.disabled_sections = ["confirmationDialog", "notificationDialog"]
        self.solo_ui_section = ""

    def get_active_sections(self):
        if self.state == GameState.MENU:
            return self.menu_sections.items()
        elif self.is_in_game():
            return self.game_sections.items()
        elif self.state == GameState.COMPLETE:
            return self.completion_sections.items()

    def get_active_ui_sections(self):
        if self.state == GameState.MENU:
            return self.menu_sections.items()
        elif self.is_in_game():
            if "confirmationDialog" not in self.disabled_sections:
                return {"confirmationDialog": self.game_sections["confirmationDialog"]}.items()
            if "notificationDialog" not in self.disabled_sections:
                return {"notificationDialog": self.game_sections["notificationDialog"]}.items()
            return self.game_sections.items()
        elif self.state == GameState.COMPLETE:
            return self.completion_sections.items()

    def enable_section(self, section):
        self.disabled_sections.remove(section)

    def disable_section(self, section):
        self.disabled_sections.append(section)

    def load_level(self):
        self.game_sections["statueSection"].load_level(self.level)

    def select_level(self, level):
        self.state = GameState.IN_GAME
        self.full_screen_effect.start()
        self.level = level
        Timer(2,self.load_level).start()

    def level_complete(self, level):
        self.state = GameState.MENU
        self.full_screen_effect.start()
        print("Level Over!")

    def open_menu(self):
        self.state = GameState.MENU
        self.full_screen_effect.start()

    def game_over(self):
        self.state = GameState.GAME_OVER
        Timer(3, self.open_menu).start()

    def complete_game(self):
        self.state = GameState.COMPLETE
        self.full_screen_effect.start()

    def get_delta_time(self):
        return self.delta_time.get_delta_time()

    def play_music(self):
        return
        playsound(get_app_path() + "/sounds/music.wav", False)
        self.music_timer = Timer(77, self.play_music)
        self.music_timer.start()

    def quit(self):
        if self.music_timer.is_alive():
            self.music_timer.cancel()
        raise SystemExit()

    def open_confirmation_dialog(self, text, confirmation_action):
        self.game_sections["confirmationDialog"].setup(
            text, confirmation_action)
        self.enable_section("confirmationDialog")

    def close_confirmation_dialog(self):
        self.disable_section("confirmationDialog")

    def open_notification_dialog(self, text):
        self.game_sections["notificationDialog"].setup(text)
        self.enable_section("notificationDialog")

    def close_notification_dialog(self):
        self.disable_section("notificationDialog")

    def is_ui_paused(self):
        return self.full_screen_effect.in_effect