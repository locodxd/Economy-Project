from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransactionLog:
    """Class to handle transaction logging for the economy system."""

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def log_transaction(self, user_id, amount, transaction_type, description):
        """Logs a transaction to the database."""
        timestamp = datetime.now().isoformat()
        query = """
        INSERT INTO transactions (user_id, amount, transaction_type, description, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self.db_connection:
                self.db_connection.execute(query, (user_id, amount, transaction_type, description, timestamp))
            logger.info(f"Transaction logged: {user_id} - {amount} - {transaction_type} - {description}")
        except Exception as e:
            logger.error(f"Failed to log transaction: {e}")

    def get_user_transactions(self, user_id):
        """Retrieves all transactions for a specific user."""
        query = "SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC"
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, (user_id,))
            transactions = cursor.fetchall()
            return transactions
        except Exception as e:
            logger.error(f"Failed to retrieve transactions for user {user_id}: {e}")
            return []

    def clear_user_transactions(self, user_id):
        """Clears all transactions for a specific user."""
        query = "DELETE FROM transactions WHERE user_id = ?"
        try:
            with self.db_connection:
                self.db_connection.execute(query, (user_id,))
            logger.info(f"Cleared transactions for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to clear transactions for user {user_id}: {e}")