import pytest
from datetime import datetime, timedelta
from jwt import encode
from flaskr.db import db
from flaskr.models import User, Group, Expense, Task, GroupTask
from dotenv import load_dotenv
import os

load_dotenv()

def jwt_factory(aud="authenticated", exp=datetime.utcnow() + timedelta(minutes=15), iat=datetime.utcnow(), sub=None, key=os.getenv("SUPABASE_JWT_SECRET")):
    return encode({
        "aud": aud,
        "exp": exp,
        "iat": iat,
        "sub": sub
    },
    key=key)

@pytest.fixture
def user_plus_session(app):
    with app.app_context():
        api_user = User(username="api_user")
        db.session.add(api_user)
        db.session.commit()
        token = jwt_factory(sub=str(api_user.id))
    return {"user": api_user, "token": token}

@pytest.fixture
def sessioned_user(user_plus_session):
    """Works with token()"""
    return user_plus_session["user"]

@pytest.fixture
def sessioned_user_token(user_plus_session):
    """Works with sessioned_user()"""
    return user_plus_session["token"]

@pytest.fixture
def get_sessioned_user_expenses(sessioned_user):
    """Works with sessioned_user()"""
    other_user = db.session.query(User).filter(User.id != sessioned_user.id).first()
    debits = []
    credits = []
    for n in range(4):
        credit = Expense(name=f"test_credit_{n}", creditor_id=sessioned_user.id, debitor_id=other_user.id, amount=10)
        debit = Expense(name=f"test_debit_{n}", creditor_id=other_user.id, debitor_id=sessioned_user.id, amount=20)
        debits.append(debit)
        credits.append(credit)
    db.session.add_all([*debits, *credits])
    db.session.commit()
    return {"debits": debits, "credits": credits, "other_user": other_user}

@pytest.fixture
def get_sessioned_user_tasks(sessioned_user):
    """Works with sessioned_user()"""
    test_group = db.session.query(Group).filter(Group.name == "test_group").first()
    group_task = GroupTask(name="test_group_task", group_id=test_group.id, recurring=True, recurring_time=7, start_date=datetime.utcnow())
    db.session.add_all([sessioned_user, group_task])
    sessioned_user.groups.append(test_group)
    db.session.commit()
    task = Task(user_id=sessioned_user.id, group_tasks_id=group_task.id, due_date=datetime.utcnow())
    db.session.add(task)
    db.session.commit()
    return {"task": task, "group_task": group_task}

    

# Authorization tests
def test_ok_api_auth(user_plus_session, client):
    token = user_plus_session["token"]
    request = client.get("api/self_user", headers={"Authorization": f"Bearer {token}"})
    assert request.status_code == 200

def test_no_auth_local(local_client):
    user_id = db.session.query(User).first().id
    request = local_client.get(f"api/user/{str(user_id)}")
    assert request

def test_wrong_secret_jwt_auth(client):
    user_id = db.session.query(User).first().id
    token = jwt_factory(key="wrong", sub=str(user_id))
    assert client.get("api/self_user", headers={"Authorization": f"Bearer {token}"}).status_code == 401

def test_expired_jwt_auth(client):
    user_id = db.session.query(User).first().id
    token = jwt_factory(exp=datetime.utcnow() - timedelta(minutes=15), sub=str(user_id))
    request = client.get("api/self_user", headers={"Authorization": f"Bearer {token}"})
    assert (request.status_code == 401 and request.json["message"] == "Token expired")

def test_query_other_user_id(user_plus_session, client):
    user = user_plus_session["user"]
    token = user_plus_session["token"]
    other_user_id = db.session.query(User).filter(User.id != user.id).first().id
    request = client.get(f"api/user/{str(other_user_id)}", headers={"Authorization": f"Bearer {token}"})
    assert (request.status_code == 401 and request.json["message"] == "You are not allowed to access this User")



# Endpoints tests
def test_post_tasks(client, sessioned_user, sessioned_user_token):
    payload = {
        "data":
            {
                "name": "Nettoyer la salle de bains",
                "description": "Laver les surfaces, la cabine de douche et le lavabo de la SDB",
                "isRecurrent": True,
                "frequencyNumber": 1,
                "frequency": "week",
                "selectedDateStart":"2023-11-20"
            }
        }
    test_group = db.session.query(Group).filter(Group.name == "test_group").first()
    db.session.add(sessioned_user)
    sessioned_user.groups.append(test_group)
    db.session.commit()
    request = client.post("api/task", headers={"Authorization": f"Bearer {sessioned_user_token}"}, json=payload)
    assert request.status_code == 200

def test_delete_task(client, sessioned_user_token, get_sessioned_user_tasks):
    task = get_sessioned_user_tasks["task"]
    db.session.add(task)
    request = client.delete(f"api/task/{str(task.id)}", headers={"Authorization": f"Bearer {sessioned_user_token}"})
    assert request.status_code == 200

def test_get_parametric_expenses(client, sessioned_user_token, get_sessioned_user_expenses):
    other_user = get_sessioned_user_expenses["other_user"]
    db.session.add(other_user)
    other_user_id = str(other_user.id)
    request = client.get(f"api/expense?creditor_id={other_user_id}&debitor_id={other_user_id}", headers={"Authorization": f"Bearer {sessioned_user_token}"})
    assert len(request.json) == 8

def test_get_expenses_with_id(client, sessioned_user_token, get_sessioned_user_expenses):
    expense = get_sessioned_user_expenses["debits"][0]
    db.session.add(expense)
    request = client.get(f"api/expense/{str(expense.id)}", headers={"Authorization": f"Bearer {sessioned_user_token}"})
    assert request.json["amount"] == expense.amount

def test_get_expense_with_unallowed_id(client, sessioned_user, sessioned_user_token):
    db.session.add(sessioned_user)
    users = db.session.query(User).filter(User.id != sessioned_user.id).all()
    user1 = users[1]
    user2 = users[2]
    expense = Expense(name="foreign_expense", creditor_id=user1.id, debitor_id=user2.id, amount=10)
    db.session.add(expense)
    db.session.commit()
    request = client.get(f"api/expense/{str(expense.id)}", headers={"Authorization": f"Bearer {sessioned_user_token}"})
    assert request.json["message"] == "You are not allowed to access this Expense"