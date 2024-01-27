from dataclasses import dataclass
from typing import Final


@dataclass
class Callbacks:
    CANCEL_FSM: Final[str] = "cancel_fsm"
    CANCEL: Final[str] = "cancel"
    DONE: Final[str] = "done"

    OPEN_MAIN_MENU: Final[str] = "main_menu"
    open_all_themes: Final[str] = "open_all_themes"
    open_all_theme_notes: Final[str] = "open_all_theme_notes"
    open_all_note_alarms: Final[str] = "open_all_note_alarms"

    create_theme: Final[str] = "create_theme"
    CREATE_NOTE: Final[str] = "create_note_"
    CREATE_ALARM: Final[str] = "create_alarm_"

    open_theme_start_with: Final[str] = "open_theme_"
    open_note_start_with: Final[str] = "open_note_"
    open_alarm_start_with: Final[str] = "open_theme_"

    delete_theme_start_with: Final[str] = "delete_theme_"
    delete_note_start_with: Final[str] = "delete_note_"
    delete_alarm_start_with: Final[str] = "delete_alarm_"

    CHANGE_FSM_USER_DATA: Final[str] = "change_fsm_user_data"

    SAVE: Final[str] = "save"

    ADD_ATTACHMENTS: Final[str] = "add_attachment"
    ADD_CHECKPOINT: Final[str] = "add_checkpoint"

    YES: Final[str] = "yes"
    NO: Final[str] = "no"

    def get_open_theme_callback(self, theme_id: str) -> str:
        return f"{self.open_theme_start_with}{theme_id}"

    def get_open_note_callback(self, note_id: str) -> str:
        return f"{self.open_note_start_with}{note_id}"

    def get_open_alarm_callback(self, alarm_id: str) -> str:
        return f"{self.open_alarm_start_with}{alarm_id}"

    def get_delete_theme_callback(self, theme_id: str) -> str:
        return f"{self.delete_theme_start_with}{theme_id}"

    def get_delete_note_callback(self, note_id: str) -> str:
        return f"{self.delete_note_start_with}{note_id}"

    def get_delete_alarm_note_callback(self, alarm_id: str) -> str:
        return f"{self.delete_alarm_start_with}{alarm_id}"

    def get_create_new_note_callback(self, theme_id: str) -> str:
        return f"{self.CREATE_NOTE}{theme_id}"

    def get_create_new_alarm_callback(self, note_id: str) -> str:
        return f"{self.CREATE_ALARM}{note_id}"

    @staticmethod
    def get_id_from_callback(callback: str) -> str:  # TODO handle possible exception
        return callback.split("_")[-1]
