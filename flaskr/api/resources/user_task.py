import ast
from db import db
from utils.tasks import generate_tasks_from_group_task
from models import Task, User, GroupTask
from models.helpers import convert_unit_in_days
from schema import TaskSchema, GroupTaskSchema
from datetime import date, timedelta

from api.resources.auth_resource import AuthResource
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('data')


class UserTaskResource(AuthResource[Task]):
    def __init__(self):
        super().__init__(Task)

    def get(self, session_user_id: User.id | None = None, query_id: Task.id=None):
        # Règle : renvoyer les tasks d'un user avec les critères:
        # - done_date = None && due_date >= today - 3 jours
        # - done_date = today
        tasks_schema = TaskSchema(many=True)
        tasks = db.session.query(Task).filter(Task.user_id == session_user_id).options(joinedload(Task.group_task)).order_by(Task.due_date.asc()).limit(10)
        return tasks_schema.dump(tasks)
    
    def post(self, session_user_id):
        #get user group
        user = self.session.query(User).get(session_user_id)
        user_group = user.groups[0]

        # Read query
        args = parser.parse_args()['data']
        args: dict[str, str] = ast.literal_eval(args)

        # Check recurring
        is_recurring = args["isRecurrent"]
        assert isinstance(is_recurring, bool), "isRecurrent must be a boolean"

        # Build group_task object for schema
        group_task_args = {
            "name": args["name"],
            "group_id": user_group.id,
            "recurring": is_recurring,
            "recurring_time": convert_unit_in_days(float(args["frequencyNumber"]), args["frequency"]) if is_recurring else None,
            "start_date": args["selectedDateStart"],
        }
        # Check via schema & add to session
        try:
            group_task: GroupTask = GroupTaskSchema().load(group_task_args) #format de db ok (ou pas)
            self.session.add(group_task)
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            return "group_task already exists", 400
        except Exception:
            self.session.rollback()
            return "Unable to create group_task", 500        
        

        # Build task object for schema    
        #create tasks calendar
        tasks_list = generate_tasks_from_group_task(self.session, group_task, session_user_id)
        try:
            self.session.add_all(tasks_list)
            self.session.commit()
        except Exception:
            self.session.rollback()
            return "Unable to create asked tasks", 500
        return 200
        
    def delete(self, query_id):
        self.session.query(Task).filter(Task.id == query_id).delete()
        self.session.commit()
        return 200
    
    @classmethod
    def is_allowed_resource(cls, user: User, task: Task):
        return user.id == task.user_id

    
        
    