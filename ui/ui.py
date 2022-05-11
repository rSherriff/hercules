from __future__ import annotations

from threading import Timer
from typing import TYPE_CHECKING
from urllib import response

import keyboard
import tcod.event
from actions.actions import Action, CloseMenu, EscapeAction, OpenMenu
from effects.horizontal_wipe_effect import (HorizontalWipeDirection,
                                            HorizontalWipeEffect)
from tcod import Console, event
from utils.utils import translate_range


class UI:
    def __init__(self, section, x=0, y=0):
        self.elements = list()

        self.x = x
        self.y = y
        self.section = section
        self.enabled = True

    def render(self, console: Console):
        for element in self.elements:
            element.render(console)

    def keydown(self, event: tcod.event.KeyDown):
        if self.enabled == False:
            return

        for element in self.elements:
            element.on_keydown(event)

    def mousedown(self, x: int, y: int):
        if self.enabled == False:
            return
            
        for element in self.elements:
            if element.is_mouseover(x, y):
                element.on_mousedown(x,y)
            elif isinstance(element, Input):
                element.selected = False
                element.blink = False

    def mouseup(self, x: int, y: int):
        if self.enabled == False:
            return
            
        for element in self.elements:
                element.on_mouseup()

    def mousemove(self, x: int, y: int):
        if self.enabled == False:
            return
            
        for element in self.elements:
            if element.is_mouseover(x, y):
                if element.mouseover == False:
                    element.on_mouseenter()
                element.mouseover = True
            else:
                if element.mouseover == True:
                    element.on_mouseleave()
                element.mouseover = False

            element.mousemove(x,y)
        
        self.sort_elements()

    def add_element(self, element):
        element.x = element.x + self.x
        element.y = element.y + self.y
        self.elements.append(element)
        self.sort_elements()

    def sort_elements(self):
        self.elements.sort(key = lambda element: element.render_order)
        self.elements.sort(key = lambda element: element.mouseover)

class UIElement:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mouseover = False
        self.render_order = 0
        pass

    def render(self, console: Console):
        pass

    def on_keydown(self, event: tcod.event.KeyDown):
        pass

    def on_mouseenter(self):
        pass

    def on_mouseleave(self):
        pass

    def is_mouseover(self, x: int, y: int):
        return self.x<= x <= self.x + self.width - 1 and self.y <= y <= self.y + self.height - 1

    def mousemove(self,x,y):
        pass

    def on_mousedown(self, x: int, y: int):
        raise NotImplementedError()
    
    def on_mouseup(self):
        pass


class Button(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, click_action: Action, tiles, normal_bg = (255,255,255), highlight_bg = (128,128,128)):
        super().__init__(x,y,width,height)
        self.click_action = click_action
        self.tiles = tiles

        self.hover_action = None

        self.normal_bg= normal_bg
        self.highlight_bg = highlight_bg


    def render(self, console: Console):
        if self.tiles is None:
            return

        temp_console = Console(width=self.width, height=self.height, order="F")

        for h in range(0,self.height):
            for w in range(0, self.width):
                if self.tiles[w,h][0] != 9488:
                    if self.mouseover:
                        self.tiles[w,h][1] = self.highlight_bg
                    else:
                        self.tiles[w,h][1] = self.normal_bg 
                        
                temp_console.tiles_rgb[w,h] = self.tiles[w,h]

        temp_console.blit(console, self.x, self.y)

    def on_mousedown(self, x: int, y: int):
        if self.click_action is not None:
            self.click_action.perform()

    def on_mouseenter(self):
        if self.hover_action is not None:
            self.hover_action.perform()

    def set_action(self, action):
        self.click_action = action
    
    def set_hover_action(self, action):
        self.hover_action = action

class ShapedButton(Button):
    def __init__(self, x: int, y: int, width: int, height: int, click_action: Action, tiles, active_tiles):
        super().__init__(x,y,width,height,click_action,tiles)
        self.active_tiles = active_tiles

    def render(self, console: Console):
        temp_console = Console(width=self.width, height=self.height, order="F")

        for h in range(0,self.height):
            for w in range(0, self.width):
                temp_console.tiles_rgb[w,h] = self.tiles[w,h]

        if self.mouseover:
            for tile in self.active_tiles:
                temp_console.tiles_rgb[tile[0],tile[1]][0] = ord(' ')
                temp_console.tiles_rgb[tile[0],tile[1]][2] = (0,255,0)

        temp_console.blit(console, self.x, self.y)

    def is_mouseover(self, x,y):
        for tile in self.active_tiles:
            if tile[0] == int(x - self.x) and tile[1] == int(y - self.y):
                return True
        return False
            
class Input(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x,y,width,height)
        self.selected = False
        self.text = ''
        self.blink_interval = 0.7
        self.bg_color = (0,0,0)
        self.fg_color = (255,255,255)

    def render(self, console: Console):
        temp_console = Console(width=self.width, height=self.height)
        for w in range(0,self.width):
            if w < len(self.text):
                temp_console.tiles_rgb[0,w] = (ord(self.text[w]), self.fg_color , self.bg_color)
            else:
                temp_console.tiles_rgb[0,w] = (ord(' '), self.fg_color , self.bg_color)

        if self.selected == True:
            if self.blink == True:
                temp_console.tiles_rgb[0,len(self.text)] = (9488, self.fg_color , self.bg_color)

        temp_console.blit(console, self.x, self.y)

    def blink_on(self):
        self.blink = True
        if self.selected == True:
            t = Timer(self.blink_interval, self.blink_off)
            t.start()
    
    def blink_off(self):
        self.blink = False
        if self.selected == True:
            t = Timer(self.blink_interval, self.blink_on)
            t.start()

    def on_mousedown(self, x: int, y: int):
        self.selected = True
        self.blink_on()

    def on_keydown(self, event):
        if self.selected == True:
            key = event.sym

            if key == tcod.event.K_BACKSPACE:
                self.text = self.text[:-1]
            elif key == tcod.event.K_RETURN or key == tcod.event.K_ESCAPE:
                self.selected = False
                self.blink = False
            elif key == tcod.event.K_SPACE and len(self.text) < self.width - 1:
                self.text += ' '
            elif len(self.text) < self.width - 1 and tcod.event.K_a <= key <= tcod.event.K_z:
                letter = get_letter_key(key)
                if keyboard.is_pressed('shift'):
                    letter = letter.capitalize()
                self.text += letter

class CheckedInput(Input):
    def __init__(self, x: int, y: int, width: int, height: int, check_string: str, trigger_once : bool, completion_action: Action, completion_color : (), completion_effect : HorizontalWipeEffect):
        super().__init__(x,y,width,height)
        self.check_string = check_string
        self.input_correct = False
        self.completion_action = completion_action
        self.completion_color = completion_color
        self.completion_effect = completion_effect
        self.trigger_once = trigger_once

    def render(self, console: Console):
        super().render(console)

        if self.completion_effect.in_effect is True:
            self.completion_effect.render(console)
        elif self.input_correct == True:
            #Completion stuff that we need one render loop after completion before we trigger
            self.bg_color = self.completion_color
            self.fg_color = (0,0,0)
            self.completion_effect.start(HorizontalWipeDirection.RIGHT)
            self.completion_effect.in_effect = True
            self.completion_effect.set_tiles(console.tiles_rgb[self.x: self.x+self.width, self.y: self.y+self.height])

    def on_mousedown(self, x: int, y: int):
        if self.input_correct == False or self.input_correct == True and self.trigger_once == False :
            self.selected = True
            self.blink_on()

    def on_keydown(self, event):
        if self.selected == True:
            super().on_keydown(event)

            if self.text.capitalize() == self.check_string.capitalize(): #Check the input is correct
                if self.trigger_once == True and self.input_correct == False: #Check whether we only trigger once and has the input been correct before
                    self.input_correct = True
                    self.completion_action.perform()

                    if self.trigger_once == True:
                        self.selected = False
            else:
                self.input_correct = False

class HoverTrigger(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, mouse_enter_action : Action, mouse_leave_action: Action):
        super().__init__(x,y,width,height)
        self.mouse_enter_action = mouse_enter_action
        self.mouse_leave_action = mouse_leave_action

    def on_mouseenter(self):
        self.mouse_enter_action.perform()
        
    def on_mouseleave(self):
        self.mouse_leave_action.perform()

    def on_mousedown(self, x: int, y: int):
        pass

class Tooltip(UIElement):
    def __init__(self, x: int, y: int, width: int, height:int, x_offset: int, y_offset: int, text: str):
        super().__init__(x,y,width,height)

        self.visible = False
        self.visibleTimer = 5

        self.render_width = 0
        self.render_height = 1
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.lines = list()
        self.lines = text.split('\n')
        self.render_height = len(self.lines) + 2
        for l in self.lines:
            self.render_width = max(self.render_width, len(l) + 2)

        self.render_order = 5

    def on_mouseenter(self):
        pass
        
    def on_mouseleave(self):
        self.visibleTimer = 5
        self.visible = False
        

    def on_mousedown(self, x: int, y: int):
        pass

    def render(self, console: Console):
        if self.mouseover:
            self.visibleTimer -= 0.17
        if self.visibleTimer < 0:
            self.visible = True

        if self.visible == True:
            temp_console = Console(width=self.render_width, height=self.render_height, order="F")

            for h in range(0,self.render_height):
                for w in range(0, self.render_width):
                    temp_console.tiles_rgb[w,h][2] = (255,255,255) 

            count = 1
            for l in self.lines:
                temp_console.print(1, count, l, (0,0,0))
                count += 1

            temp_console.blit(console, self.x + self.x_offset, self.y+self.y_offset)

class Toggle(Button):
    def __init__(self, x: int, y: int, width: int, height: int, is_on: bool, on_action: Action, off_action: Action, tiles, on_tiles, off_tiles, response_x:int, response_y:int, normal_bg = (255,255,255), highlight_bg = (128,128,128)):
        super().__init__(x,y,width,height, None, tiles, normal_bg, highlight_bg)
        self.on_action = on_action
        self.off_action = off_action
        self.on_tiles = on_tiles
        self.off_tiles = off_tiles
        self.response_x = response_x
        self.response_y = response_y

        self.is_on = is_on

    def render(self, console: Console):
        if self.tiles is None:
            return

        temp_console = Console(width=self.width, height=self.height, order="F")

        for h in range(0,self.height):
            for w in range(0, self.width):
                if self.tiles[w,h][0] != 9488:
                    if self.mouseover:
                        self.tiles[w,h][1] = self.highlight_bg
                    else:
                        self.tiles[w,h][1] = self.normal_bg 
                        
                temp_console.tiles_rgb[w,h] = self.tiles[w,h]
        
        tiles_to_draw = self.on_tiles if self.is_on else self.off_tiles
        shape = self.on_tiles.shape
        for h in range(0,shape[1]):
            for w in range(0, shape[0]):
                temp_console.tiles_rgb[self.response_x + w, self.response_y + h] = tiles_to_draw[w,h]["graphic"]
                if self.mouseover:
                    temp_console.tiles_rgb[self.response_x + w, self.response_y + h][1] = self.highlight_bg
                else:
                    temp_console.tiles_rgb[self.response_x + w, self.response_y + h][1] = self.normal_bg 

        temp_console.blit(console, self.x, self.y)

    def on_mousedown(self, x: int, y: int):
        if self.is_on:
            if self.off_action is not None:
                self.off_action.perform()
        if not self.is_on:
            if self.on_action is not None:
                self.on_action.perform()
                
        self.is_on = not self.is_on

    def set_on_action(self, action):
        self.click_action = action

    def set_off_action(self, action):
        self.off_action = action

class HorizontalSlider(UIElement):
    def __init__(self, x, y, width, handle_tiles, move_action: Action, value:int=0, range_min:int=0, range_max:int=1):
        super().__init__(x, y, width, 1)
        self.handle_tiles = handle_tiles
        self.move_action = move_action
        self.is_dragging = False
        self.range_min = range_min
        self.range_max = range_max
        self.value = int(self.get_reversed_ranged_value(value))

    def render(self, console):
        shape = self.handle_tiles.shape
        x = self.x + self.value
        console.tiles_rgb[x:x+shape[0], self.y:self.y+shape[1]] = self.handle_tiles["graphic"]

    def on_mousedown(self, x: int, y: int):
        self.value = min(max(self.x, x), self.x+self.width) - self.x
        self.is_dragging = True

    def mousemove(self, x: int, y: int):
        old_value = self.value
        if self.is_dragging:
            self.value = min(max(self.x, x), self.x+self.width- 1) - self.x
            if self.value != old_value:
                self.move_action.perform(self.get_ranged_value(self.value))
                
    def on_mouseup(self):
        if self.is_dragging:
            self.is_dragging = False
            self.move_action.perform(self.get_ranged_value(self.value))

    def get_ranged_value(self, value):
        return translate_range(value, 0, self.width, self.range_min, self.range_max)

    def get_reversed_ranged_value(self, value):
        return translate_range(value, self.range_min, self.range_max, 0, self.width)

class VerticalSlider(UIElement):
    def __init__(self, x, y, height, handle_tiles, move_action: Action, value:int=0, range_min:int=0, range_max:int=1):
        super().__init__(x, y, 1, height)
        self.handle_tiles = handle_tiles
        self.move_action = move_action
        self.is_dragging = False
        self.range_min = range_min
        self.range_max = range_max
        self.value = int(self.get_reversed_ranged_value(value))

    def render(self, console):
        shape = self.handle_tiles.shape
        y = self.y + self.value
        console.tiles_rgb[self.x:self.x+shape[0], y:y+shape[1]] = self.handle_tiles["graphic"]

    def on_mousedown(self, x: int, y: int):
        self.value = min(max(self.y, y), self.y+self.height) - self.y
        self.is_dragging = True

    def mousemove(self, x: int, y: int):
        old_value = self.value
        if self.is_dragging:
            self.value = min(max(self.y, y), self.y+self.height) - self.y
            if self.value != old_value:
                self.move_action.perform(self.get_ranged_value(self.value))
                
    def on_mouseup(self):
        if self.is_dragging:
            self.is_dragging = False
            self.move_action.perform(self.get_ranged_value(self.value))

    def get_ranged_value(self, value):
        return translate_range(value, 0, self.height, self.range_min, self.range_max)

    def get_reversed_ranged_value(self, value):
        return translate_range(value, self.range_min, self.range_max, 0, self.height)
        

def ele_comp(a:UIElement, b:UIElement):
    if a is Tooltip:
        return b
    else:
        return a

def get_letter_key(key):
    if key == tcod.event.K_a:
        return 'a'
    elif key == tcod.event.K_b:
        return 'b'
    elif key == tcod.event.K_c:
        return 'c'
    elif key == tcod.event.K_d:
        return 'd'
    elif key == tcod.event.K_e:
        return 'e'
    elif key == tcod.event.K_f:
        return 'f'
    elif key == tcod.event.K_g:
        return 'g'
    elif key == tcod.event.K_h:
        return 'h'
    elif key == tcod.event.K_i:
        return 'i'
    elif key == tcod.event.K_j:
        return 'j'
    elif key == tcod.event.K_k:
        return 'k'
    elif key == tcod.event.K_l:
        return 'l'
    elif key == tcod.event.K_m:
        return 'm'
    elif key == tcod.event.K_n:
        return 'n'
    elif key == tcod.event.K_o:
        return 'o'
    elif key == tcod.event.K_p:
        return 'p'
    elif key == tcod.event.K_q:
        return 'q'
    elif key == tcod.event.K_r:
        return 'r'
    elif key == tcod.event.K_s:
        return 's'
    elif key == tcod.event.K_t:
        return 't'
    elif key == tcod.event.K_u:
        return 'u'
    elif key == tcod.event.K_v:
        return 'v'
    elif key == tcod.event.K_w:
        return 'w'
    elif key == tcod.event.K_x:
        return 'x'
    elif key == tcod.event.K_y:
        return 'y'
    elif key == tcod.event.K_z:
        return 'z'

    return ''
