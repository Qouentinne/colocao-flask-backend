from sqlalchemy import ForeignKey, Column, Table
from .base import BaseModel

user_groups = Table(
    'user_groups',
    BaseModel.metadata,
    Column("user_id", ForeignKey('public.users.id'), primary_key=True),
    Column("group_id", ForeignKey('public.groups.id'), primary_key=True)
)