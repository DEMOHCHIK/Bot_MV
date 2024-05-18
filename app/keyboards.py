from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_gifts

start_reply_keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Добавить партнёра')]],
                                                 resize_keyboard=True,
                                                 input_field_placeholder='Добавьте партнёра!',
                                                 one_time_keyboard=True)

# -- Основное главное меню --
main_reply_keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Список желаемого(партнёра)')],
                                                          [types.KeyboardButton(text='Список желаемого(свой)')],
                                                          [types.KeyboardButton(text='Добавить желаемое')]],
                                                resize_keyboard=True,
                                                input_field_placeholder='Выберите пункт меню...')


async def gifts(user_id):
    all_gifts = await get_gifts(user_id)

    if all_gifts:
        keyboard = InlineKeyboardBuilder()
        for gift in all_gifts:
            keyboard.add(types.InlineKeyboardButton(text=gift.name, callback_data=f"gift_{gift.id}"))
# -- Возврат на главную --
        # keyboard.add(types.InlineKeyboardButton(text='Вернуться к меню', callback_data='to_main'))
        return keyboard.adjust(1).as_markup()
    else:
        return None
