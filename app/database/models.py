import os
from dotenv import load_dotenv

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Gift(Base):
    __tablename__ = 'gifts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(140))
    author: Mapped[int] = mapped_column(ForeignKey('users.id'))


class Partner(Base):
    __tablename__ = 'partners'

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_1: Mapped[int] = mapped_column(ForeignKey('users.id'))
    partner_2: Mapped[int] = mapped_column(ForeignKey('users.id'))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
