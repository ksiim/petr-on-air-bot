import asyncio
from aiogram import F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, FSInputFile
)

from bot import dp, bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *
from .markups import *
from .states import *

@dp.message(Command('start'))
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await Orm.create_user(message)
    await send_start_message(message)
    await asyncio.sleep(5)
    # await asyncio.sleep(60*60*24)
    await send_mail(message.from_user.id)
    
async def send_mail(telegram_id):
    user = await Orm.get_user_by_telegram_id(telegram_id)
    
    if any([user.bought, user.sended]):
        return
    else:
        await Orm.update_user_sended(telegram_id, sended=True)
    
    await bot.send_message(
        chat_id=telegram_id,
        text=mail_text,
        reply_markup=start_markup
    )
    
async def send_start_message(message: Message):
    await bot.send_photo(
        chat_id=message.from_user.id,
        photo=start_photo,
        caption=await generate_start_text(message),
        reply_markup=start_markup
    )
    
@dp.callback_query(F.data == "themes")
async def themes_callback_handler(callback: CallbackQuery):
    await callback.answer(".")
    await callback.message.delete()
    
    await callback.message.answer(
        text=themes_text,
        reply_markup=themes_markup
    )
    
@dp.callback_query(F.data == "buy")
async def buy_callback_handler(callback: CallbackQuery):
    await callback.answer(".")
    await callback.message.delete()
    
    await callback.message.answer(
        text='После успешной оплаты...'
    )
    
@dp.callback_query(F.data == "back")
async def back_callback_handler(callback: CallbackQuery):
    await callback.answer(".")
    await callback.message.delete()
    
    await send_start_message(callback)
    