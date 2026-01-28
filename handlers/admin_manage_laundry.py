from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.admin_manage_laundry_keyboards import get_machines_kb
from config import ADMIN_CHAT_ID

manage_laundry_router = Router()


@manage_laundry_router.message(Command("manage_laundry"))
async def manage_laundry(message: Message):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        await message.answer("Выберите машину:", reply_markup=get_machines_kb())


@manage_laundry_router.callback_query(F.data == "exit_from_manage_machines")
async def exit_from_manage_machines(cb: CallbackQuery):
    await cb.message.delete()