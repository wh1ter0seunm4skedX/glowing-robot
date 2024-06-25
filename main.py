from utils.database_utils import check_database_connection
from operations.create_operations import (
    check_and_create_view_in_my_wiki,
    check_and_create_view_in_target_db,
    import_sql_file
)
from operations.read_operations import (
    list_tables,
    fetch_all_page_titles,
    fetch_page_text_by_id,
    check_if_view_exists_in_my_wiki,
    check_if_view_exists_in_target_db,
    export_view_as_sql_file
)
from operations.update_operations import (
    copy_and_convert_data,
    copy_view_to_target_db,
    copy_and_convert_data_to_small_pages
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
from operations.text_processing import parse_database_text

def main():
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
            check_and_create_view_in_my_wiki(user)
        elif choice == '2':
            check_and_create_view_in_target_db(user)
        elif choice == '3':
            sql_file_path = input("Enter the path to the SQL file: ")
            import_sql_file(user, 'target_db', sql_file_path)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

def handle_read_operations(user):
    while True:
        choice = show_read_operations_menu()
        if choice == '1':
            list_tables('target_db')
        elif choice == '2':
            titles = fetch_all_page_titles()
            if titles:
                for i, (page_id, title) in enumerate(titles):
                    print(f"{i + 1}. Page ID: {page_id}, Title: {title}")
        elif choice == '3':
            page_id = input("Enter the page ID to view its text: ")
            try:
                page_id = int(page_id)
                page_text = fetch_page_text_by_id(page_id)
                if page_text:
                    cleaned_text = parse_database_text(page_text)
                    print(f"\nText for Page ID {page_id}:\n{cleaned_text}")
                else:
                    print("No text found for the selected page ID.")
            except ValueError:
                print("Invalid input. Please enter a valid page ID.")
        elif choice == '4':
            check_if_view_exists_in_my_wiki()
        elif choice == '5':
            check_if_view_exists_in_target_db()
        elif choice == '6':
            export_path = input("Enter the path to export the SQL file: ")
            export_view_as_sql_file('latest_text_view', 'my_wiki', export_path)
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")

def handle_update_operations(user):
    while True:
        choice = show_update_operations_menu()
        if choice == '1':
            copy_and_convert_data(user, 'latest_text_view')
        elif choice == '2':
            copy_view_to_target_db(user)
        elif choice == '3':
            copy_and_convert_data_to_small_pages(user)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

def handle_delete_operations(user):
    while True:
        choice = show_delete_operations_menu()
        if choice == '1':
            table_name = input("Enter the table name to remove: ")
            remove_table(user, 'target_db', table_name)
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
