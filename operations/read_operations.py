import json
import os
from utils.database_utils import create_connection, close_connection, config
from mysql.connector import Error


def get_mediawiki_base_url():
    return 'https://bo-botpress.bezeqonline.corp/'


def fetch_page_titles():
    """Fetch all page titles from the pages table."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM pages")
        titles = cursor.fetchall()
        return titles

    except Error as e:
        print(f"Error fetching page titles: {e}")
        return []
    finally:
        if conn:
            close_connection(conn)

