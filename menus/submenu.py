from utils.database_utils import config


def show_create_operations_menu():
    current_db = config['database']
    print("\nCreate Operations Menu")
    print("1. Create 'latest_text_view' in my_wiki")
    print(f"2. Create 'latest_text_view' in {current_db}")
    print("3. Import an SQL file into a database")
    print("4. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice


def show_read_operations_menu():
    current_db = config['database']
    print("\nRead Operations Menu")
    print(f"1. List tables in {current_db}")
    print("2. Fetch all page titles from 'all_pages'")
    # print("3. Fetch page text by ID")
    print("4. Check if 'latest_text_view' exists in my_wiki")
    print(f"5. Check if 'latest_text_view' exists in {current_db}")
    # print("6. Export 'latest_text_view' as SQL file if exists in my_wiki")
    print("6. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice


def show_update_operations_menu():
    current_db = config['database']
    print("\nUpdate Operations Menu")
    print("1. Copy and convert data from 'latest_text_view' to 'all_pages'")
    # print(f"2. Copy 'latest_text_view' from my_wiki to {current_db}")
    print("3. Copy and convert data from 'latest_text_temp' to 'small_pages'")
    print(f"4. Copy and overwrite tables from source database to {current_db}")
    print("5. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice


def show_delete_operations_menu():
    current_db = config['database']
    print("\nDelete Operations Menu")
    print(f"1. Remove a table from {current_db} database")
    print("2. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice
