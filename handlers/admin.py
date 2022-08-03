import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile

import config
from bot import bot
from data import db
from markup.markup_admin import inline_admin

logger = logging.getLogger("bot.handlers.admin")


class FSMAdmin(StatesGroup):
    id = State()
    change_money = State()
    block_user = State()
    change_block_user = State()


async def start_admin(message: types.Message):
    logger.debug('Проводится валидация администратора')
    if message.from_user.id == config.ADMIN_ID:
        await bot.send_message(message.from_user.id,
                               f'{config.COOL} Администратор - {message.from_user.username}',
                               reply_markup=inline_admin)
    else:
        logger.info(f'Вход запрещен пользователю '
                    f'{message.from_user.first_name} {message.from_user.last_name}')
        await bot.send_message(message.from_user.id,
                               f'Вход запрещен! {config.BAN}')


async def check_users(callback: types.CallbackQuery):
    logger.debug('Проверяем пользователей в БД')
    result = db.db_obj.all_users()
    users_dict = {}
    for i in result:
        users_dict[i[0]] = {"id": i[0], "user_id": i[1], "first_name": i[2],
                            "last_name": i[3], "money": i[4], "ban": i[5]}
    await bot.send_message(callback.from_user.id, f"Всего пользователей {len(result)}\n")
    await bot.send_message(callback.from_user.id, f"Вывожу список...")
    for i in users_dict.values():
        """В цикле формируем данные каждого пользователя"""
        db_id, tg_id, first_name = i.get("id"), i.get("user_id"), i.get("first_name")
        last_name, money, ban = i.get("last_name"), i.get("money"), i.get("ban")
        ban_icon, blocked = None, ''
        if i.get("ban") == 0:
            ban_icon = config.NOT_BAN
            blocked = "Not"
        if i.get("ban") == 1:
            ban_icon = config.BAN
        """Выводим администратору красивые и информативные данные"""
        await bot.send_message(callback.from_user.id,
                               f"Database {config.ID} - <b>{db_id}</b> | "
                               f"Telegram {config.ID} - <b>{tg_id}</b> | "
                               f"Name {config.NAME} - <b>{first_name}</b> |"
                               f"Last Name {config.NAME} - <b>{last_name}</b> |"
                               f"Money {config.MONEY} - <b>{money}</b> |"
                               f"{blocked} Blocked {ban_icon} |")
    await bot.send_message(callback.from_user.id,
                           'Нажми сюда чтобы попасть в главное меню /admin')


async def change_balance(callback: types.CallbackQuery):
    logger.debug("Функция начала цепочки изменения баланса пользователя")
    await bot.send_message(callback.from_user.id, 'Введите id пользователя')
    await FSMAdmin.id.set()


async def balance(message: types.Message, state: FSMContext):
    logger.debug("Проверка валидности и наличие в БД")
    if message.text.isdigit():
        answer = int(message.text)
        result = db.db_obj.all_users()
        users_dict = {}
        for i in result:
            users_dict[i[0]] = {"id": i[0], "user_id": i[1], "money": i[4]}
        await state.update_data(answer_id=answer, users_dict=users_dict)
        if answer in users_dict:
            await message.answer(f"Да, есть такой юзер, вот его user_id - {users_dict[answer].get('user_id')}"
                                 f", вот его баланс - {users_dict[answer].get('money')}")
            await message.answer(f"Введите количество денег")
            await FSMAdmin.change_money.set()
        else:
            await message.answer(f'Юзер с таким id {answer} не найден!\n'
                                 f'Чтобы начать заново нажмите /admin')
            await state.finish()
    else:
        logger.info(f"Не валидные данные! - {message.text}")
        await message.answer("Это не целое число")


async def change_money(message: types.Message, state: FSMContext):
    logger.debug("Изменение количество денег в БД")
    if message.text.isdigit():
        answer_money = int(message.text)
        data = await state.get_data()
        answer_id = data.get("answer_id")
        users_dict = data.get("users_dict")
        db.db_obj.set_money(users_dict[int(answer_id)].get("user_id"), answer_money)
        await message.answer("Успешно изменили денежное состояние!\n"
                             "Вернуться в главное меню /admin")
        await state.finish()
    else:
        logger.info(f"Не валидные данные! - {message.text}")
        await message.answer("Нужно ввести целое число")


async def block_user(callback: types.CallbackQuery):
    logger.debug("Запуск блокирования пользователя")
    await bot.send_message(callback.from_user.id, 'Введите id пользователя')
    await FSMAdmin.block_user.set()


async def user(message: types.Message, state: FSMContext):
    logger.debug("Проверяем наличие пользователя в БД")
    if message.text.isdigit():
        answer = int(message.text)
        result = db.db_obj.all_users()
        users_dict = {}
        for i in result:
            users_dict[i[0]] = {"id": i[0], "user_id": i[1], 'first_name': i[2], "ban": i[5]}
        await state.update_data(answer_id=answer, users_dict=users_dict)
        if answer in users_dict:
            await message.answer(f"Да, есть такой юзер, вот его user_id - {users_dict[answer].get('user_id')}\n"
                                 f"А имя его {users_dict[answer].get('first_name')}")
            await message.answer(f"Если хотите заблокировать введите <b>любое положительное число</b>\n"
                                 f"Если хотите разблокировать введите <b>0</b>")
            await FSMAdmin.change_block_user.set()
        else:
            logger.info(f"Юзер с таким id {answer} не найден!")
            await message.answer(f'Юзер с таким id {answer} не найден!')
    else:
        logger.info(f"Не валидные данные! - {message.text}")
        await message.answer('Это не целое число\n'
                             'Введите id пользователя')


async def change_block_user(message: types.Message, state: FSMContext):
    logger.debug("Запуск блокировки или разблокировки пользователя")
    if message.text.isdigit():
        answer_0_or_1 = int(message.text)
        data = await state.get_data()
        answer_id = data.get("answer_id")
        users_dict = data.get("users_dict")
        if answer_0_or_1 >= 1:
            db.db_obj.block_user(users_dict[int(answer_id)].get("user_id"), 1)
            await message.answer(f"Пользователь в <b>заблокирован!</b> {config.BAN}\n"
                                 "Вернуться в админку /admin")
            await state.finish()
        if answer_0_or_1 == 0:
            db.db_obj.block_user(users_dict[int(answer_id)].get("user_id"), 0)
            await message.answer(f"Пользователь в <b>разблокирован!</b> {config.NOT_BAN}\n"
                                 "Вернуться в админку /admin")
            await state.finish()
    else:
        logger.info(f"Не валидные данные! - {message.text}")
        await message.answer("Нужно ввести любое положительное число если хочешь заблокировать\n"
                             "А если разблокировать то нажми 0")


async def uploading_logs(callback: types.CallbackQuery):
    logger.debug("Администратор запросил выгрузку логов")
    file_debug = InputFile("logs/info_debug.log")
    file_warning = InputFile("logs/err_warning.log")
    await bot.send_document(chat_id=callback.from_user.id, document=file_debug)
    await bot.send_document(chat_id=callback.from_user.id, document=file_warning)

        
def admin_handlers(dp: Dispatcher):
    logger.debug("Запуск регистрации admin хэндлеров (обработчиков)")
    dp.register_message_handler(start_admin, commands='admin')
    dp.register_callback_query_handler(uploading_logs, text='logs')
    dp.register_callback_query_handler(check_users, text='check_users')
    dp.register_callback_query_handler(change_balance, text='change_user_balance')
    dp.register_callback_query_handler(block_user, text='block_user')
    dp.register_message_handler(balance, state=FSMAdmin.id)
    dp.register_message_handler(change_money, state=FSMAdmin.change_money)
    dp.register_message_handler(user, state=FSMAdmin.block_user)
    dp.register_message_handler(change_block_user, state=FSMAdmin.change_block_user)
