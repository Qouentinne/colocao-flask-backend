import ast
from db import db
from models import User, Expense
from models.expense import get_per_user_amount
from schema.expense import expenses_schema, ExpenseSchema
from api.resources.auth_resource import AuthResource
from flask_restful import reqparse
from flask import current_app


class UserExpenseResource(AuthResource[Expense]):
    def __init__(self):
        super().__init__(Expense)
        self.method_decorators['delete']= [self.inject_session_user_id, self.authorization_required, self.must_be_logged]
    
    def get(self, session_user_id: User.id | None = None, query_id:Expense.id | None = None, **kwargs):
        #if an expense query_id is provided, return it
        if query_id:
            expense = self.session.query(Expense).get(query_id)
            return ExpenseSchema().dump(expense)
        
        #all other cases require a session_user_id
        querying_user = self.session.query(User).get(session_user_id)

        #if no kwargs were provided, get session_user_id's expenses
        if not kwargs:
            return get_per_user_amount(querying_user)

        #if provided, check if creditor_id or debitor_id in kwargs
        expenses = []
        if 'creditor_id' in kwargs:
            creditor_id = kwargs.pop('creditor_id')
            creditor_expenses = self.session.query(Expense).filter_by(creditor_id=creditor_id, debitor_id=session_user_id).all()
            expenses.extend(creditor_expenses)
        if 'debitor_id' in kwargs:
            debitor_id = kwargs.pop('debitor_id')
            debitor_expenses = self.session.query(Expense).filter_by(creditor_id=session_user_id, debitor_id=debitor_id).all()
            expenses.extend(debitor_expenses)
        return expenses_schema.dump(expenses)
       
    def post(self, session_user_id: User.id):
        parser = reqparse.RequestParser()
        parser.add_argument('data')
        args = parser.parse_args()['data']
        args = ast.literal_eval(args)
        expense_name = args['name']
        expense_date = args['date']
        data=[]
        for participant in args["participants"]:
            expense = {
                'creditor_id': session_user_id,
                'debitor_id': participant['id'],
                'created_at': expense_date,
                'name': expense_name,
                'amount': participant['amount']
            }
            data.append(expense)
        data_db = expenses_schema.load(data)
        self.session.add_all(data_db)
        self.session.commit()
        return 200
    
    def delete(self, session_user_id: User.id, query_id: Expense.id):
        expense_to_delete = self.session.query(Expense).get(query_id)
        if expense_to_delete.creditor_id != session_user_id:
            return "You are not the creditor of this expense", 400
        self.session.delete(expense_to_delete)
        self.session.commit()
        return 200

    @classmethod
    def is_allowed_resource(cls, user: User, expense: Expense):
        session = current_app.extensions['sqlalchemy'].session
        session.add_all([user, expense])
        return user.id == expense.creditor_id or user.id == expense.debitor_id

