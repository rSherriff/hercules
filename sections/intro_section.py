
import json
from enum import Enum, auto

import numpy as np
import tcod
from actions.actions import IntroEndAction, PlayMusicFileAction, PlayMenuMusicAction
from image import Image
from tcod import Console
import copy

from sections.section import Section


class IntroSplashType(Enum):
    TEXT = auto()
    IMAGE = auto() 
    BLANK = auto()
    SOUND = auto()

class IntroSplash():
    def __init__(self, type, intro, hang, outro) -> None:
        self.type = type
        self.length = intro + hang + outro
        self.intro = intro
        self.hang = hang
        self.outro_start = intro + hang
        self.outro_end = self.outro_start + outro

class TextIntroSplash(IntroSplash):
    def __init__(self,  intro, hang, outro, text) -> None:
        super().__init__(IntroSplashType.TEXT,  intro, hang, outro)
        self.text = text

class ImageIntroSplash(IntroSplash):
    def __init__(self,  intro, hang, outro, width, height, image_path) -> None:
        super().__init__(IntroSplashType.IMAGE,  intro, hang, outro)
        self.image = Image( width, height, image_path)
        self.width = width
        self.height = height

class BlankIntroSplash(IntroSplash):
    def __init__(self, length) -> None:
        super().__init__(IntroSplashType.BLANK, 0, length, 0)

class SoundIntroSplash(IntroSplash):
    def __init__(self, file, keep_into_menu) -> None:
        super().__init__(IntroSplashType.SOUND, 0, 0, 0)
        self.file = file
        self.keep_into_menu = keep_into_menu

class IntroSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = "") -> None:
        super().__init__(engine, x, y, width, height, xp_filepath)
        
        self.splash_list = list()
        self.time_into_splash = 0

    def load_splashes(self, splahes):
        """
        { "type": "TEXT", "intro": 2, "hang": 3, "outro": 2, "text": "A Game by Richard Sherriff" }
        { "type": "BLANK", "length": 2 }
        { "type": "IMAGE", "intro": 2, "hang": 3, "outro": 0, "file": "images/logo.xp", "width": -1, "height": -1 }
        { "type": "SOUND", "file": "filepath"}
        """
        for splash in splahes:
            if splash["type"] == "TEXT":
                self.splash_list.append(TextIntroSplash(splash["intro"],splash["hang"],splash["outro"], splash["text"]))
            elif splash["type"] == "BLANK":
                self.splash_list.append(BlankIntroSplash(splash["length"]))
            elif splash["type"] == "IMAGE":
                width = splash["width"] if splash["width"] > 0 else self.width
                height = splash["height"] if splash["height"] > 0 else self.height
                self.splash_list.append(ImageIntroSplash(splash["intro"],splash["hang"],splash["outro"], width, height, splash["file"]))
            elif splash["type"] == "SOUND":
                self.splash_list.append(SoundIntroSplash(splash["file"], splash["keep_into_menu"]))

    def update(self):
        self.time_into_splash += self.engine.get_delta_time()

        if len(self.splash_list) > 0:
            
            splash = self.splash_list[0]
            if splash.type == IntroSplashType.SOUND:
                if splash.keep_into_menu:
                    PlayMenuMusicAction(self.engine,splash.file).perform()
                else:
                    PlayMusicFileAction(self.engine,splash.file).perform()

            if self.time_into_splash > self.splash_list[0].length:
                self.splash_list = self.splash_list[1:]
                self.time_into_splash = 0
        else:        
            self.end()

    def render(self, console):
          if len(self.splash_list) > 0:
            splash = self.splash_list[0]
            if splash.type == IntroSplashType.TEXT:
                
                if self.time_into_splash < splash.intro:
                    t = self.translate(self.time_into_splash, 0, splash.intro, 0, 1)
                    fg = self.blend_colour((255,255,255), (0,0,0), t)
                elif self.time_into_splash > splash.outro_start:
                    t = self.translate(self.time_into_splash,  splash.outro_start,  splash.outro_end, 0, 1)
                    fg = self.blend_colour((0,0,0), (255,255,255), t)
                else:
                    fg = (255,255,255)
                console.print_box(x=0, y=int(self.height/2) - 1,  width=self.width, height=self.height, string=splash.text, alignment=tcod.CENTER, fg = fg)
            elif splash.type == IntroSplashType.IMAGE:
                if self.time_into_splash < splash.intro:
                    t = self.translate(self.time_into_splash, 0, splash.intro, 0, 1)
                elif self.time_into_splash > splash.outro_start:
                    t = self.translate(self.time_into_splash, splash.outro_start,  splash.outro_end, 0, 1)

                for w in range(0, console.width):
                    for h in range(0, self.height):
                        new_tile =  copy.copy(splash.image.tiles[w,h]["graphic"])
                        if self.time_into_splash < splash.intro:
                            new_tile[1] = self.blend_colour(new_tile[1], (0,0,0), t)
                            new_tile[2] = self.blend_colour(new_tile[2], (0,0,0), t)
                        elif self.time_into_splash > splash.outro_start:
                            new_tile[1] = self.blend_colour((0,0,0), new_tile[1],  t)
                            new_tile[2] = self.blend_colour((0,0,0), new_tile[2],  t)

                        console.tiles_rgb[w,h] = new_tile
            elif splash.type == IntroSplashType.BLANK:
                pass
            
    def keydown(self, key):
        if key == tcod.event.K_RETURN or key == tcod.event.K_ESCAPE:
            #HACK! 
            PlayMenuMusicAction(self.engine,"menu.mp3").perform()
            self.end()

    def end(self):
        IntroEndAction(self.engine).perform()

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    def blend_colour(self, lc, rc, t):
        r = lc[0] * t + rc[0] * (1 - t) 
        g = lc[1] * t + rc[1] * (1 - t) 
        b = lc[2] * t + rc[2] * (1 - t)

        return (int(r),int(g),int(b))