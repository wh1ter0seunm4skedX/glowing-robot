from operations.logs import log_action
from utils.database_utils import create_connection, close_connection, config
from mysql.connector import Error


def create_all_pages_table():
    """Create the all_pages table with the desired structure"""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return

        cursor = conn.cursor()
        # Change page_title to VARCHAR(255)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS all_pages (
            page_id INT(10) PRIMARY KEY,
            page_title VARCHAR(255),
            page_text TEXT
        )
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Table all_pages created successfully in {target_db}")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


