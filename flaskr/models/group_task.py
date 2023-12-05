from models import BaseModel, Group
from sqlalchemy import Column, String, ForeignKey, Boolean, Integer, Date, event
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from typing import TYPE_CHECKING
from datetime import date


if TYPE_CHECKING:
    from models import Group



class GroupTask(BaseModel):
    __tablename__ = "group_tasks"
    __table_args__ = (UniqueConstraint('group_id', 'name', name='_group_id_name_uc'),)
    group_id = Column(ForeignKey(Group.id), nullable=False)
    name = Column(String(50), nullable=False)
    recurring = Column(Boolean, nullable=False)
    recurring_time = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    tasks = relationship('Task', back_populates="group_task")
    group = relationship('Group', back_populates="group_tasks")


 
    