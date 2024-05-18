from app.database.models import async_session
from app.database.models import User, Gift
from sqlalchemy import select


# -- Запрос на добавление Пользователя в БД --
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


# -- Запрос на получение списка подарков Пользователя --
async def get_gifts(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User.id).where(User.tg_id == user_id))
        user_gifts = await session.scalars(select(Gift).where(Gift.author == user))
        return user_gifts.all()


# -- Запрос на создание подарка --
async def create_gift(name: str, description: str, author_id: int):
    async with async_session() as session:
        author_id = await session.scalar(select(User.id).where(User.tg_id == author_id))
        new_gift = Gift(name=name, description=description, author=author_id)
        session.add(new_gift)
        await session.commit()


# -- Запрос на детальную информацию о Подарке --
async def get_gift(gift_id):
    async with async_session() as session:
        return await session.scalar(select(Gift).where(Gift.id == gift_id))
