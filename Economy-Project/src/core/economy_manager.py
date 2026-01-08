from typing import Dict, Any

class EconomyManager:
    def __init__(self):
        self.user_balances: Dict[int, float] = {}
        self.user_transactions: Dict[int, List[Dict[str, Any]]] = {}

    def get_balance(self, user_id: int) -> float:
        return self.user_balances.get(user_id, 0.0)

    def add_money(self, user_id: int, amount: float) -> None:
        if user_id not in self.user_balances:
            self.user_balances[user_id] = 0.0
        self.user_balances[user_id] += amount
        self.log_transaction(user_id, amount, "add")

    def remove_money(self, user_id: int, amount: float) -> bool:
        if self.get_balance(user_id) >= amount:
            self.user_balances[user_id] -= amount
            self.log_transaction(user_id, -amount, "remove")
            return True
        return False

    def log_transaction(self, user_id: int, amount: float, action: str) -> None:
        if user_id not in self.user_transactions:
            self.user_transactions[user_id] = []
        self.user_transactions[user_id].append({
            "amount": amount,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })

    def get_transaction_history(self, user_id: int) -> List[Dict[str, Any]]:
        return self.user_transactions.get(user_id, [])

    def reset_user_balance(self, user_id: int) -> None:
        if user_id in self.user_balances:
            del self.user_balances[user_id]