TOKEN = 'YOUR_DISCORD_BOT_TOKEN'  # Replace with your bot token
PREFIX = '!'  # Command prefix for the bot

# Configuration for the economy system
ECONOMY_CONFIG = {
    "daily_reward": 1000,
    "weekly_reward": 10000,
    "transfer_tax": 0.02,  # 2% tax on transfers
    "job_payment_range": {
        "min": 200,
        "max": 800
    },
    "gambling": {
        "min_bet": 10,
        "max_bet": 1000
    }
}

# Configuration for the game
GAME_CONFIG = {
    "screen_width": 800,
    "screen_height": 600,
    "fps": 60
}