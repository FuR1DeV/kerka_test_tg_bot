from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_admin = InlineKeyboardMarkup()

balance = InlineKeyboardButton(text='Список пользователей',
                               callback_data='check_users')
logs = InlineKeyboardButton(text='Выгрузка логов',
                            callback_data='logs')
change_balance = InlineKeyboardButton(text='Изменить баланс пользователя',
                                      callback_data='change_user_balance')
block_user = InlineKeyboardButton(text='Заблокировать | Разблокировать пользователя',
                                  callback_data='block_user')

inline_admin.row(balance)
inline_admin.row(logs)
inline_admin.row(change_balance)
inline_admin.row(block_user)
