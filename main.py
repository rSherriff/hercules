#!/usr/bin/env python3
import json
import os

import tcod
from appdirs import *

from application_path import get_app_path
from hercules_game import HerculesGame


def main() -> None:
    screen_width = 51
    screen_height = 30

    terminal_height = screen_height * 2
    terminal_width = screen_width * 2

    tileset = tcod.tileset.load_tilesheet(
        get_app_path() + "/fonts/polyducks_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    load_failed = False
    window_flags = tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP

    appname = "fhercules"
    appauthor = "rsherriff"
    save_path = user_data_dir(appname, appauthor) 

    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    save_path += "/game_save.json"

    if os.path.isfile(save_path):
        with open(save_path) as f:
            try:
                data = json.load(f)
                if "fullscreen" in data:
                    window_flags = tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP if data["fullscreen"] else tcod.context.SDL_WINDOW_RESIZABLE
            except:
                load_failed = True
        if load_failed:
            print("Save data exists but it failed to load, overwriting!")
            os.remove(save_path)

    with tcod.context.new_terminal(
        terminal_width,
        terminal_height,
        tileset=tileset,
        title="The Farnese Hercules",
        vsync=True,
        sdl_window_flags=window_flags
    ) as root_context:

        tcod.lib.SDL_SetHint(b"SDL_RENDER_SCALE_QUALITY", b"0")

        root_console = tcod.Console(screen_width, screen_height, order="F")
        engine = HerculesGame(save_path, screen_width, screen_height)

        cycle = 0
        while True:
            cycle += 1
            if cycle % 2 == 0:
                engine.update()

            root_console.clear()

            engine.event_handler.on_render(root_console=root_console)

            root_context.present(root_console)

            engine.handle_events(root_context)

            if cycle % 2 == 0:
                engine.late_update()


if __name__ == "__main__":
    main()
