from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine


class Action:
    def __init__(self, engine) -> None:
        super().__init__()
        self.engine = engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        self.engine.quit()


class CloseMenu(Action):
    def perform(self) -> None:
        self.engine.close_menu()


class OpenMenu(Action):
    def perform(self) -> None:
        self.engine.open_menu()


class ShowTooltip(Action):
    def __init__(self, engine, tooltip_key: str) -> None:
        super().__init__(engine)
        self.tooltip_key = tooltip_key

    def perform(self):
        self.engine.show_tooltip(self.tooltip_key)


class HideTooltip(Action):
    def __init__(self, engine, tooltip_key: str) -> None:
        super().__init__(engine)
        self.tooltip_key = tooltip_key

    def perform(self):
        self.engine.hide_tooltip(self.tooltip_key)


class GameOver(Action):
    def perform(self) -> None:
        self.engine.game_over()

class AddEntity(Action):
    def __init__(self, engine, section, entity):
        super().__init__(engine)
        self.section = section
        self.entity = entity

    def perform(self):
        self.section.entities.append(self.entity)

class DeleteEntity(Action):
    def __init__(self, engine, section, entity):
        super().__init__(engine)
        self.section = section
        self.entity = entity

    def perform(self):
        self.section.remove_entity(self.entity)


class DisableSection(Action):
    def __init__(self, engine, section) -> None:
        super().__init__(engine)
        self.section = section

    def perform(self) -> None:
        return self.engine.disable_section(self.section)


class OpenConfirmationDialog(Action):
    def __init__(self, engine, text, confirmation_action) -> None:
        super().__init__(engine)
        self.text = text
        self.confirmation_action = confirmation_action

    def perform(self) -> None:
        return self.engine.open_confirmation_dialog(self.text, self.confirmation_action)


class CloseConfirmationDialog(Action):
    def perform(self) -> None:
        return self.engine.close_confirmation_dialog()


class OpenNotificationDialog(Action):
    def __init__(self, engine, text) -> None:
        super().__init__(engine)
        self.text = text

    def perform(self) -> None:
        return self.engine.open_notification_dialog(self.text)


class CloseNotificationDialog(Action):
    def perform(self) -> None:
        return self.engine.close_notification_dialog()


class StatueMaterialChiseled(Action):
    def __init__(self, engine, entity) -> None:
        super().__init__(engine)
        self.entity = entity
        
    def perform(self) -> None:
        return self.entity.section.remove_entity(self.entity)

class BlockMaterialChiseled(Action):
    def __init__(self, engine, entity) -> None:
        super().__init__(engine)
        self.entity = entity

    def perform(self) -> None:
        return self.entity.section.remove_entity(self.entity)

class ChiselMistakeAction(Action):
    def __init__(self, engine, entity) -> None:
        super().__init__(engine)
        self.entity = entity
        
    def perform(self) -> None:
        return self.entity.section.chisel_mistake()

class SelectLevelAction(Action):
    def __init__(self, engine, level) -> None:
        super().__init__(engine)
        self.level = level

    def perform(self) -> None:
        return self.engine.select_level(self.level)

class LevelCompleteAction(Action):
    def __init__(self, engine, summary) -> None:
        super().__init__(engine)
        self.summary = summary

    def perform(self) -> None:
        return self.engine.level_complete(self.summary)

class CloseSummarySectionAction(Action):
    def perform(self) -> None:
        return self.engine.close_summary_section()

class HideSummarySectionAction(Action):
    def perform(self) -> None:
        return self.engine.hide_summary_section()

