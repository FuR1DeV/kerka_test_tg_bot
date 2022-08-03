import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

pay_btn = InlineKeyboardButton(text='Пополнить баланс', callback_data='pay')
pay_menu = InlineKeyboardMarkup(row_width=1)
pay_menu.insert(pay_btn)

cancel_btn = InlineKeyboardButton(text="Отмена", callback_data='cancel_pay')
cancel_menu = InlineKeyboardMarkup(row_width=1)
cancel_menu.insert(cancel_btn)


def buy_menu(is_url=True, url='', bill=''):
    logging.info('Запуск создания инлайн кнопок для платежа')
    menu = InlineKeyboardMarkup(row_width=1)
    if is_url:
        btn_url = InlineKeyboardButton(text="Ссылка на оплату", url=url)
        menu.insert(btn_url)
    btn_check = InlineKeyboardButton(text="Проверить оплату", callback_data="check_"+bill)
    btn_cancel = InlineKeyboardButton(text="Отмена", callback_data="cancel_pay")
    menu.insert(btn_check)
    menu.insert(btn_cancel)
    return menu
