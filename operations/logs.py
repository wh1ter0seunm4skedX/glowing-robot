from mysql.connector import Error
from utils.database_utils import create_connection, close_connection, config

def log_action(user, operation, details):
    """Log an action in the logs table."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return

        cursor = conn.cursor()
        insert_sql = "INSERT INTO logs (user, operation, details) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (user, operation, details))
        conn.commit()
        print(f"Logged action: {operation} by {user}")

    except Error as e:
        print(f"Error logging action: {e}")
    finally:
        if conn:
            close_connection(conn)
