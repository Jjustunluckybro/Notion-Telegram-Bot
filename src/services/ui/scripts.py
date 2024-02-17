from src.models.alarm_model import AlarmModel, AlarmStatus


def get_alarm_menu_script(alarm: AlarmModel) -> str:
    return f"""
{alarm.name}\n
{alarm.description}\n
Сейчас напоминание {"активно" if alarm.status in [AlarmStatus.READY, AlarmStatus.QUEUE] else "не активно"}
Следующее напоминание будет: {alarm.times.next_notion_time.strftime("%d/%m/%y %H:%M")}    
Напоминаниее {"повторяющаяся" if alarm.is_repeatable else "не повторяющаяся"}
{f"Будет повторяться каждые {alarm.times.repeat_interval} мин." if alarm.is_repeatable else ""}
    """
