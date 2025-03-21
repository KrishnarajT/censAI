def menu_system(menu, level=0):
    while True:
        print("\n" + "  " * level + "Select an option:")
        options = list(menu.keys()) + ["Back"] if level > 0 else list(menu.keys())

        for i, option in enumerate(options, 1):
            print(f"{'  ' * level}{i}. {option}")

        choice = input("Enter choice: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            choice = int(choice) - 1
            selected_option = options[choice]

            if selected_option == "Back":
                return  # Go back to the previous level

            if isinstance(menu[selected_option], dict):
                menu_system(menu[selected_option], level + 1)  # Recursively go deeper
            else:
                print(f"\n{'  ' * level}→ You selected: {selected_option}\n")
        else:
            print("Invalid choice. Try again.")


# Define the menu structure using a nested dictionary
menu_tree = {
    "Option 1": {
        "Sub-option 1.1": {"Sub-sub-option 1.1.1": {}, "Sub-sub-option 1.1.2": {}},
        "Sub-option 1.2": {},
    },
    "Option 2": {
        "Sub-option 2.1": {"Sub-sub-option 2.1.1": {}, "Sub-sub-option 2.1.2": {}}
    },
    "Option 3": {},
}

if __name__ == "__main__":
    print("Welcome to CensAI!")
    print(
        """

    ░▒▓██████▓▒░░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░░▒▓██████▓▒░░▒▓█▓▒░ 
    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░      ░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 
    ░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ 

    Censorship Model for TV shows and Movies


    """
    )
    menu_system(menu_tree)
