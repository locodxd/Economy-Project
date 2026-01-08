from datetime import datetime, timedelta
from typing import Dict, Any

class CooldownManager:
    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, datetime]] = {}

    def set_cooldown(self, user_id: str, command: str, duration: int) -> None:
        """Set a cooldown for a specific command for a user."""
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        self.cooldowns[user_id][command] = datetime.now() + timedelta(seconds=duration)

    def check_cooldown(self, user_id: str, command: str) -> (bool, int):
        """Check if a user is on cooldown for a specific command."""
        if user_id in self.cooldowns and command in self.cooldowns[user_id]:
            remaining_time = (self.cooldowns[user_id][command] - datetime.now()).total_seconds()
            if remaining_time > 0:
                return True, int(remaining_time)
            else:
                del self.cooldowns[user_id][command]
        return False, 0

    def reset_cooldown(self, user_id: str, command: str) -> None:
        """Reset the cooldown for a specific command for a user."""
        if user_id in self.cooldowns and command in self.cooldowns[user_id]:
            del self.cooldowns[user_id][command]