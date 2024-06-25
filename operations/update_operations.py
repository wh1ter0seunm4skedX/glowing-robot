from operations.create_operations import create_all_pages_table
from operations.logs import log_action
from operations.read_operations import get_mediawiki_base_url
from operations.text_processing import parse_database_text, parse_wikitext_to_clean_text, extract_text_between_big_tags
from utils.database_utils import create_connection, close_connection
from mysql.connector import Error

def copy_view_to_target_db(user, source_db='my_wiki', target_db='target_db'):
    """Copy the latest_text_view view from my_wiki to target_db and overwrite the table."""
    try:
        # Connect to the source database to fetch data
        source_conn = create_connection(source_db)
        if source_conn is None:
            print(f"Failed to connect to the database: {source_db}")
            return

        # Fetch the latest data from the source view
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT * FROM latest_text_view")
        view_data = source_cursor.fetchall()

        # Connect to the target database to insert data
        target_conn = create_connection(target_db)
        if target_conn is None:
            print(f"Failed to connect to the database: {target_db}")
            return

        target_cursor = target_conn.cursor()

        # Check if the temporary table exists
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'latest_text_temp'
        """, (target_db,))
        table_exists = target_cursor.fetchone()[0]

        if table_exists:
            # Clear the table before inserting new data
            target_cursor.execute("TRUNCATE TABLE latest_text_temp")
            log_action(user, "overwrite_table", "latest_text_temp table truncated in target_db")
        else:
            # Create the temporary table if it doesn't exist
            target_cursor.execute("""
                CREATE TABLE latest_text_temp (
                    page_id INT,
                    page_title VARCHAR(255),
                    old_text MEDIUMBLOB
                )
            """)
            log_action(user, "create_table", "latest_text_temp table created in target_db")

        # Insert the fetched data into the temporary table
        insert_sql = "INSERT INTO latest_text_temp (page_id, page_title, old_text) VALUES (%s, %s, %s)"
        target_cursor.executemany(insert_sql, view_data)
        target_conn.commit()

        print("Table 'latest_text_temp' populated in target_db successfully.")
        log_action(user, "populate_table", "latest_text_temp table populated with data from latest_text_view in my_wiki")

    except Error as e:
        print(f"Error copying view to target_db: {e}")
        log_action(user, "error", f"Error copying view to target_db: {e}")
    finally:
        if source_conn:
            close_connection(source_conn)
        if target_conn:
            close_connection(target_conn)


def copy_and_convert_data(user, view_name, table_name='all_pages'):
    """Copy data from a view to a table and convert mediumblob to text"""
    try:
        conn = create_connection('target_db')
        if not conn:
            print(f"Failed to connect to the database: target_db")
            return

        cursor = conn.cursor()

        # Ensure the table exists
        create_all_pages_table()

        # Fetch data from the view
        cursor.execute(f"SELECT page_id, page_title, old_text FROM {view_name}")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                page_id, page_title, old_text = row
                if isinstance(page_title, bytearray):
                    page_title = bytes(page_title).decode('utf-8')
                elif isinstance(page_title, bytes):
                    page_title = page_title.decode('utf-8')

                # Convert underscores to spaces in page_title
                page_title = page_title.replace('_', ' ')

                if isinstance(old_text, bytearray):
                    old_text = bytes(old_text).decode('utf-8')
                elif isinstance(old_text, bytes):
                    old_text = old_text.decode('utf-8')

                # Process the text
                page_text = parse_database_text(parse_wikitext_to_clean_text(old_text))

                # Check if the page_id already exists
                cursor.execute("SELECT page_id FROM all_pages WHERE page_id = %s", (page_id,))
                if cursor.fetchone():
                    # Update existing entry
                    cursor.execute("""
                        UPDATE all_pages
                        SET page_title = %s, page_text = %s
                        WHERE page_id = %s
                    """, (page_title, page_text, page_id))
                else:
                    # Insert new entry
                    cursor.execute("""
                        INSERT INTO all_pages (page_id, page_title, page_text)
                        VALUES (%s, %s, %s)
                    """, (page_id, page_title, page_text))

            conn.commit()
            print(f"Data copied and converted from {view_name} to {table_name} in target_db")
            log_action(user, "copy_and_convert", f"Data copied and converted from {view_name} to {table_name}")
        else:
            print(f"No data found in view {view_name}")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)


def copy_and_convert_data_to_small_pages(user, source_table='latest_text_temp', target_table='small_pages'):
    """Copy data from latest_text_temp to small_pages and convert mediumblob to text"""
    try:
        conn = create_connection('target_db')
        if not conn:
            print(f"Failed to connect to the database: target_db")
            return

        cursor = conn.cursor()

        # Ensure the small_pages table exists
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {target_table} (
                page_id INT(10) PRIMARY KEY,
                page_title VARCHAR(255),
                page_text TEXT,
                page_link VARCHAR(255)
            )
        """)

        # Fetch data from the source table
        cursor.execute(f"SELECT page_id, page_title, old_text FROM {source_table}")
        rows = cursor.fetchall()

        base_url = get_mediawiki_base_url()

        if rows:
            for row in rows:
                page_id, page_title, old_text = row

                if isinstance(page_title, bytearray):
                    page_title = bytes(page_title).decode('utf-8')
                elif isinstance(page_title, bytes):
                    page_title = page_title.decode('utf-8')

                # Convert underscores to spaces in page_title
                page_title = page_title.replace('_', ' ')

                if isinstance(old_text, bytearray):
                    old_text = bytes(old_text).decode('utf-8')
                elif isinstance(old_text, bytes):
                    old_text = old_text.decode('utf-8')

                # Extract text between the first pair of <big> and </big> tags
                page_text = extract_text_between_big_tags(old_text)

                # Process the text
                page_text = parse_database_text(parse_wikitext_to_clean_text(page_text))

                # Construct the page link
                page_link = f"{base_url}index.php?title={page_title.replace(' ', '_')}"

                # Insert or update the entry in small_pages
                cursor.execute(f"SELECT page_id FROM {target_table} WHERE page_id = %s", (page_id,))
                if cursor.fetchone():
                    # Update existing entry
                    cursor.execute(f"""
                        UPDATE {target_table}
                        SET page_title = %s, page_text = %s, page_link = %s
                        WHERE page_id = %s
                    """, (page_title, page_text, page_link, page_id))
                else:
                    # Insert new entry
                    cursor.execute(f"""
                        INSERT INTO {target_table} (page_id, page_title, page_text, page_link)
                        VALUES (%s, %s, %s, %s)
                    """, (page_id, page_title, page_text, page_link))

            conn.commit()
            print(f"Data copied and converted from {source_table} to {target_table} in target_db")
            log_action(user, "copy_and_convert", f"Data copied and converted from {source_table} to {target_table}")
        else:
            print(f"No data found in table {source_table}")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "error", str(e))
    finally:
        if conn:
            close_connection(conn)


