from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from actions.actions import Action, EscapeAction

import tcod.event

if TYPE_CHECKING:
    from engine import Engine


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.current_context = None

    def handle_events(self, context: tcod.context.Context, discard_events: bool) -> None:
        for event in tcod.event.get():

            if discard_events == True:
                continue

            context.convert_event(event)
            self.dispatch(event)

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.engine.quit()

    def on_render(self, root_console: tcod.Console) -> None:
        self.engine.render(root_console)


class MainGameEventHandler(EventHandler):
    def handle_events(self, context: tcod.context.Context, discard_events: bool) -> None:
        self.current_context = context
        for event in tcod.event.get():

            if discard_events == True:
                continue

            context.convert_event(event)
            actions = self.dispatch(event)

            if actions is None:
                continue

            for action in actions:
                action.perform()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:

        if self.engine.is_ui_paused():
            return

        key = event.sym

        for _, section in self.engine.get_active_ui_sections():
            section.keydown(key)
            if section.ui is not None:
                section.ui.keydown(event)

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:

        self.engine.mouse_location = self.current_context.pixel_to_tile(
            event.pixel.x, event.pixel.y)

        for _, section in self.engine.get_active_ui_sections():
            if section.ui is not None:
                section.ui.mousemove(
                    self.engine.mouse_location[0], self.engine.mouse_location[1])

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[list(Action)]:

        if self.engine.is_ui_paused():
            return

        actions = []

        for _, section in self.engine.get_active_ui_sections():
            section.mousedown(event.button, self.engine.mouse_location[0], self.engine.mouse_location[1])
            if section.ui is not None:
                section.ui.mousedown(
                    self.engine.mouse_location[0], self.engine.mouse_location[1])

        return actions

    def ev_mousebuttonup(self, event: tcod.event.MouseButtonUp) -> Optional[T]:
        if self.engine.is_ui_paused():
            return

        actions = []

        for _, section in self.engine.get_active_ui_sections():
            section.mouseup(event.button, self.engine.mouse_location[0], self.engine.mouse_location[1])
            if section.ui is not None:
                section.ui.mouseup(
                    self.engine.mouse_location[0], self.engine.mouse_location[1])

        return actions
