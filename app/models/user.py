from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import synonym

from core.database import Base


class UserModel(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': "[schema_name]"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    fullname = Column(String)
    disabled = Column(Boolean)
    subscription = Column(Integer, ForeignKey('[schema_name].subscriptions.id'))

    # synonyms or aliases
    full_name = synonym('fullname')
