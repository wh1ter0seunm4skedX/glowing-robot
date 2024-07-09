import json
import os
from utils.database_utils import create_connection, close_connection, config, set_target_db
from mysql.connector import Error
from operations.summarization import summarize_text
import time

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

def fetch_random_pages():
    set_target_db('dev_db')  # Set the database to dev_db
    conn = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM pages ORDER BY RAND() LIMIT 10")
        pages = cursor.fetchall()
        return pages
    except Error as e:
        print(f"Error fetching random pages: {e}")
        return []
    finally:
        close_connection(conn)

def fetch_page_text(page_id):
    conn = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return ""

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT clean_text FROM pages WHERE id = %s", (page_id,))
        result = cursor.fetchone()
        return result[0] if result else ""
    except Error as e:
        print(f"Error fetching page text: {e}")
        return ""
    finally:
        close_connection(conn)

def show_random_pages():
    pages = fetch_random_pages()
    if not pages:
        return

    for page_id, title in pages:
        print(f"Page ID: {page_id}, Title: {title}")

def select_page_and_summarize():
    pages = fetch_random_pages()
    if not pages:
        return

    for page_id, title in pages:
        print(f"Page ID: {page_id}, Title: {title}")

    while True:
        user_input = input("\nEnter the ID of the page you want to summarize (or type 'done' to quit): ")
        if user_input.lower() == 'done':
            print("Going up...")
            break

        try:
            page_id = int(user_input)
            if page_id in [page[0] for page in pages]:
                text = fetch_page_text(page_id)
                if text:
                    print("Summarization process started...")
                    start_time = time.time()
                    summary = summarize_text(text)
                    end_time = time.time()
                    print("Summarization process ended.")
                    print(f"Time taken for summarization: {end_time - start_time:.2f} seconds")
                    print("\nSummary:")
                    print(summary)
                else:
                    print("No text found for the selected page.")
            else:
                print("Invalid ID selected.")
        except ValueError:
            print("Invalid input. Please enter a valid ID.")
