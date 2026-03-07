from collections import UserDict
from typing import Tuple, List


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.phones.remove(phone_to_edit)
            self.phones.append(Phone(new_phone))
        else:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def __str__(self):
        phones_str = "; ".join(phone.value for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]


def show_help():
    return """
Welcome to the assistant bot!

Commands:
  add <name> <phone>                 Add new contact
  change <name> <old_phone> <new_phone> Change contact phone
  phone <name>                       Show phone number
  all                                Show all contacts
  hello                              Greeting
  exit / close                       Exit the program
"""


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args


def add_contact(args, book: AddressBook) -> str:
    name, phone = args

    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

    record.add_phone(phone)
    return "Phone added."


def change_contact(args, book: AddressBook) -> str:
    name, old_phone, new_phone = args

    record = book.find(name)

    if record is None:
        raise KeyError("Contact not found.")

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


def show_phone(args, book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError("Contact not found.")

    return str(record)


def show_all(book: AddressBook) -> str:
    if not book.data:
        return "No contacts saved."

    items = sorted(book.data.items(), key=lambda x: x[0].lower())
    rows = [(str(i), name, "; ".join(phone.value for phone in record.phones))
            for i, (name, record) in enumerate(items, start=1)]

    headers = ("ID", "Name", "Phones")
    col_widths = [
        max(len(headers[0]), max(len(r[0]) for r in rows)),
        max(len(headers[1]), max(len(r[1]) for r in rows)),
        max(len(headers[2]), max(len(r[2]) for r in rows)),
    ]

    def line(left, fill, sep, right):
        return (
            left
            + fill * (col_widths[0] + 2) + sep
            + fill * (col_widths[1] + 2) + sep
            + fill * (col_widths[2] + 2)
            + right
        )

    def fmt_row(a, b, c):
        return (
            f"│ {a:>{col_widths[0]}} │ "
            f"{b:<{col_widths[1]}} │ "
            f"{c:<{col_widths[2]}} │"
        )

    top = line("┌", "─", "┬", "┐")
    mid = line("├", "─", "┼", "┤")
    bot = line("└", "─", "┴", "┘")

    out = []
    out.append(f"Contacts: {len(rows)}")
    out.append(top)
    out.append(fmt_row(*headers))
    out.append(mid)
    out.extend(fmt_row(*r) for r in rows)
    out.append(bot)

    return "\n".join(out)