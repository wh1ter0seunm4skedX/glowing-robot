from operations.logs import log_action
from utils.database_utils import create_connection, close_connection
from mysql.connector import Error

def remove_table(user, database, table_name):
    """Remove a table from a database"""
    try:
        conn = create_connection(database)
        if not conn:
            print(f"Failed to connect to the database: {database}")
            return

        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table {table_name} removed from {database}")
        log_action(user, "remove", f"Table {table_name} removed from {database}")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)
