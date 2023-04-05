from aiogram import types

from database import db_session, blacklist
from aiogram.dispatcher.filters import BoundFilter


class InBlackList(BoundFilter):
    async def check(self, msg: types.Message):
        db_sess = db_session.create_session()
        return db_sess.query(blacklist.Blacklist).filter_by(user_id=msg.from_user.id).count()


class IsBanword(BoundFilter):
    async def check(self, msg: types.Message):
        with open('data/banwords.txt') as file_with_banwords:
            return any(word in msg.text for word in map(lambda x: x.strip(), file_with_banwords.readlines()))
