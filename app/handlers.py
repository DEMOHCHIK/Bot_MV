from aiogram import types, F, Router
import aiogram.filters as fl

from aiogram.fsm.context import FSMContext

from app.states import NewGift
import app.keyboards as kb
import app.database.requests as rq

router = Router()


@router.message(fl.CommandStart())
async def cmd_start(message: types.Message):
    await rq.set_user(message.from_user.id, message.from_user.username)
    await message.answer('Вас приветстует Gift Bot MV! Для начала работы добавьте своего партнёра в систему😊❤',
                         reply_markup=kb.start_reply_keyboard)


@router.message(fl.Command(commands='menu'))
async def cmd_menu(message: types.Message):
    await message.answer('Выберите пунтк меню:', reply_markup=kb.main_reply_keyboard)


@router.message(F.text == 'Список желаемого(свой)')
async def cmd_my_gifts_list(message: types.Message):
    user_id = message.from_user.id
    user_gifts_markup = await kb.gifts(user_id)
    if user_gifts_markup:
        await message.answer('Список ваших желаемых подарков:', reply_markup=user_gifts_markup)
    else:
        await message.answer("Ваш список желаемого пуст😪")

# -- Детальные просмотр Подарка --
@router.callback_query(F.data.startswith('gift_'))
async def gift_callback(callback: types.CallbackQuery):
    gift_data = await rq.get_gift(callback.data.split('_')[1])
    await callback.answer(f'{gift_data.name}')
    await callback.message.answer(f'🎁{gift_data.name}\n💻{gift_data.description}')


# -- Добавление Подарка --
@router.message(F.text == 'Добавить желаемое')
async def cmd_add_gift(message: types.Message, state: FSMContext):
    await state.set_state(NewGift.name)
    await message.answer("Введите название нового желаемого подарка:")


@router.message(NewGift.name)
async def cmd_add_gift_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewGift.description)
    await message.answer("Введите описание нового желаемого подарка:")


@router.message(NewGift.description)
async def cmd_add_gift_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()

    name = data.get('name')
    description = data.get('description')
    author_id = message.from_user.id

    await rq.create_gift(name, description, author_id)

    await message.answer(f"Желаемый подарок '{name}' успешно добавлен!🤩")
    await state.clear()
