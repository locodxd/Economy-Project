import pytest
from src.core.database import Database

@pytest.fixture
def db():
    db = Database('database/economy.db')
    yield db
    db.close()

def test_create_user(db):
    user_id = 1
    username = "TestUser"
    db.create_user(user_id, username)
    user_data = db.get_user(user_id)
    assert user_data is not None
    assert user_data['username'] == username

def test_update_user_balance(db):
    user_id = 1
    db.update_user_balance(user_id, 1000)
    user_data = db.get_user(user_id)
    assert user_data['balance'] == 1000

def test_get_nonexistent_user(db):
    user_id = 999
    user_data = db.get_user(user_id)
    assert user_data is None

def test_delete_user(db):
    user_id = 1
    db.delete_user(user_id)
    user_data = db.get_user(user_id)
    assert user_data is None

def test_transaction_logging(db):
    user_id = 1
    db.create_user(user_id, "TestUser")
    db.update_user_balance(user_id, 1000)
    db.log_transaction(user_id, 1000, "deposit")
    transactions = db.get_transactions(user_id)
    assert len(transactions) > 0
    assert transactions[0]['amount'] == 1000
    assert transactions[0]['type'] == "deposit"