from models import BaseModel, GroupTask, User
from sqlalchemy import Column, String, ForeignKey, Boolean, Integer, Date
from sqlalchemy.orm import relationship


class Task(BaseModel):
    __tablename__ = "tasks"
    group_tasks_id = Column(ForeignKey(GroupTask.id), nullable=False)
    user_id = Column(ForeignKey(User.id), nullable=False)
    due_date = Column(Date, nullable=True)
    done_date = Column(Date, nullable=True)

    group_task = relationship('GroupTask', back_populates="tasks")
    user = relationship('User', back_populates="tasks")    