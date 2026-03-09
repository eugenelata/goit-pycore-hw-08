from collections import UserDict
from datetime import datetime, date, timedelta
import pickle


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


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove is None:
            raise ValueError("Phone number not found.")
        self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit is None:
            raise ValueError("Phone number not found.")
        self.phones.remove(phone_to_edit)
        self.phones.append(Phone(new_phone))

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(phone.value for phone in self.phones)
        birthday_str = self.birthday.value if self.birthday else "not set"
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones_str}, "
            f"birthday: {birthday_str}"
        )


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        name = name.lower()
        if name not in self.data:
            raise KeyError("Contact not found.")
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_date = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()

            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_diff = (birthday_this_year - today).days

            if 0 <= days_diff <= 7:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                    }
                )

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return str(error)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the argument for the command."
    return inner


def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    cmd = cmd.lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError

    if not record.phones:
        return "No phones found."

    return "; ".join(phone.value for phone in record.phones)


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts saved."

    items = sorted(book.data.items(), key=lambda x: x[0].lower())
    rows = []

    for i, (name, record) in enumerate(items, start=1):
        phones = "; ".join(phone.value for phone in record.phones)
        birthday = record.birthday.value if record.birthday else "not set"
        rows.append((str(i), name, phones, birthday))

    headers = ("ID", "Name", "Phones", "Birthday")
    col_widths = [
        max(len(headers[0]), max(len(r[0]) for r in rows)),
        max(len(headers[1]), max(len(r[1]) for r in rows)),
        max(len(headers[2]), max(len(r[2]) for r in rows)),
        max(len(headers[3]), max(len(r[3]) for r in rows)),
    ]

    def line(left, fill, sep, right):
        return (
            left
            + fill * (col_widths[0] + 2) + sep
            + fill * (col_widths[1] + 2) + sep
            + fill * (col_widths[2] + 2) + sep
            + fill * (col_widths[3] + 2)
            + right
        )

    def fmt_row(a, b, c, d):
        return (
            f"│ {a:>{col_widths[0]}} │ "
            f"{b:<{col_widths[1]}} │ "
            f"{c:<{col_widths[2]}} │ "
            f"{d:<{col_widths[3]}} │"
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


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError

    if record.birthday is None:
        return "Birthday not set."

    return record.birthday.value


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()

    if not upcoming_birthdays:
        return "No upcoming birthdays."

    lines = []
    for item in upcoming_birthdays:
        lines.append(f"{item['name']}: {item['congratulation_date']}")

    return "\n".join(lines)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()

def show_help():
    return """
Welcome to the assistant bot!

Commands:
  add <name> <phone>                         Add new contact
  change <name> <old_phone> <new_phone>     Change contact phone
  phone <name>                              Show phones for contact
  all                                       Show all contacts
  add-birthday <name> <DD.MM.YYYY>          Add birthday for contact
  show-birthday <name>                      Show birthday for contact
  birthdays                                 Show upcoming birthdays
  hello                                     Greeting
  exit / close                              Exit the program
"""