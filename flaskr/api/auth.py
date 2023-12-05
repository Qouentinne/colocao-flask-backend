from functools import wraps
import jwt
from flask import request
import os
from flask import current_app
from models import User
from dotenv import load_dotenv
from typing import Literal

def must_be_logged(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        load_dotenv()
        
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
            TokenAuth.is_valid_token(access_token)
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

def local_only(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if os.getenv("ENVIRONMENT") not in ("LOCAL", "TEST"):
            return {
                "message": "Unauthorized",
                "error": "Unauthorized"
            }, 401
        return func(*args, **kwargs)
    return decorated


class TokenAuth:
    @classmethod
    def is_valid_token(cls, token) -> User:
        db = current_app.extensions['sqlalchemy']
        try:
            data=jwt.decode(token, os.getenv("SUPABASE_JWT_SECRET"), algorithms=["HS256"], options={'verify_aud':False})
        except jwt.ExpiredSignatureError as e:
            raise e
        except Exception as e:
            raise e
        current_user=db.session.query(User).filter(User.id==data.get("sub")).one_or_none()
        if current_user is None:
            raise jwt.InvalidTokenError("Invalid access token")
        return current_user


class ApiKeyAuth:
    @classmethod
    def check_api_key(cls, api_key):
        pass