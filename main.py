import asyncio
import logging
import sys
import os

from dotenv import load_dotenv

from utils.variants import available_groups

load_dotenv()

from handlers import survey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    if message.chat.id < 0:
        pass
    else:
        await message.answer(
            f"Привет, {html.bold(message.from_user.full_name)}!\nЯ – бот для публикации ивентов. Желаете продолжить?",
            reply_markup=ReplyKeyboardRemove())
        await message.answer("\nВведи /survey, если хочешь начать заполнение.")




async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls

    dp.include_router(survey.router)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
