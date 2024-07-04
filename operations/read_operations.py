import json
import os
from utils.database_utils import create_connection, close_connection, config
from mysql.connector import Error


def fetch_all_page_titles():
    """Fetch all page titles from the all_pages table."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT page_id, page_title FROM all_pages")
        titles = cursor.fetchall()
        # Since page_title is now VARCHAR, no need to decode
        decoded_titles = [(page_id, page_title) for page_id, page_title in titles]
        return decoded_titles

    except Error as e:
        print(f"Error fetching page titles: {e}")
        return []
    finally:
        if conn:
            close_connection(conn)


def fetch_page_text_by_id(page_id):
    """Fetch the page text by page_id from the all_pages table."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return None

        cursor = conn.cursor()
        cursor.execute("SELECT page_text FROM all_pages WHERE page_id = %s", (page_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    except Error as e:
        print(f"Error fetching page text: {e}")
        return None
    finally:
        if conn:
            close_connection(conn)


def list_tables(database):
    """List all tables in a database"""
    try:
        conn = create_connection(database)
        if not conn:
            print(f"Failed to connect to the database: {database}")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print(f"Tables in {database}:")
            for table in tables:
                print(table[0])
        else:
            print(f"No tables found in {database}")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def get_mediawiki_base_url():
    default_base_url = 'http://localhost:8081/'  # Default base URL
    if 'MEDIAWIKI_BASE_URL' in os.environ:
        return os.environ['MEDIAWIKI_BASE_URL']
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
            return config.get('mediawiki_base_url', default_base_url)
    except FileNotFoundError:
        print("config.json not found. Using default base URL.")
        return default_base_url


def check_if_view_exists_in_my_wiki():
    """Check if 'latest_text_view' exists in 'my_wiki'."""
    try:
        conn = create_connection('my_wiki')
        if not conn:
            print("Failed to connect to the database: my_wiki")
            return False

        cursor = conn.cursor()
        cursor.execute(
            "SHOW FULL TABLES IN `my_wiki` WHERE TABLE_TYPE LIKE 'VIEW' AND TABLES_IN_my_wiki = 'latest_text_view'")
        view_exists = cursor.fetchone()
        if view_exists:
            print("'latest_text_view' exists in 'my_wiki'.")
            return True
        else:
            print("'latest_text_view' does not exist in 'my_wiki'.")
            return False

    except Error as e:
        print(f"Error checking view existence in my_wiki: {e}")
        return False
    finally:
        if conn:
            close_connection(conn)


def check_if_view_exists_in_target_db():
    """Check if 'latest_text_view' exists in the current target database."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return False

        cursor = conn.cursor()
        cursor.execute(
            f"SHOW FULL TABLES IN `{target_db}` WHERE TABLE_TYPE LIKE 'VIEW' AND TABLES_IN_{target_db} = 'latest_text_view'")
        view_exists = cursor.fetchone()
        if view_exists:
            print(f"'latest_text_view' exists in {target_db}.")
            return True
        else:
            print(f"'latest_text_view' does not exist in {target_db}.")
            return False

    except Error as e:
        print(f"Error checking view existence in {target_db}: {e}")
        return False
    finally:
        if conn:
            close_connection(conn)


'''
def export_view_as_sql_file(view_name, database, file_path):
    """Export 'latest_text_view' as SQL file if exists in the given database."""
    try:
        conn = create_connection(database)
        if not conn:
            print(f"Failed to connect to the database: {database}")
            return

        cursor = conn.cursor()
        cursor.execute(f"SHOW FULL TABLES IN `{database}` WHERE TABLE_TYPE LIKE 'VIEW' AND TABLES_IN_{database} = '{view_name}'")
        view_exists = cursor.fetchone()

        if view_exists:
            cursor.execute(f"SHOW CREATE VIEW {view_name}")
            view_creation = cursor.fetchone()[1]
            with open(file_path, 'w') as file:
                file.write(f"{view_creation};")
            print(f"View '{view_name}' exported as SQL file to {file_path}.")
        else:
            print(f"View '{view_name}' does not exist in {database}.")

    except Error as e:
        print(f"Error exporting view as SQL file: {e}")
    finally:
        if conn:
            close_connection(conn)
'''
