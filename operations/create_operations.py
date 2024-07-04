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


def create_view_in_my_wiki(user, source_db='my_wiki'):
    """Create or replace the latest_text_view view in my_wiki."""
    try:
        # Connect to the source database to create the view
        source_conn = create_connection(source_db)
        if source_conn is None:
            print(f"Failed to connect to the database: {source_db}")
            return

        source_cursor = source_conn.cursor()
        source_cursor.execute("""
            CREATE OR REPLACE VIEW latest_text_view AS
            SELECT p.page_id, p.page_title, t.old_text
            FROM page p
            INNER JOIN text t ON p.page_latest = t.old_id
        """)
        source_conn.commit()

        print("View 'latest_text_view' created successfully in my_wiki.")
        log_action(user, "create_view", "latest_text_view created/replaced in my_wiki")

    except Error as e:
        print(f"Error creating view in MySQL: {e}")
        log_action(user, "error", f"Error creating view in my_wiki: {e}")
    finally:
        if source_conn:
            close_connection(source_conn)


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


def check_and_create_view_in_my_wiki(user):
    """Check if 'latest_text_view' exists in 'my_wiki', create if it does not exist."""
    try:
        conn = create_connection('my_wiki')
        if not conn:
            print(f"Failed to connect to the database: my_wiki")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW FULL TABLES IN `my_wiki` WHERE TABLE_TYPE LIKE 'VIEW' AND TABLES_IN_my_wiki = 'latest_text_view'")
        view_exists = cursor.fetchone()

        if view_exists:
            print("'latest_text_view' already exists in 'my_wiki'. No need to create it.")
        else:
            create_view_in_my_wiki(user)

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)

def check_and_create_view_in_target_db(user):
    """Check if 'latest_text_view' exists in the current target database, create if it does not exist."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return

        cursor = conn.cursor()
        cursor.execute(f"SHOW FULL TABLES IN `{target_db}` WHERE TABLE_TYPE LIKE 'VIEW' AND TABLES_IN_{target_db} = 'latest_text_view'")
        view_exists = cursor.fetchone()

        if view_exists:
            print(f"'latest_text_view' already exists in {target_db}. No need to create it.")
        else:
            create_view_in_target_db(user)

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)

def create_view_in_target_db(user, source_db=None):
    """Create or replace the latest_text_view view in the current target database."""
    target_db = config['database']
    try:
        if source_db is None:
            source_db = target_db

        # Connect to the source database to create the view
        source_conn = create_connection(source_db)
        if source_conn is None:
            print(f"Failed to connect to the database: {source_db}")
            return

        source_cursor = source_conn.cursor()
        source_cursor.execute("""
            CREATE OR REPLACE VIEW latest_text_view AS
            SELECT p.page_id, p.page_title, t.old_text
            FROM page p
            INNER JOIN text t ON p.page_latest = t.old_id
        """)
        source_conn.commit()

        print(f"View 'latest_text_view' created successfully in {target_db}.")
        log_action(user, "create_view", f"latest_text_view created/replaced in {target_db}")

    except Error as e:
        print(f"Error creating view in MySQL: {e}")
        log_action(user, "error", f"Error creating view in {target_db}: {e}")
    finally:
        if source_conn:
            close_connection(source_conn)
