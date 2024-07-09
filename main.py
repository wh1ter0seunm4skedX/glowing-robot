import sys
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from utils.database_utils import check_database_connection, set_target_db, initialize_db, config
from operations.create_operations import (
    create_summaries_table,
    create_raw_page_data_table,
    create_logs_table,
    create_pages_table
)
from operations.read_operations import (
    fetch_page_titles, select_page_and_summarize
)
from operations.update_operations import (
    copy_n_convert, import_csv_to_raw_page_data
)
from operations.delete_operations import (
    remove_table
)
from menus.main_menu import show_main_menu
from menus.submenu import (
    show_create_operations_menu,
    show_read_operations_menu,
    show_update_operations_menu,
    show_delete_operations_menu
)


def choose_environment():
    print("Choose the environment you want to work on:")
    print("1. Development 🔧")
    print("2. Production 🧨")

    choice = input("Enter the number of your choice (1 or 2): ").strip()

    if choice == '1':
        set_target_db('dev_db')
    elif choice == '2':
        set_target_db('prod_db')
    else:
        print("Invalid choice. Please enter 1 or 2.")
        sys.exit(1)


def main():
    choose_environment()
    initialize_db()
    if not check_database_connection():
        print("Database connection failed. Please check your settings and try again.")
        return

    user = input("\nEnter your username: ")

    while True:
        choice = show_main_menu()
        if choice == '1':
            handle_create_operations(user)
        elif choice == '2':
            handle_read_operations(user)
        elif choice == '3':
            handle_update_operations(user)
        elif choice == '4':
            handle_delete_operations(user)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


def handle_create_operations(user):
    while True:
        choice = show_create_operations_menu()
        if choice == '1':
            create_logs_table(user)
        elif choice == '2':
            create_raw_page_data_table(user)
        elif choice == '3':
            create_summaries_table(user)
        elif choice == '4':
            create_pages_table(user)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")


def handle_read_operations(user):
    while True:
        choice = show_read_operations_menu()
        if choice == '1':
            titles = fetch_page_titles()
            if titles:
                for i, (page_id, title) in enumerate(titles):
                    print(f"{i + 1}. Page ID: {page_id}, Title: {title}")
        elif choice == '2':
            select_page_and_summarize()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")


def handle_update_operations(user):
    while True:
        choice = show_update_operations_menu()
        if choice == '1':
            copy_n_convert(user, 'raw_page_data', 'pages')
        elif choice == '2':
            file_path = input("Enter the path to the CSV file: ")
            import_csv_to_raw_page_data(user, file_path)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")


def handle_delete_operations(user):
    while True:
        choice = show_delete_operations_menu()
        if choice == '1':
            table_name = input("Enter the table name to remove: ")
            remove_table(user, config['database'], table_name)
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
