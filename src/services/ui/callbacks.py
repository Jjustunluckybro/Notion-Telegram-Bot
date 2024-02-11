from dataclasses import dataclass
from typing import Final


@dataclass
class Callbacks:
    CANCEL_FSM: Final[str] = "cancel_fsm"
    CANCEL: Final[str] = "cancel"
    DONE: Final[str] = "done"

    OPEN_MAIN_MENU: Final[str] = "main_menu"

    OPEN_ALL_THEMES: Final[str] = "open_all_themes"
    OPEN_ALL_THEME_NOTES: Final[str] = "open_all_theme_notes"
    OPEN_ALL_NOTE_ALARMS: Final[str] = "open_all_note_alarms"

    CREATE_THEME: Final[str] = "create_theme_"
    CREATE_NOTE: Final[str] = "create_note_"
    CREATE_ALARM: Final[str] = "create_alarm_"

    OPEN_THEME_START_WITH: Final[str] = "open_theme_"
    OPEN_NOTE_START_WITH: Final[str] = "open_note_"
    OPEN_ALARM_START_WITH: Final[str] = "open_alarm_"

    DELETE_THEME_START_WITH: Final[str] = "delete_theme_"
    DELETE_NOTE_START_WITH: Final[str] = "delete_note_"
    DELETE_ALARM_START_WITH: Final[str] = "delete_alarm_"

    SET_NEW_ALARM_TIME: Final[str] = "set_new_alarm_time"
    FINISH_ALARM: Final[str] = "finish_alarm"
    SET_ALARM_REPEATABLE: Final[str] = "set_alarm_repeatable"
    SET_ALARM_NOT_REPEATABLE: Final[str] = "set_alarm_not_repeatable"
    SET_ALARM_NEW_REPEAT_INTERVAL: Final[str] = "set_alarm_new_repeat_interval"

    CHANGE_FSM_USER_DATA: Final[str] = "change_fsm_user_data"

    SAVE: Final[str] = "save"

    ADD_ATTACHMENTS: Final[str] = "add_attachment"
    ADD_CHECKPOINT: Final[str] = "add_checkpoint"

    YES: Final[str] = "yes"
    NO: Final[str] = "no"

    @staticmethod
    def add_id_to_callback_string(callback_string: str, entity_id: str) -> str:
        return f"{callback_string}_{entity_id}"

    @staticmethod
    def get_id_from_callback(callback: str) -> str:
        return callback.split("_")[-1]

    def get_open_theme_callback(self, theme_id: str) -> str:
        return f"{self.OPEN_THEME_START_WITH}{theme_id}"

    def get_open_note_callback(self, note_id: str) -> str:
        return f"{self.OPEN_NOTE_START_WITH}{note_id}"

    def get_open_alarm_callback(self, alarm_id: str) -> str:
        return f"{self.OPEN_ALARM_START_WITH}{alarm_id}"

    def get_delete_theme_callback(self, theme_id: str) -> str:
        return f"{self.DELETE_THEME_START_WITH}{theme_id}"

    def get_delete_note_callback(self, note_id: str) -> str:
        return f"{self.DELETE_NOTE_START_WITH}{note_id}"

    def get_delete_alarm_note_callback(self, alarm_id: str) -> str:
        return f"{self.DELETE_ALARM_START_WITH}{alarm_id}"

    def get_create_new_note_callback(self, theme_id: str) -> str:
        return f"{self.CREATE_NOTE}{theme_id}"

    def get_create_new_alarm_callback(self, note_id: str) -> str:
        return f"{self.CREATE_ALARM}{note_id}"
