import pytest
from flaskr.db import db
from flaskr.models import Group, User, GroupTask, Task
from flaskr.utils.tasks import generate_tasks_from_group_task
from sqlalchemy.exc import IntegrityError
from datetime import date


@pytest.fixture
def recurring_group_task(app):
    with app.app_context():
        group = db.session.query(Group).filter(Group.name == "test_group").first()
        group_task = GroupTask(name="Laver les vitres", group_id=group.id, recurring=True, recurring_time=7, start_date=date(2021, 1, 1), end_date=date(2021, 2, 15))
        db.session.add(group_task)
        db.session.commit()
        return group_task

@pytest.mark.usefixtures("app_ctx")
def test_generate_tasks_from_group_task(recurring_group_task):
    group_task = recurring_group_task
    db.session.add(group_task)
    task_creator = group_task.group.members[0]
    generate_tasks_from_group_task(db.session, group_task, task_creator_id=task_creator.id, commit=True)
    assert len(group_task.tasks) == 7
    

@pytest.mark.usefixtures("app_ctx")
def not_same_name_group_task(group_task):
    group = group_task.group
    group_task2 = GroupTask(name="Laver les vitres", group_id=group.id, recurring=False)
    db.session.add(group_task2)
    with pytest.raises(IntegrityError):
        db.session.commit()

def test_hello(client):
    response = client.get('/')
    assert response.data == b'Hello, World!'