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
from utils.payments import YooPay

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
    
    yoopay = YooPay()
    response = await yoopay.create_payment(
        amount=amount,
        telegram_id=callback.from_user.id,
    )
    payment_id = response.id
    payment_link = response.confirmation.confirmation_url
    
    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Совершите оплату по ссылке ниже",
        reply_markup=await generate_payment_keyboard(payment_link=payment_link, payment_id=payment_id)
    )
    
@dp.callback_query(lambda callback: callback.data.startswith("check_payment"))
async def check_payment_callback(callback: CallbackQuery):
    _, payment_id = callback.data.split(":")
    payment = await YooPay.payment_success(payment_id)
    if payment:
        answer = await process_successful_payment(callback)
    else:
        answer = await callback.message.answer("Оплата не прошла")
        
    await asyncio.sleep(3)
    await answer.delete()
    
async def process_successful_payment(callback: CallbackQuery):
    await callback.answer(".")
    await callback.message.delete()
    answer = await callback.message.answer("Оплата прошла успешно!")
    await Orm.update_user_bought(callback.from_user.id)
    
    await callback.message.answer(
        text=successful_payment_text
    )
    
    return answer
    
@dp.callback_query(F.data == "back")
async def back_callback_handler(callback: CallbackQuery):
    await callback.answer(".")
    await callback.message.delete()
    
    await send_start_message(callback)
    