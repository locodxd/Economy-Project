from typing import Dict, Any

class UserData:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.wallet = 0
        self.bank = 0
        self.daily_streak = 0
        self.last_daily = None
        self.last_weekly = None
        self.inventory: Dict[str, int] = {}
        self.jobs: Dict[str, Any] = {}
        self.missions: Dict[str, Any] = {}

    def add_money(self, amount: int, source: str = "wallet"):
        if source == "wallet":
            self.wallet += amount
        elif source == "bank":
            self.bank += amount

    def remove_money(self, amount: int, source: str = "wallet"):
        if source == "wallet":
            if self.wallet >= amount:
                self.wallet -= amount
                return True
            return False
        elif source == "bank":
            if self.bank >= amount:
                self.bank -= amount
                return True
            return False
        return False

    def update_daily_streak(self, increment: bool = True):
        if increment:
            self.daily_streak += 1
        else:
            self.daily_streak = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "wallet": self.wallet,
            "bank": self.bank,
            "daily_streak": self.daily_streak,
            "last_daily": self.last_daily,
            "last_weekly": self.last_weekly,
            "inventory": self.inventory,
            "jobs": self.jobs,
            "missions": self.missions,
        }