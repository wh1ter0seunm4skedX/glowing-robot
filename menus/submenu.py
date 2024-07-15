from menus.ascii_art import create_ascii, read_ascii, update_ascii, delete_ascii
from utils.database_utils import config
from colorama import init, Fore, Back, Style


def show_create_operations_menu():
    print(create_ascii)
    print("1. Create 'logs' table")
    print("2. Create 'raw_page_data' table")
    print("3. Create 'summaries' table")
    print("4. Create 'pages' table")
    print("5. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice


def show_read_operations_menu():
    print(read_ascii)
    print("1. List all page titles")
    print("2. Make real-time summary of specific page")
    print("3. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice


def show_update_operations_menu():
    current_db = config['database']
    init()
    print(update_ascii)
    print("1. Copy and convert data from 'raw_page_data' to 'pages'")
    print(f"2. Import data from CSV file into 'raw_page_data'")
    print("3. Update a random page summary")
    print("4. Make a summary of specific page by ID")
    print(Fore.YELLOW + "5. Make a summary of all the pages" + Style.RESET_ALL)
    print("6. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice


def show_delete_operations_menu():
    current_db = config['database']
    print(delete_ascii)
    print(f"1. Remove a table from {current_db} database")
    print("2. Back to Main Menu")
    choice = input("Enter your choice: ")
    print("")
    return choice
