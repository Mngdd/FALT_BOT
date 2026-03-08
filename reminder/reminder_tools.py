import sqlite3

from crontab import CronTab
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).parent.parent))

from config import LAUNDRY_DATA_PATH, DB_PATH

# TODO: в идеале бы сделать ремайндеры настраиваемыми
# аля типа напомните мне за 5 минут до и после начала стирки

# TODO: можно для пущей надежности добавить мьютексы или чет такое при работе с крон,
#  но это же все асинхронно, так что хз

def add_reminders(chat_id: int, event_time: datetime, machine_num: int):
    cron = CronTab(user=True)  # текущий пользователь

    # тут возможно стоит чуть получше сделать, но пока так придумал
    base_dir = Path(__file__).parent
    # скрипт который шлет напоминание
    script_path = base_dir.parent / "reminder" / "send_cron_remind.py"
    # todo: поменять если у нас питон какой-то особенный надо запускать
    python_path = sys.executable


    reminders = [
        (event_time - timedelta(minutes=15),
         f"🔔 Напоминаем о стирке в машинке №{machine_num}. До начала осталось 15 минут."
         ),
        (event_time - timedelta(minutes=5),
         f"🔔 Напоминаем о стирке в машинке №{machine_num}. До начала 5 минут!"
         ),
        (event_time,
         f"⏰ Напоминаем, что машинка №{machine_num} ждет вас!"
         ),
    ]

    for remind_time, msg in reminders:
        if remind_time < datetime.now():
            continue

        ts = remind_time.strftime("%d_%H_%M_%S")

        comment = f"reminder_{chat_id}_{ts}_wm_{machine_num}"
        command = f'{python_path} {script_path} {chat_id} "{msg}" "{comment}"'

        # напоминалка должна быть уникальной...
        job = cron.new(command=command, comment=comment)
        job.setall(
            remind_time.minute,
            remind_time.hour,
            remind_time.day,
            remind_time.month,
            "*"
        )

    cron.write()

#гавнакод чтоб всем поставить уведы
def add_remind_to_all():
    def find_user_id(initials: str):
        # "marathon j." -> имя "marathon", инициал "j"
        parts = initials.strip().rstrip(".").split()
        if len(parts) < 2:
            return None

        surname = parts[0]
        name_initial = parts[1].rstrip(".")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id FROM users
                WHERE LOWER(surname) = LOWER(?)
                AND LOWER(SUBSTR(name, 1, 1)) = LOWER(?)
                LIMIT 1
            """, (surname, name_initial))
            row = cursor.fetchone()
            return row[0] if row else None

    with open(LAUNDRY_DATA_PATH, mode="r") as f:
        data = json.load(f)

    now = datetime.now() + timedelta(minutes=20)
    for date_str, numbers in data.items():
        for num, events in numbers.items():
            for event in events:
                event_time = datetime.strptime(f"{event[0]} {date_str}", "%H:%M %d.%m.%Y")
                if event_time > now:
                    user_id = find_user_id(event[2])
                    if user_id is not None:
                        print(f"уведомляем: дата [{event_time}]; машинка {num}; объект {event}; user_id: {user_id}")
                        add_reminders(user_id, event_time, num)



if __name__ == "__main__":
    add_remind_to_all()
