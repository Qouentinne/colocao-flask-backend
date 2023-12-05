from .base import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship



class Group(BaseModel):
    __tablename__ = "groups"
    name = Column(String(50), nullable=False)

    members = relationship('User', secondary='user_groups', viewonly=True, lazy=True)
    group_tasks = relationship('GroupTask', back_populates="group")