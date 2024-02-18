from typing import Any

from src.models.alarm_model import AlarmModel, AlarmStatus
from src.models.themes_modles import ThemeModel


def get_alarm_menu_script(alarm: AlarmModel) -> str:
    return f"""
{alarm.name}\n
{alarm.description}\n
Сейчас напоминание {"активно" if alarm.status in [AlarmStatus.READY, AlarmStatus.QUEUE] else "не активно"}
Следующее напоминание будет: {alarm.times.next_notion_time.strftime("%d/%m/%y %H:%M")}    
Напоминаниее {"повторяющаяся" if alarm.is_repeatable else "не повторяющаяся"}
{f"Будет повторяться каждые {alarm.times.repeat_interval} мин." if alarm.is_repeatable else ""}
    """


def get_change_theme_accept_script(user_data: dict[str, Any]) -> str:
    theme: ThemeModel = user_data["theme"]

    text = "Изменения:"
    if user_data.get("new_name") is not None:
        text += f"\nИмя:\n'{theme.name}' -> '{user_data.get('new_name')}'"
    if user_data.get("new_description") is not None:
        text += f"\nОписание:\n'{theme.description}' -> '{user_data.get('new_description')}'"
    text += "\n\nВыберите что изменить или сохраните изменения"
    return text
