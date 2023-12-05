import uuid
from .base import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class User(BaseModel):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda:str(uuid.uuid1()))
    username = Column(String(50), nullable=False)
    
    debits = relationship('Expense', primaryjoin='User.id == Expense.debitor_id', back_populates="debitor")
    credits = relationship('Expense', primaryjoin='User.id == Expense.creditor_id', back_populates="creditor")

    groups = relationship('Group', secondary='user_groups', cascade="all, delete")

    tasks = relationship('Task', back_populates="user", cascade="all, delete-orphan")

#primaryjoin='(user_groups.c.user_id == User.id)', secondaryjoin='(user_groups.c.group_id == Group.id)',

