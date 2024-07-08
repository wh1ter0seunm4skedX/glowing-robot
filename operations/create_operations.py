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


def import_sql_file(user):
    """Import an SQL file into a database"""
    print("Choose the source database:")
    print("1. my_wiki")
    print("2. src_db")

    choice = input("Enter the number of your choice (1 or 2): ").strip()
    if choice == '1':
        database = 'my_wiki'
    elif choice == '2':
        database = 'src_db'
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    sql_file_path = input("Enter the absolute path to the SQL file: ").strip()

    try:
        conn = create_connection(database)
        if not conn:
            print(f"Failed to connect to the database: {database}")
            return

        cursor = conn.cursor()
        with open(sql_file_path, 'r') as file:
            sql_commands = file.read()
            for command in sql_commands.split(';'):
                if command.strip():
                    try:
                        cursor.execute(command)
                    except Warning as w:
                        print(f"Warning: {w}")
        conn.commit()
        print(f"SQL file {sql_file_path} imported into {database}")
        log_action(user, "import_sql", f"SQL file {sql_file_path} imported into {database}")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)
