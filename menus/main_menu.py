from menus.ascii_art import intro_ascii


def show_main_menu():
    print(intro_ascii)
    print("1. Create Operations")
    print("2. Read Operations")
    print("3. Update Operations")
    print("4. Delete Operations")
    print("5. Exit")
    choice = input("Enter your choice: ")
    return choice
