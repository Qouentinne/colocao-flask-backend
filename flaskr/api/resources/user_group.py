from db import db
from models import User
from schema.user import minimalpeople_schema


from flask_restful import Resource


class UserGroupResource(Resource):
    def get(self, user_id):
        self_user = db.session.query(User).get(user_id)
        group = self_user.groups[0]
        group_members = group.members
        return minimalpeople_schema.dump(group_members)