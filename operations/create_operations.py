from operations.logs import log_action
from utils.database_utils import create_connection, close_connection, config
from mysql.connector import Error


def create_logs_table(user):
    """Create the logs table with the desired structure"""
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "create_logs_table", "Failed to connect to the database")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'logs'")
        result = cursor.fetchone()
        if result:
            print("Table 'logs' already exists.")
            return

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS logs (
            log_id INT(11) NOT NULL AUTO_INCREMENT,
            username VARCHAR(20) NOT NULL,
            operation VARCHAR(255) NOT NULL,
            operation_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            details TEXT NOT NULL,
            PRIMARY KEY (log_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Table logs created successfully in {target_db}")
        log_action(user, "create_logs_table", "Table created successfully")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "create_logs_table", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def create_raw_page_data_table(user):
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "create_raw_page_data_table", "Failed to connect to the database")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'raw_page_data'")
        result = cursor.fetchone()
        if result:
            print("Table 'raw_page_data' already exists.")
            return

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw_page_data (
            latest_page_id INT(11) NOT NULL,
            page_title VARCHAR(255) NOT NULL,
            page_text TEXT NOT NULL,
            export_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            import_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (latest_page_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Table raw_page_data created successfully in {target_db}")
        log_action(user, "create_raw_page_data_table", "Table created successfully")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "create_raw_page_data_table", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def create_summaries_table(user):
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "create_summaries_table", "Failed to connect to the database")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'summaries'")
        result = cursor.fetchone()
        if result:
            print("Table 'summaries' already exists.")
            return

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS summaries (
            sum_id INT(11) NOT NULL AUTO_INCREMENT,
            page_id INT(11) NOT NULL,
            sum_text VARCHAR(255) NOT NULL,
            sum_quality TINYINT NOT NULL,
            sum_update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            latest_reviewer VARCHAR(20) NOT NULL,
            latest_approve_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (sum_id),
            FOREIGN KEY (page_id) REFERENCES raw_page_data(latest_page_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Table summaries created successfully in {target_db}")
        log_action(user, "create_summaries_table", "Table created successfully")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "create_summaries_table", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def create_pages_table(user):
    target_db = config['database']
    try:
        conn = create_connection(target_db)
        if not conn:
            print(f"Failed to connect to the database: {target_db}")
            log_action(user, "create_pages_table", "Failed to connect to the database")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'pages'")
        result = cursor.fetchone()
        if result:
            print("Table 'pages' already exists.")
            return

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS pages (
            id INT(11) NOT NULL,
            title VARCHAR(255) NOT NULL,
            clean_text TEXT NOT NULL,
            sum_text VARCHAR(255) NOT NULL,
            link VARCHAR(255) NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (id) REFERENCES raw_page_data(latest_page_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Table pages created successfully in {target_db}")
        log_action(user, "create_pages_table", "Table created successfully")

    except Error as e:
        print(f"Error: {e}")
        log_action(user, "create_pages_table", f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)

