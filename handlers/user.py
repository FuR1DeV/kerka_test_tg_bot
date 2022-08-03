import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from random import randint

import config
from bot import bot
from data import db
from markup.markup_user import pay_menu, buy_menu, cancel_menu

logger = logging.getLogger("bot.handlers.user")


class FSMUser(StatesGroup):
    pay = State()


async def start(message: types.Message):
    logger.debug("Проверка на блокировку пользователя")
    access_denied = 0
    if message.chat.type == 'private':
        if not db.db_obj.user_exists(message.from_user.id):
            db.db_obj.add_user(message.from_user.id,
                               message.from_user.first_name,
                               message.from_user.last_name)

        """Заполняем переменную users_dict пользователями из БД"""
        res = db.db_obj.all_users()
        users_dict = {}
        for i in res:
            users_dict[i[0]] = {"id": i[0], "user_id": i[1], "ban": i[5]}

        """В этом цикле мы найдём user_id и проверим есть ли там блокировка"""
        for i in users_dict.values():
            if message.from_user.id in i.values() and i.get('ban') == 1:
                access_denied = 1

        """Если блокировки нет, то мы приветствуем пользователя, а если есть, то мы его опечалим"""
        if not access_denied:
            await bot.send_message(message.from_user.id,
                                   f'Привет, {message.from_user.username} {config.HELLO}\n'
                                   f'Я - бот {config.ROBOT} для пополнения баланса.\n'
                                   'Нажмите на кнопку, чтобы пополнить баланс\n')
            await message.answer(config.DOWN,
                                 reply_markup=pay_menu)
        else:
            logger.info(f"Пользователь заблокирован "
                        f"{message.from_user.first_name} {message.from_user.last_name}")
            await bot.send_message(message.from_user.id, f"Ты заблокирован! {config.BAN}")


async def pay(callback: types.CallbackQuery):
    logger.debug("Запуск цепочки пополнения баланса")
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id,
                           "Введите сумму, на которую вы хотите пополнить баланс",
                           reply_markup=cancel_menu)
    await FSMUser.pay.set()


async def pay_balance(message: types.Message):
    logger.debug("Проверка на валидацию, и выставление счёта на оплату")
    if message.text.isdigit():
        message_money = int(message.text)
        if message_money >= 1:
            comment = f"Выставлен счёт для <b>{message.from_user.first_name}_{randint(1, 10000)}</b>"
            bill = config.P2P.bill(amount=message_money, lifetime=5, comment=comment)
            db.db_obj.add_check(message.from_user.id, message_money, bill.bill_id)
            await bot.send_message(message.from_user.id,
                                   f"Вам нужно отправить <b>{message_money}</b> руб на наш счёт QIWI\n"
                                   f"{comment}",
                                   reply_markup=buy_menu(url=bill.pay_url, bill=bill.bill_id))

        else:
            await bot.send_message(message.from_user.id,
                                   "Минимальная сумма для пополнения 1 руб.",
                                   reply_markup=cancel_menu)
    else:
        logger.info(f"Не валидные данные! - {message.text}")
        await bot.send_message(message.from_user.id, "Введите целое число")


async def check(callback: types.CallbackQuery, state: FSMContext):
    logger.debug("Запуск функции проверки оплаты")
    bill = str(callback.data[6:])
    info = db.db_obj.get_check(bill)
    if info:
        if str(config.P2P.check(bill_id=bill).status) == "PAID":
            user_money = db.db_obj.user_money(callback.from_user.id)
            money = int(info[2])
            db.db_obj.set_money(callback.from_user.id, user_money + money)
            db.db_obj.delete_check(bill_id=bill)
            await bot.send_message(callback.from_user.id, "Ваш счёт пополнен!\n"
                                                          "Хотите еще ? нажмите /start")
            logger.info(f"Пользователь {callback.from_user.id} {callback.from_user.first_name} "
                        f"успешно пополнил баланс")
            await state.finish()
        else:
            logger.warning(f"У пользователя {callback.from_user.id} {callback.from_user.first_name} "
                           f"платёж не прошел!")
            await bot.send_message(callback.from_user.id,
                                   "Платёж не прошел",
                                   reply_markup=buy_menu(False, bill=bill))
    else:
        logger.warning(f"У пользователя {callback.from_user.id} {callback.from_user.first_name}"
                       f"Счёт не найден")
        await bot.send_message(callback.from_user.id, "Счёт не найден")
        await state.finish()


async def cancel(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback.from_user.id} отменил пополнения баланса!")
    await bot.send_message(callback.from_user.id,
                           "Вы отменили пополнение баланса\n"
                           "Что бы вернуться в главное меню нажмите /start")
    await state.finish()


def user_handlers(dp: Dispatcher):
    logger.debug("Запуск регистрации user хэндлеров (обработчиков)")
    dp.register_message_handler(start, commands='start')
    dp.register_callback_query_handler(pay, text='pay')
    dp.register_callback_query_handler(cancel, text='cancel_pay', state=FSMUser.pay)
    dp.register_callback_query_handler(check, text_contains='check_', state=FSMUser.pay)
    dp.register_message_handler(pay_balance, state=FSMUser.pay)
