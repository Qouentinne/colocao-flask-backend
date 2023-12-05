from models import GroupTask, User, Task
from sqlalchemy.orm import session
import logging
from datetime import date, timedelta


def generate_tasks_from_group_task(session: session, group_task : GroupTask, task_creator_id: User.id, commit: bool = False) -> list[Task]:
    #Check user exists
    try:
        task_creator = session.query(User).get(task_creator_id)
    except Exception as e:
        raise RuntimeError(f"User with id {task_creator_id} does not exist")
    #Check user belongs to group_task group
    assert task_creator in group_task.group.members, f"User<{task_creator_id}> does not belong to group_task<{group_task.id}> group ({group_task.group.id})"

    task_date = group_task.start_date or date.today()
    task_list = []
    if group_task.recurring:
        #Recurring task -> create tasks for all members of the group for the coming year
        end_date = group_task.end_date or date.today() + timedelta(days=365)
        users_id = [user.id for user in group_task.group.members]
        counter = 0
        while task_date < end_date:
            current_user_id = users_id[counter % len(users_id)]            
            task = Task(group_tasks_id= group_task.id, due_date=task_date, user_id=current_user_id)
            task_list.append(task)
            task_date += timedelta(days=group_task.recurring_time)
            counter += 1
    else:
        #Non recurring task -> create one task at given date attributed to task creator
        task_list = [Task(group_tasks_id= group_task.id, due_date=task_date, user_id=task_creator_id)]
    if commit:
        session.add_all(task_list)
        session.commit()
    logging.info (f"Generated {len(task_list)} tasks from group_task<{group_task.id}>")
    return task_list