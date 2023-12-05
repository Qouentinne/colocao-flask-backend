from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field
from models import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        include_relationships = True
        load_instance = True
        transient = True
person_schema = UserSchema()
people_schema = UserSchema(many=True)

class UserMinimalSchema(SQLAlchemySchema): 
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
    id = auto_field()
    username = auto_field()

minimalperson_schema = UserMinimalSchema()
minimalpeople_schema = UserMinimalSchema(many=True)
