def format_currency(amount: float) -> str:
    """Format a currency amount with commas and a dollar sign."""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format a percentage value to two decimal places."""
    return f"{value:.2f}%"

def format_user_data(username: str, balance: float, bank_balance: float) -> str:
    """Format user data for display."""
    return f"**{username}**\nBalance: {format_currency(balance)}\nBank: {format_currency(bank_balance)}"

def format_item_list(items: dict) -> str:
    """Format a list of items for display."""
    return "\n".join([f"{item}: {quantity}" for item, quantity in items.items()])

def format_leaderboard(leaderboard: list) -> str:
    """Format the leaderboard for display."""
    formatted = "\n".join([f"{index + 1}. {user['username']} - {format_currency(user['balance'])}" for index, user in enumerate(leaderboard)])
    return f"**Leaderboard**\n{formatted}"