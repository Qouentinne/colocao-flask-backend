from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Expense


class ExpenseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Expense
        include_fk = True
        include_relationships = True
        load_instance = True
        transient = True
expenses_schema = ExpenseSchema(many=True)