import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from schemas.user import User, UserStatus
from aiogram.filters import CommandStart, Command, CommandObject
from depends import get_database_user_service
from aiogram.types import Message
from dotenv import load_dotenv
import random
import datetime as dt
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag, TextLink, html_decoration
)
import string
load_dotenv()

TOKEN = getenv("BOT_TOKEN")
SYMBOLS_FOR_SALT = "ABC"
dp = Dispatcher()


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
async def test(message: Message) -> None:
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