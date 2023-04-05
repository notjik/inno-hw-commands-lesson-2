import datetime
import sqlalchemy

from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Blacklist(SqlAlchemyBase):
    __tablename__ = 'blacklist'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.user_id'), unique=True, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship("Users", backref="blacklist", lazy=True)

    def __repr__(self):
        return '<Blacklist> [{}] {}'.format(self.id, self.user_id)
