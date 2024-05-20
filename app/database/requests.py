from app.database.models import async_session
from app.database.models import User, Gift, Partner
from sqlalchemy import select


# -- Запрос на получение id пользователя по tg_id --
async def get_user_id(user_tg_id):
    async with async_session() as session:
        user_id = await session.scalar(select(User.id).where(User.tg_id == user_tg_id))
        return user_id


# -- Запрос на получение объекта User по id пользователя --
async def get_user(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))
        return user


# -- Запрос на проверку/добавление пользователя в БД --
async def set_user(tg_id, username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, username=username))
            await session.commit()
        else:
            if user.username != username:
                user.username = username
                await session.commit()


# -- Запрос на поиск пользователя по username --
async def search_user(username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.username == username))

        if user:
            return user
        return None


# -- Запрос на создания приглашения в партнёры --
async def add_partners_connection(partner_1_id, partner_2_id):
    async with async_session() as session:
        session.add(Partner(partner_1=partner_1_id, partner_2=partner_2_id, accepted=False))
        await session.commit()


# -- Запрос на поиск приглашения по id пользователя --
async def check_in_partners(user_id):
    async with async_session() as session:
        partner_check = await session.scalar(
            select(Partner).where((Partner.partner_1 == user_id) | (Partner.partner_2 == user_id)))
        return partner_check


# -- Запрос на проверку открытого партнёрства --
async def check_accepted_partners(user_id):
    async with async_session() as session:
        partner_record = await session.scalar(
            select(Partner).where((Partner.partner_2 == user_id) & (Partner.accepted == False)))
        return partner_record


# -- Запрос на подтверждение партнёрства --
async def accepted_partners(partner_record_id):
    async with async_session() as session:
        partner_record = await session.get(Partner, partner_record_id)
        partner_record.accepted = True
        await session.commit()


# -- Запрос на отклонение партнёрства --
async def decline_partners(partner_record_id):
    async with async_session() as session:
        partner_record = await session.get(Partner, partner_record_id)
        await session.delete(partner_record)
        await session.commit()


# -- Запрос на получение списка подарков Пользователя --
async def get_gifts(user_id):
    async with async_session() as session:
        user_gifts = await session.scalars(select(Gift).where(Gift.author == user_id))
        return user_gifts.all()


# -- Запрос на создание подарка --
async def create_gift(name, description, user_tg_id):
    async with async_session() as session:
        user_id = await get_user_id(user_tg_id)
        session.add(Gift(name=name, description=description, author=user_id))
        await session.commit()


# -- Запрос на детальную информацию о Подарке --
async def get_gift(gift_id):
    async with async_session() as session:
        return await session.scalar(select(Gift).where(Gift.id == gift_id))
