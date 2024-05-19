import asyncio
import logging
import sys
from io import BytesIO
from os import getenv

import aiofiles
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

from schemas.cell import Cell
from schemas.user import User, UserStatus
from aiogram.filters import CommandStart, Command, CommandObject
from depends import get_database_user_service, get_database_map_service
from aiogram.types import Message
from dotenv import load_dotenv
import random
import datetime as dt
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag, TextLink, html_decoration
)
import string
from PIL import Image, ImageDraw

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
SYMBOLS_FOR_SALT = "ABC"
dp = Dispatcher()


async def save_image(path: str, image: memoryview) -> None:
    async with aiofiles.open(path, "wb") as file:
        await file.write(image)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    text = f"""<b>Привет 👋)</b>
    
это бот для регистрации и привязке аккаунта на сайте <a href='https://artemki77.ru'>artemki77.ru</a>

для регистрации вы можете воспользоваться командой /setpass, инструкция ниже

<b>доступные команды:</b>

1. /setpass
{html_decoration.pre('Команда для того чтобы задать или сменить пароль, формат: /setpass "ваш пароль"')}

2. /info
{html_decoration.pre('Сосояние сервера, а так же выводит карту')}

3. /me, /stats
{html_decoration.pre('выводит ваш статус, а так же важу статистику')}
"""
    username = message.from_user.username.lower()
    db_users = get_database_user_service()
    users_from_db = await db_users.get_user_by_username(username)
    if not users_from_db:
        user = User(
            username=username,
            last_click=dt.datetime.now(),
        )
        await db_users.add_user(user)

    await message.answer(text)


@dp.message(Command("test", "admin"))
async def test(message: Message) -> None:
    await message.answer("и чё?")


@dp.message(Command("info"))
async def command_info_handler(message: Message) -> None:
    KEY_INFO_DB = "INFO_IMG"
    db_map = get_database_map_service()
    result = await db_map.get_by_key(KEY_INFO_DB)
    count_click = str(await db_map.get_count_clicks())

    if result != count_click:
        all_map: list[Cell] = await db_map.get_all_map()
        if not all_map:
            await message.answer("карта пока пуста(")
            return

        img = Image.new('RGBA', (500, 500), 'white')
        buffer = BytesIO()
        idraw = ImageDraw.Draw(img)

        for cell in all_map:
            size_cell = 10  # px
            cell_cords = list(map(int, cell.cords.split()))
            cell_cords = list(map(lambda x: x * 10, cell_cords))
            cell_cords += list(map(lambda cord: cord + size_cell, cell_cords))

            idraw.rectangle(cell_cords, fill=cell.color)
        img.save(buffer, format="PNG")
        await save_image("info.png", buffer.getbuffer())
        await db_map.set_by_key(KEY_INFO_DB, count_click)
        await message.answer_photo(FSInputFile("info.png"))
    else:
        await message.answer_photo(FSInputFile("info.png"))


@dp.message(Command("setpass"))
async def command_setpass_handler(message: Message, command: CommandObject) -> None:
    if command.args is None:
        text = f"""
        {html_decoration.bold('❗️Вы не ввели пароль:')}
        {html_decoration.pre('/setpass "ваш пароль"')}
        """
        await message.answer(text)
        return

    username = message.from_user.username.lower()

    db_users = get_database_user_service()

    users_from_db = await db_users.get_user_by_username(username)
    if not users_from_db:
        user = User(
            username=username,
            last_click=dt.datetime.now(),
        )
        await db_users.add_user(user)
    else:
        user = users_from_db[0]

    new_password = command.args.strip()
    new_salt = "".join(random.sample(string.ascii_lowercase, 5))
    new_hash = db_users.hash_pass(new_password, new_salt)
    user.password_salt = new_salt
    user.password_hash = new_hash
    old_status = user.status
    user.status = UserStatus.activated
    await db_users.add_user(user)

    if old_status == UserStatus.at_registration:
        text = f"""
            {html_decoration.bold('✅Вы зарегистрировались')}
теперь вы можете войти на сайте <a href='https://artemki77.ru'>artemki77.ru</a>

логин: {username}
пароль:  {new_password}


{html_decoration.italic('сайт и бот сохраняют только хэши паролей')}
        """
        await message.answer(text)
    else:
        text = f"""
            ✅Вы поменяли пароль
теперь вы можете войти на сайте <a href='https://artemki77.ru'>artemki77.ru</a>

логин: {username}
пароль:  {new_password}


{html_decoration.italic('сайт и бот сохраняют только хэши паролей')}
        """
        await message.answer(text)


@dp.message(Command("me", "stats"))
async def command_stats_handler(message: Message) -> None:
    username = message.from_user.username.lower()

    db_users = get_database_user_service()

    users = await db_users.get_user_by_username(username)
    if not users:
        text = html_decoration.bold("❗Вас нету в базе данных или вы заблокированны:")
        await message.answer(text)
        return

    user = users[0]

    text = f"""
    👤{user.username}
{html_decoration.bold('роль:')}  {user.role.value}
{html_decoration.bold('статус:')} {user.status.value}
{html_decoration.bold('последний клик:')} {user.last_click.isoformat()}
{html_decoration.bold('количество кликов:')} {user.count_click}
    """

    await message.answer(text)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())