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

class NoAction(Action):
    def perform(self) -> None:
        print("No Action taken!")

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
    def __init__(self, engine, text, confirmation_action, section) -> None:
        super().__init__(engine)
        self.text = text
        self.confirmation_action = confirmation_action
        self.section = section

    def perform(self) -> None:
        return self.engine.open_confirmation_dialog(self.text, self.confirmation_action, self.section)


class CloseConfirmationDialog(Action):
    def __init__(self, engine, section) -> None:
        super().__init__(engine)
        self.section = section

    def perform(self) -> None:
        return self.engine.close_confirmation_dialog(self.section)


class OpenNotificationDialog(Action):
    def __init__(self, engine, text, section) -> None:
        super().__init__(engine)
        self.text = text
        self.section = section

    def perform(self) -> None:
        return self.engine.open_notification_dialog(self.text, self.section)


class CloseNotificationDialog(Action):
    def __init__(self, engine, section) -> None:
        super().__init__(engine)
        self.section = section
        
    def perform(self) -> None:
        return self.engine.close_notification_dialog(self.section)


class ToggleFullScreenAction(Action):
    def __init__(self, engine) -> None:
        super().__init__(engine)

    def perform(self) -> None:
        self.engine.toggle_fullscreen()


class SliderAction(Action):
    def __init__(self, engine, action_type) -> None:
        super().__init__(engine)
        self.action_type = action_type
        
    def perform(self, value) -> None:
        action = self.action_type(self.engine, value)
        return action.perform(value)

class ChangeVolumeAction(Action):
    def __init__(self, engine, value) -> None:
        super().__init__(engine)
        self.value = value
        
    def perform(self, value) -> None:
        return self.engine.set_mixer_volume(value)

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
        return self.entity.section.chisel_fault()

class SelectLevelAction(Action):
    def __init__(self, engine, stage, level) -> None:
        super().__init__(engine)
        self.level = level
        self.stage = stage

    def perform(self) -> None:
        return self.engine.select_level(self.stage, self.level)

class LevelCompleteAction(Action):
    def __init__(self, engine, summary) -> None:
        super().__init__(engine)
        self.summary = summary

    def perform(self) -> None:
        return self.engine.level_complete(self.summary)

class LevelLeaveAction(Action):
    def perform(self) -> None:
        return self.engine.leave_level()

class CloseSummarySectionAction(Action):
    def perform(self) -> None:
        return self.engine.close_summary_section()

class HideSummarySectionAction(Action):
    def perform(self) -> None:
        return self.engine.hide_summary_section()

class QueueMusicAction(Action):
    def __init__(self, engine, stage) -> None:
        super().__init__(engine)
        self.stage = stage

    def perform(self) -> None:
        self.engine.queue_music(self.stage)

class EndMusicQueueAction(Action):
    def __init__(self, engine, fadeout_time) -> None:
        super().__init__(engine)
        self.fadeout_time = fadeout_time

    def perform(self) -> None:
        self.engine.end_music_queue( self.fadeout_time)

class IntroEndAction(Action):
    def perform(self) -> None:
        self.engine.end_intro()

class EnterStageSelectAction(Action):
    def perform(self) -> None:
        self.engine.menu_sections["Menu"].enter_stage_select()

class PlayMusicFileAction(Action):
    def __init__(self, engine, file) -> None:
        super().__init__(engine)
        self.file = file

    def perform(self) -> None:
        self.engine.play_music_file(self.file)

class PlayMenuMusicAction(Action):
    def __init__(self, engine, file="") -> None:
        super().__init__(engine)
        self.file = file

    def perform(self) -> None:
        self.engine.play_menu_music(self.file)

class ChangeMenuStageAction(Action):
    def __init__(self, engine, stage) -> None:
        super().__init__(engine)
        self.stage = stage

    def perform(self) -> None:
        self.engine.menu_sections["Menu"].delta_change_stage(self.stage)

class MenuHoverLevelAction(Action):
    def __init__(self, engine, level_index) -> None:
        super().__init__(engine)
        self.level_index = level_index

    def perform(self) -> None:
        self.engine.menu_sections["Menu"].hover_over_level(self.level_index)

class MenuSelectLevelAction(Action):
    def __init__(self, engine, level_index) -> None:
        super().__init__(engine)
        self.level_index = level_index

    def perform(self) -> None:
        self.engine.menu_sections["Menu"].select_level(self.level_index)

class EnterMenuMainAction(Action):
    def __init__(self, engine) -> None:
        super().__init__(engine)

    def perform(self) -> None:
        self.engine.menu_sections["Menu"].enter_main()

class EnterOptionsAction(Action):
    def __init__(self, engine) -> None:
        super().__init__(engine)

    def perform(self) -> None:
        self.engine.menu_sections["Menu"].enter_options()