from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from models import Task, GroupTask

class GroupTaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GroupTask
        include_fk = True
        include_relationships = True
        load_instance = True
        transient = True
grouptask_schema = GroupTaskSchema()
grouptasks_schema = GroupTaskSchema(many=True)

class NestedGroupTaskSchema(SQLAlchemySchema):
    class Meta:
        model = GroupTask
        include_fk = True
        include_relationships = True
        load_instance = True
        transient = True
    id = auto_field()
    name = auto_field(dump_only=True)
    recurring = auto_field(dump_only=True)

class TaskSchema(SQLAlchemySchema):
    class Meta:
        model = Task
        include_relationships = True
        load_instance = True
        transient = True
    id = auto_field()
    user_id = auto_field()
    group_task = fields.Nested(NestedGroupTaskSchema())
    due_date = auto_field()
    done_date = auto_field(dump_only=True)
