import mysql.connector
from mysql.connector import Error
import time

# Configuration for connecting to the database server
config = {
    'user': 'root',
    'password': 'rootpassword',
    'host': 'localhost',
    'database': 'target_db',  # Dynamically set based on user input
    'raise_on_warnings': False,
    'get_warnings': True,
}


def check_database_connection():
    """Check database connection"""
    print("Checking database connection...")
    time.sleep(0.5)  # Simulate the connection process
    conn = create_connection()
    if conn:
        close_connection(conn)
        print("Database connection successful.")
        return True
    else:
        print("Failed to connect to the database.")
        return False


def create_connection(database=None, allow_local_infile=False):
    """Create a database connection"""
    try:
        conn_config = config.copy()
        if database:
            conn_config['database'] = database
        if allow_local_infile:
            conn_config['allow_local_infile'] = allow_local_infile
        conn = mysql.connector.connect(**conn_config)
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def close_connection(conn):
    """Close the database connection"""
    if conn.is_connected():
        conn.close()


def list_databases():
    """List all databases"""
    try:
        conn = create_connection()
        if not conn:
            print("Failed to connect to the database server")
            return

        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        if databases:
            print("Databases:")
            for db in databases:
                print(db[0])
            return [db[0] for db in databases]
        else:
            print("No databases found")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            close_connection(conn)


def set_target_db(db_name):
    """Set the target database"""
    global config
    config['database'] = db_name


def initialize_db():
    """Initialize the database connection"""
    print(f"Connecting to {config['database']}")
    conn = create_connection()
    if conn:
        close_connection(conn)
        print(f"Connected to {config['database']} successfully.")
    else:
        print(f"Failed to connect to {config['database']}")


# Example function to demonstrate the usage
def get_connection():
    """Get the database connection"""
    print(f"Using database: {config['database']}")
    return create_connection()
