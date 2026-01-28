from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_machine_names


def get_machines_kb() -> InlineKeyboardMarkup:
    btns = [[InlineKeyboardButton(text=name, callback_data="empty")] for name in get_machine_names()]
    btns.append([InlineKeyboardButton(text="Отмена", callback_data="exit_from_manage_machines")])
    return InlineKeyboardMarkup(inline_keyboard=btns)

