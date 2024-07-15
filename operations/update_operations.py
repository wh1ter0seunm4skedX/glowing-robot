import os
from colorama import Fore, Style, init
from operations.logs import log_action
from operations.read_operations import get_mediawiki_base_url
from utils.text_processing import parse_database_text, parse_wikitext_to_clean_text
from utils.database_utils import create_connection, close_connection, config
from mysql.connector import Error
from operations.summarization import summarize_text
from datetime import datetime
import time
import sys
import threading

init(autoreset=True)


# Example usage
# import_csv_to_raw_page_data("username", "C:\\Users\\micha\\Downloads")
def import_csv_to_raw_page_data(user, dir_path):
    """Import data from the newest CSV file in the directory into the raw_page_data table and log the operation."""
    target_db = config['database']
    try:
        conn = create_connection(target_db, allow_local_infile=True)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "import_csv_to_raw_page_data", "Failed to connect to the database")
            return

        cursor = conn.cursor()

        # Check if the raw_page_data table exists
        cursor.execute("SHOW TABLES LIKE 'raw_page_data'")
        table_exists = cursor.fetchone()
        if not table_exists:
            print(f"Table 'raw_page_data' does not exist.")
            log_action(user, "import_csv_to_raw_page_data", f"Table 'raw_page_data' does not exist.")
            return

        # Find the newest CSV file in the directory
        files = [f for f in os.listdir(dir_path) if f.startswith("latest_pages_data_") and f.endswith(".csv")]
        if not files:
            print(f"No CSV file found in the directory {dir_path}")
            log_action(user, "import_csv_to_raw_page_data", f"No CSV file found in the directory {dir_path}")
            return

        full_paths = [os.path.join(dir_path, f) for f in files]
        file_path = max(full_paths, key=os.path.getctime)

        # Enable local infile globally
        cursor.execute("SET GLOBAL local_infile = 1;")

        # Load data from the CSV file into raw_page_data
        import_query = f"""
        LOAD DATA LOCAL INFILE '{file_path.replace("\\", "\\\\")}'
        INTO TABLE raw_page_data
        FIELDS TERMINATED BY ','
        ENCLOSED BY '\"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS
        (latest_page_id, page_title, page_text, export_time)
        SET import_time = NOW();
        """

        cursor.execute(import_query)
        conn.commit()

        print(f"Data from {file_path} has been successfully imported into the raw_page_data table.")
        log_action(user, "import_csv_to_raw_page_data", f"Data from {file_path} imported successfully")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "import_csv_to_raw_page_data", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def copy_n_convert(user, source_table='raw_page_data', target_table='pages'):
    """Copy data from raw_page_data to pages, sanitize title and text, and set sum entry to empty string."""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "copy_n_convert", "Failed to connect to the database")
            return

        cursor = conn.cursor()

        # Check if the source table exists
        cursor.execute(f"SHOW TABLES LIKE '{source_table}'")
        source_exists = cursor.fetchone()
        if not source_exists:
            print(f"Source table '{source_table}' does not exist.")
            log_action(user, "copy_n_convert", f"Source table '{source_table}' does not exist.")
            return

        # Check if the target table exists
        cursor.execute(f"SHOW TABLES LIKE '{target_table}'")
        target_exists = cursor.fetchone()
        if not target_exists:
            print(f"Target table '{target_table}' does not exist.")
            log_action(user, "copy_n_convert", f"Target table '{target_table}' does not exist.")
            return

        # Truncate the target table to delete existing data
        cursor.execute(f"TRUNCATE TABLE {target_table}")

        # Fetch data from the source table (raw_page_data)
        cursor.execute(f"SELECT latest_page_id, page_title, page_text FROM {source_table}")
        rows = cursor.fetchall()

        base_url = get_mediawiki_base_url()

        if rows:
            for row in rows:
                page_id, page_title, page_text = row

                # Sanitize the title
                if isinstance(page_title, bytearray):
                    page_title = bytes(page_title).decode('utf-8')
                elif isinstance(page_title, bytes):
                    page_title = page_title.decode('utf-8')
                page_title = page_title.replace('_', ' ')

                # Sanitize the text
                if isinstance(page_text, bytearray):
                    page_text = bytes(page_text).decode('utf-8')
                elif isinstance(page_text, bytes):
                    page_text = page_text.decode('utf-8')
                page_text = parse_database_text(parse_wikitext_to_clean_text(page_text))

                # Construct the page link
                page_link = f"{base_url}index.php?title={page_title.replace(' ', '_')}"

                # Fetch summary text for the current page_id
                cursor.execute(
                    f"SELECT sum_text FROM summaries WHERE page_id = %s ORDER BY sum_update_time DESC LIMIT 1",
                    (page_id,))
                summary_result = cursor.fetchone()
                sum_text = summary_result[0] if summary_result else ''

                # Insert new entry into pages
                cursor.execute(f"""
                    INSERT INTO {target_table} (id, title, clean_text, sum_text, link)
                    VALUES (%s, %s, %s, %s, %s)
                """, (page_id, page_title, page_text, sum_text, page_link))

            conn.commit()
            print(f"Data copied and converted from {source_table} to {target_table} in {target_db}")
            log_action(user, "copy_n_convert", f"Data copied and sanitized from {source_table} to {target_table}")
        else:
            print(f"No data found in table {source_table}")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)


def random_page_summary_update(user):
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "random_page_summary_update", "Failed to connect to the database")
            return

        cursor = conn.cursor()

        # Fetch one random page from the pages table
        cursor.execute("SELECT id, clean_text FROM pages ORDER BY RAND() LIMIT 1")
        page = cursor.fetchone()
        if not page:
            print("No page found in the pages table.")
            log_action(user, "random_page_summary_update", "No page found in the pages table")
            return

        page_id, clean_text = page

        # Generate summary
        print("Summarization process started...")
        summary = summarize_text(clean_text)
        print("Summarization process ended.")

        # Insert new entry in summaries table
        insert_summary_sql = """
        INSERT INTO summaries (page_id, sum_text, sum_quality, sum_update_time, latest_reviewer, latest_approve_time)
        VALUES (%s, %s, 5, NOW(), %s, NOW())
        """
        cursor.execute(insert_summary_sql, (page_id, summary, user))

        # Update the same entry in the pages table with the summary text
        update_pages_sql = "UPDATE pages SET sum_text = %s WHERE id = %s"
        cursor.execute(update_pages_sql, (summary, page_id))

        conn.commit()

        print(f"Summary for page ID {page_id} has been updated.")
        log_action(user, "random_page_summary_update", f"Summary for page ID {page_id} has been updated")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "random_page_summary_update", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def select_page_summary_update(user):
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "select_page_summary_update", "Failed to connect to the database")
            return

        cursor = conn.cursor()

        while True:
            user_input = input("\nEnter the ID of the page you want to summarize (or type 'back' to return): ")
            if user_input.lower() == 'back':
                print("Going back to the previous menu...")
                break

            try:
                page_id = int(user_input)

                # Check if the page exists in the pages table
                cursor.execute("SELECT clean_text FROM pages WHERE id = %s", (page_id,))
                page = cursor.fetchone()
                if not page:
                    print("Page not found. Please enter a valid page ID.")
                    continue

                clean_text = page[0]

                # Generate summary
                print("Summarization process started...")
                summary = summarize_text(clean_text)
                print("Summarization process ended.")

                # Insert new entry in summaries table
                insert_summary_sql = """
                INSERT INTO summaries (page_id, sum_text, sum_quality, sum_update_time, latest_reviewer, latest_approve_time)
                VALUES (%s, %s, 5, NOW(), %s, NOW())
                """
                cursor.execute(insert_summary_sql, (page_id, summary, user))

                # Update the same entry in the pages table with the summary text
                update_pages_sql = "UPDATE pages SET sum_text = %s WHERE id = %s"
                cursor.execute(update_pages_sql, (summary, page_id))

                conn.commit()

                print(f"Summary for page ID {page_id} has been updated.")
                log_action(user, "select_page_summary_update", f"Summary for page ID {page_id} has been updated")
                break

            except ValueError:
                print("Invalid input. Please enter a valid ID.")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "select_page_summary_update", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def countdown(t):
    """Countdown timer that can be aborted by pressing any key."""
    print("Starting in 5 seconds... Press any key to abort.")
    for i in range(t, 0, -1):
        print(f"Starting in {i} seconds... Press any key to abort.", end='\r')
        time.sleep(1)
        if stop_timer_event.is_set():
            print("Job start aborted.")
            return
    print("Starting summarization job now...", end='\r')


def listen_for_abort():
    """Listen for a key press to abort the timer."""
    input()
    stop_timer_event.set()


def summarize_all_entries(user):
    """Summarize all entries in the pages table and log the process."""
    global stop_timer_event
    stop_timer_event = threading.Event()

# Start the countdown timer and listen for key press
    timer_thread = threading.Thread(target=countdown, args=(5,))
    listener_thread = threading.Thread(target=listen_for_abort)
    timer_thread.start()
    listener_thread.start()

    # Wait for the timer to complete or be aborted
    timer_thread.join()

    if stop_timer_event.is_set():
        return

    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(Fore.RED + f"Failed to connect to the database: {target_db}")
            log_action(user, "summarize_all_entries", "Failed to connect to the database")
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, clean_text FROM pages")
        entries = cursor.fetchall()

        total_entries = len(entries)
        passed_entries = 0
        failed_entries = 0

        for entry in entries:
            page_id = entry['id']
            clean_text = entry['clean_text']
            try:
                summary = summarize_text(clean_text)

                # Insert new entry in summaries table
                insert_summary_sql = """
                INSERT INTO summaries (page_id, sum_text, sum_quality, sum_update_time, latest_reviewer, latest_approve_time)
                VALUES (%s, %s, 5, NOW(), %s, NOW())
                """
                cursor.execute(insert_summary_sql, (page_id, summary, user))

                # Update the same entry in the pages table with the summary text
                update_pages_sql = "UPDATE pages SET sum_text = %s WHERE id = %s"
                cursor.execute(update_pages_sql, (summary, page_id))

                conn.commit()
                print(Fore.GREEN + f"Successfully summarized entry ID: {page_id}")
                passed_entries += 1
            except Exception as e:
                print(Fore.RED + f"Failed to summarize entry ID: {page_id}, Error: {e}")
                failed_entries += 1

            print(Style.BRIGHT + f"Entries left: {total_entries - (passed_entries + failed_entries)}, Passed: {passed_entries}, Failed: {failed_entries}")

        log_message = f"Summarized {passed_entries} entries successfully, {failed_entries} entries failed."
        log_action(user, "summarize_all_entries", log_message)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(os.path.dirname(__file__), f"summarize_all_entries_log_{timestamp}.txt")
        with open(log_file_path, 'w') as log_file:
            log_file.write(log_message)

    except Error as e:
        print(Fore.RED + f"Error: {e}")
        log_action(user, "summarize_all_entries", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)
