from processing import (
    parse_input,
    add_contact,
    change_contact,
    show_phone,
    show_all,
    show_help,
    add_birthday,
    show_birthday,
    birthdays,
    save_data,
    load_data,
)


def main():
    book = load_data()

    print(show_help())

    commands = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
    }

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ("close", "exit", "bye"):
            save_data(book)
            print("Good bye!")
            break

        elif command in ("hello", "hi", "start"):
            print("How can I help you?")

        elif command in commands:
            print(commands[command](args, book))

        else:
            print("Invalid command. Try another command from /help/")


if __name__ == "__main__":
    main()