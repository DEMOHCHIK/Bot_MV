from aiogram import types, F, Router
import aiogram.filters as fl

from aiogram.fsm.context import FSMContext

from app.states import Gift, Partner
import app.keyboards as kb
import app.database.requests as rq

router = Router()


@router.message(fl.CommandStart())
async def cmd_start(message: types.Message):
    await rq.set_user(message.from_user.id, message.from_user.username)
    await message.answer('Вас приветстует Gift Bot MV! Для начала работы добавьте/примите своего партнёра!😊❤',
                         reply_markup=kb.start_reply_keyboard)


@router.message(fl.Command(commands='menu'))
async def cmd_menu(message: types.Message):
    await message.answer('Выберите пункт меню:', reply_markup=kb.main_reply_keyboard)


@router.message(F.text == 'Список желаемого(партнёра)')
async def cmd_partner_gifts_list(message: types.Message):
    user_id = message.from_user.id
    user_gifts_markup = await kb.gifts(user_id)
    if user_gifts_markup:
        await message.answer('Список желаемых подарков вашего партнёра:')
    else:
        await message.answer('Список желаемых подарков вашего партнёра пуст..😪')


@router.message(F.text == 'Список желаемого(свой)')
async def cmd_my_gifts_list(message: types.Message):
    user_tg_id = message.from_user.id
    user_gifts_markup = await kb.gifts(user_tg_id)
    if user_gifts_markup:
        await message.answer('Список ваших желаемых подарков:', reply_markup=user_gifts_markup)
    else:
        await message.answer('Ваш список желаемого пуст..😪')


# -- Детальные просмотр Подарка --
@router.callback_query(F.data.startswith('gift_'))
async def gift_callback(callback: types.CallbackQuery):
    gift_data = await rq.get_gift(callback.data.split('_')[1])
    await callback.answer(f'{gift_data.name}')
    await callback.message.answer(f'🎁{gift_data.name}\n💻{gift_data.description}')


# -- Добавление Подарка --
@router.message(F.text == 'Добавить желаемое')
async def cmd_add_gift(message: types.Message, state: FSMContext):
    await state.set_state(Gift.name)
    await message.answer('Введите название нового желаемого подарка:')


@router.message(Gift.name)
async def cmd_add_gift_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Gift.description)
    await message.answer('Введите описание нового желаемого подарка:')


@router.message(Gift.description)
async def cmd_add_gift_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()

    name = data.get('name')
    description = data.get('description')
    user_tg_id = message.from_user.id

    await rq.create_gift(name, description, user_tg_id)

    await message.answer(f"Желаемый подарок '{name}' успешно добавлен!🤩")
    await state.clear()


# -- Добавление Партнёра --
@router.message(F.text == 'Добавить партнёра')
async def cmd_add_partner(message: types.Message, state: FSMContext):
    await state.set_state(Partner.username)
    await message.answer('Введите @username вашего будущего партнёра🧐')


@router.message(Partner.username)
async def cmd_search_partner(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text.lstrip('@'))
    data = await state.get_data()

    username = data.get('username')
    user = await rq.search_user(username)

    partner_1_id = await rq.get_user_id(message.from_user.id)

    if user:
        if user.tg_id == message.from_user.id:
            await message.answer('Вы не можете сделать себя своим партнёром!🤪')
        else:
            partners_connection = await rq.partners_connection(partner_1_id, user.id)

            if isinstance(partners_connection, bool):
                await message.answer(f'Пользователю {user.username} отправлено приглашение о партнёрстве!🤗',
                                     reply_markup=kb.main_reply_keyboard)
                await message.bot.send_message(
                    chat_id=user.tg_id,
                    text=f'Вам отправлено приглашение в партнёры от {message.from_user.username}!💞'
                )
            elif partners_connection.partner_2 == partner_1_id:
                await message.answer(
                    f'Пользователь {user.username} уже отправил вам приглашение о партнёрстве. '
                    'Нажмите "Принять партнёра"!😉')
            elif partners_connection.accepted:
                await message.answer('Вы уже состоите в партнёрстве, неужели хотите совершить страшный грех?🤨')
            else:
                await message.answer('Вы уже отправили приглашение, дождитесь пока партнёр примет его.😇')
    else:
        await message.answer('Пользователь с таким именем не найден в Базе.😭'
                             '\nПопросите вашего будущего партнёра зайти в Бота и нажать Старт.🤭')
    await state.clear()
