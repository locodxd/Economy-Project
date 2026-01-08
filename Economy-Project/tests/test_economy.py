import pytest
from src.core.economy_manager import EconomyManager
from src.core.user_data import UserData

@pytest.fixture
def economy_manager():
    return EconomyManager()

@pytest.fixture
def user_data():
    return UserData(user_id=1, username="TestUser")

def test_add_money(economy_manager, user_data):
    initial_balance = user_data.wallet
    amount_to_add = 500
    economy_manager.add_money(user_data, amount_to_add, "wallet")
    assert user_data.wallet == initial_balance + amount_to_add

def test_remove_money(economy_manager, user_data):
    economy_manager.add_money(user_data, 1000, "wallet")
    initial_balance = user_data.wallet
    amount_to_remove = 300
    economy_manager.remove_money(user_data, amount_to_remove, "wallet")
    assert user_data.wallet == initial_balance - amount_to_remove

def test_transfer_money(economy_manager, user_data):
    user_data2 = UserData(user_id=2, username="TestUser2")
    economy_manager.add_money(user_data, 1000, "wallet")
    economy_manager.transfer_money(user_data, user_data2, 200)
    assert user_data.wallet == 800
    assert user_data2.wallet == 200

def test_check_cooldown(economy_manager, user_data):
    economy_manager.set_cooldown(user_data.user_id, "daily", 60)
    on_cooldown, seconds = economy_manager.check_cooldown(user_data.user_id, "daily")
    assert on_cooldown is True
    assert seconds == 60

def test_user_data_initialization(user_data):
    assert user_data.user_id == 1
    assert user_data.username == "TestUser"
    assert user_data.wallet == 0
    assert user_data.bank == 0
    assert user_data.daily_streak == 0
    assert user_data.last_daily is None