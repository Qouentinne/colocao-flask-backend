from db import db
from models import User
from schema import UserSchema
from .auth_resource import AuthResource, TestResource


class UserResource(AuthResource[User]):
    def __init__(self):
        super().__init__(User)

    def get(self, session_user_id: User.id | None = None, query_id: User.id | None = None):
        user_id = query_id or session_user_id
        user = self.session.query(User).get(user_id)
        if not user:
            return {
                "message": "User not found",
                "error": "User not found"
            }, 404
        return UserSchema().dump(user)
    
    @classmethod
    def is_allowed_resource(cls, user, other_user):
        return user.id == other_user.id



class TestPeopleResource(TestResource):    
    def get(self):
        return UserSchema(many=True).dump(self.session.query(User).all())