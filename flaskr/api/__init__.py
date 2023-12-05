from flask_restful import Api
from api.resources.user import UserResource, TestPeopleResource
from api.resources.user_task import UserTaskResource
from flask_restful import Resource
from api.resources.user_expense import UserExpenseResource
from api.resources.user_group import UserGroupResource


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}    

def create_api(app):
    api = Api(app)
    api.add_resource(HelloWorld, '/test')
    api.add_resource(TestPeopleResource, '/api/all_users')
    api.add_resource(UserResource,
        '/api/self_user', 
        '/api/user/<string:query_id>')
    api.add_resource(UserTaskResource,
        '/api/task/<string:query_id>',
        '/api/task')
    api.add_resource(UserExpenseResource, 
        '/api/expense/<string:query_id>',
        '/api/expense')
    api.add_resource(UserGroupResource, '/api/user/group/<string:user_id>')
    return api