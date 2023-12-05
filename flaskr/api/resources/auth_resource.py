import os
import jwt
from flask_restful import Resource
from api.auth import TokenAuth, local_only, must_be_logged
from flask import current_app, request
from typing import Generic, TypeVar, Type
from models import BaseModel, User
from functools import wraps
from dotenv import load_dotenv
import logging

M = TypeVar('M', bound=BaseModel)
load_dotenv()

class BaseResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.session = current_app.extensions['sqlalchemy'].session

class TestResource(BaseResource):
    method_decorators = [local_only]    

class AuthResource(BaseResource, Generic[M]):
    model: Type[M]

    def __init__(self, model: Type[M]) -> None:
        super().__init__()
        self.model = model
        self.method_decorators = {'get': [self.inject_request_kwargs, self.inject_session_user_id, self.authorization_required, self.must_be_logged],
                                  'post': [self.inject_request_kwargs, self.inject_session_user_id, self.must_be_logged],
                                  'delete': [self.authorization_required, self.must_be_logged]
                                  }
        self.current_user: User | None = None

    def must_be_logged(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):            
            #NOCHECK in local
            # if os.getenv("ENVIRONMENT") == "LOCAL":
            #     return func(*args, **kwargs)

            #Check for auth header
            auth_field = request.headers.get("Authorization", {})
            access_token = auth_field.removeprefix("Bearer ").strip() if auth_field else None
            if not access_token:
                return {
                    "message": "No authentication type found",
                    "error": "Unauthorized"
                }, 401
            
            #Check token
            try:
                self.current_user = TokenAuth.is_valid_token(access_token)
            except jwt.ExpiredSignatureError as e:
                return {
                    "message": "Token expired",
                    "error": str(e)
                }, 401
            except jwt.InvalidTokenError as e:
                return {
                    "message": "Invalid access token",
                    "error": str(e)
                }, 401
            except Exception as e:
                return {
                    "message": "Something went wrong during authentication",
                    "error": str(e)
                }, 500
            return func(*args, **kwargs)
        return decorated

    def authorization_required(self, func):
        """Check if the current_user is authorized to access the resource"""
        @wraps(func)
        def decorated(*args, **kwargs):
            #NOCHECK in local
            # if os.getenv("ENVIRONMENT") == "LOCAL":
            #     return func(*args, **kwargs)

            if not self.current_user:
                logging.error(f"no user available to further check authorization, check for self.current_user instantiation")
                return {
                    "error": "Server error"
                }, 500
            
            #If no query_id is specified, proceed, the resource will return all of the user's resources
            if not kwargs.get("query_id"):
                logging.info(f"no secific query_id specified, proceeding with user {self.model} request")
                return func(*args, **kwargs)                        
            
            #If asking for a specific resource, check if it exists
            requested_resource_id = kwargs.get("query_id")
            requested_resource = self.session.query(self.model).get(requested_resource_id)
            if not requested_resource:
                return {
                    "message": "Object not found",
                    "error": "Object not found"
                }, 404
                        
            #Use the subclass check method
            if not self.is_allowed_resource(self.current_user, requested_resource):
                logging.warning(f"User {self.current_user.id} is not allowed to access {requested_resource}<{requested_resource.id}>")
                return {
                    "message": f"You are not allowed to access this {self.model.__name__}",
                    "error": "Unauthorized"
                }, 401
            
            #If the user is allowed to access the resource, proceed
            return func(*args, **kwargs)
        return decorated
    
    def inject_session_user_id(self, func):
        """Inject the user_id in the kwargs"""
        @wraps(func)
        def decorated(*args, **kwargs):
            if self.current_user:
                kwargs["session_user_id"] = self.current_user.id
            return func(*args, **kwargs)
        return decorated
    
    def inject_request_kwargs(self, func):
        """Inject the request kwargs in the kwargs"""
        @wraps(func)
        def decorated(*args, **kwargs):
            kwargs.update(dict(request.args))
            return func(*args, **kwargs)
        return decorated

    @classmethod
    def is_allowed_resource(cls, user: User, resource: Type[M]) -> bool:
        raise NotImplementedError(f"Please implement the is_allowed_resource method in {cls.__name__}")

