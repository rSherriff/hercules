import json
from threading import Timer

from pygame import mixer

from engine import Engine, GameState

class HerculesGame(Engine):
    def __init__(self, teminal_width: int, terminal_height: int):
        super().__init__(teminal_width, terminal_height)

    def create_new_save_data(self):
        super().create_new_save_data()
        self.save_data["total_crowns"] = 0

    def load_initial_data(self, data):
        self.stage_music = {}
        
        for stage in data["stages"]:
            self.stage_music[stage["name"]] = {}
            self.stage_music[stage["name"]]["music"] = stage["music"]
            self.stage_music[stage["name"]]["music_volume"] = stage["music_volume"]

    def load_fonts(self):
        self.font_manager.add_font("number_font")

    def award_crowns(self, num_crowns, total_level_crowns, level_name):
        with open("game_data/game_save.json", "w") as f:
            self.save_data["total_crowns"] += num_crowns
            if not level_name in self.save_data or self.save_data[level_name] < total_level_crowns:
                self.save_data[level_name] = total_level_crowns

            if not "levels_completed" in self.save_data:
                self.save_data["levels_completed"] = 0
            
            self.save_data["levels_completed"] += 1
            
            json.dump(self.save_data, f, indent=2)

    def get_awarded_crowns(self, level_name):
        if level_name in self.save_data:
            return self.save_data[level_name]
        else:
            return 0

    def get_total_awarded_crowns(self):
        return self.save_data["total_crowns"]

    def load_level(self):
        self.enable_section("statueSection")
        self.game_sections["statueSection"].load_level(self.stage, self.level)

    def select_level(self, stage, level): 
        mixer.music.fadeout(1000)
        self.playing_menu_music = False
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
        self.start_lfsr_effect()
        self.disable_section("statueSection")
        self.game_sections["statueSection"].reset()
        self.play_menu_music()

