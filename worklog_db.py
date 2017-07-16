#####################################################
# Work Log with Database
# Author: Jay Li
#####################################################
##########################################################
# Specs: Part 1
##########################################################
# As a user of the script, I should be able to choose whether to add a new entry or lookup previous entries.
# As a user of the script, if I choose to enter a new work log, I should be able to provide my name, a task name, a number of minutes spent working on it, and any additional notes I want to record.
# As a user of the script, if I choose to find a previous entry, I should be presented with four options: find by employee, find by date, find by time spent, find by search term.
# As a user of the script, if finding by employee, I should be presented with a list of employees with entries and be able to choose one to see entries from.
# As a user of the script, if finding by date, I should be presented with a list of dates with entries and be able to choose one to see entries from.
# As a user of the script, if finding by time spent, I should be allowed to enter the amount of time spent on the project and then be presented with entries containing that amount of time spent.
# As a user of the script, if finding by a search term, I should be allowed to enter a string and then be presented with entries containing that string in the task name or notes.
# As a user of the script, if finding by employee, I should be allowed to enter employee name and then be presented with entries with that employee as their creator.
# As a fellow developer, I should find at least 50% of the code covered by tests. I would use coverage.py to validate this amount of coverage.
##########################################################
# Specs: Part 2
##########################################################
# Menu has a “quit” option to exit the program.
# Records can be deleted and edited, letting user change the date, task name, time spent, and/or notes.
# Can find entries based on a ranges of dates. For example between 01/01/2016 and 12/31/2016.
# If multiple employees share a name (e.g. multiple people with the first name Beth), a list of possible matches is given.
# Records are displayed one at a time with the ability to page through records (previous/next/back).
# As a fellow developer of the script, I should see test coverage of 85% of the code or better.
import os
from collections import OrderedDict
import sys
import datetime

from entry import db, Entry


##########################################################
# Utilities
##########################################################
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def initialize():
    db.connect()
    db.create_tables([Entry], safe=True)
    # test_name = 'John Lennon'
    # test_task = 'Write a new song'
    # test_spent_minutes = 10
    # test_notes = 'Wonderful time'
    # Entry.create(name=test_name, task=test_task,
    #              spent_minutes=test_spent_minutes, notes=test_notes)


########################################################
# Input functions
########################################################
def get_name():
    while True:
        name = input("Enter name: ").strip()
        if not name.isspace():
            return name


def get_task():
    while True:
        task = input("Enter task name: ").strip()
        if not task.isspace():
            return task


def get_spent_minutes_string():
    return input("Enter time spent in (rounded) minutes: ").strip()


def get_spent_minutes():
    while True:
        try:
            spent_minutes = get_spent_minutes_string()
            spent_minutes = int(spent_minutes)
            assert spent_minutes >= 0
        except ValueError:
            print("Invalid minutes entered. Please enter again")
        except AssertionError:
            print("Minutes cannot be negative. Please enter again")
        else:
            return spent_minutes


def get_notes():
    print("Enter additional notes (Optional):")
    print("Enter ctrl+d to finish")
    return sys.stdin.read().strip()


def get_input():
    return input("> ").strip()


def enter_any_key():
    return input("Enter any key to go back")
########################################################
# End: Input functions
########################################################

########################################################
# Utility functions
########################################################
def add_entry():
    """Add an entry"""
    clear_screen()
    print("Add a new entry")
    name = get_name()
    task = get_task()
    spent_minutes = get_spent_minutes()
    notes = get_notes()
    Entry.create(name=name, task=task, spent_minutes=spent_minutes,
                 notes=notes)


def get_browse_input():
    print()
    print("[N]ext (Default), [P]revious, [E]dit, [D]elete, [B]ack")
    return get_input().lower()


def print_entry(entry):
    timestamp = entry.timestamp.strftime('%m/%d/%Y')
    print(timestamp)
    print("=" * len(timestamp))
    print("name: {}".format(entry.name))
    print("task: {}".format(entry.task))
    print("minutes spent: {}".format(entry.spent_minutes))
    print("notes: {}".format(entry.notes))
########################################################
# End: Utility functions
########################################################


def edit_name(entry):
    """Edit employee name"""
    entry.name = get_name()


def edit_task(entry):
    """Edit task title"""
    entry.task = get_task()


def edit_spent_minutes(entry):
    """Edit minutes spent"""
    entry.spent_minutes = get_spent_minutes()


def edit_notes(entry):
    """Edit notes"""
    entry.notes = get_notes()


def edit_entry(entry):
    entry_attributes = OrderedDict([
        ('a', edit_name),
        ('b', edit_task),
        ('c', edit_spent_minutes),
        ('d', edit_notes)
    ])
    clear_screen()
    print("Edit which attribute:")
    for key, val in entry_attributes.items():
        print("{}) {}".format(key, val.__doc__))
    print("Enter q to quit (Default)")
    chosen = get_input().lower()
    if chosen in entry_attributes:
        entry_attributes[chosen](entry)
        entry.save()
        return True
    else:
        return False


def browse_through(matched_entries):
    if matched_entries:
        index = 0
        while index < len(matched_entries):
            entry = matched_entries[index]
            clear_screen()
            print_entry(entry)
            browse_option = get_browse_input()
            if browse_option == 'p':
                if index > 0:
                    index -= 1
            elif browse_option == 'd':
                entry.delete_instance()
                break
            elif browse_option == 'e':
                edited = edit_entry(entry)
                if edited:
                    break
            elif browse_option == 'b':
                break
            else:
                index +=1
    else:
        print("No entries matched")
        enter_any_key()


def find_by_employee():
    """Find by employee name"""
    clear_screen()
    print("Employees to choose from:")
    entries = Entry.select()
    names = set([entry.name for entry in entries])
    for name in sorted(names):
        print(name)
    print("Enter an employee name")
    print("Enter q to go back (Default)")
    name = get_input()
    if name == 'q':
        return None
    matched_entries = entries.where(Entry.name.contains(name))
    unique_names = set([entry.name for entry in matched_entries])
    if len(unique_names) > 1:
        print("Multiple matched names:")
        for name in unique_names:
            print(name)
        print('Enter a name')
        name = get_input()
        matched_entries = entries.where(Entry.name == name)
    browse_through(matched_entries)
    return matched_entries


def get_date():
    while True:
        date = get_input()
        if date.lower() == 'q':
            return None
        try:
            date = datetime.datetime.strptime(date, '%m/%d/%Y').date()
            return date
        except ValueError:
            print("Invalid date. Please enter again.")


def find_by_date():
    """Find by date of entry"""
    entries = Entry.select()
    dates = set([entry.timestamp for entry in entries])
    clear_screen()
    print("Dates to choose from:")
    for date in dates:
        print(date.strftime('%m/%d/%Y'))
    print("Enter a date (MM/DD/YYYY)")
    print("Enter q to go back")
    date = get_date()
    if date is None:
        return
    matched_entries = entries.where(
        Entry.timestamp.year == date.year,
        Entry.timestamp.month == date.month,
        Entry.timestamp.day == date.day
    )
    browse_through(matched_entries)
    return matched_entries


def find_by_date_range():
    """Find by date range"""
    entries = Entry.select()
    dates = set([entry.timestamp for entry in entries])
    clear_screen()
    print("Dates to choose from:")
    for date in dates:
        print(date.strftime('%m/%d/%Y'))
    print("Enter a start date (MM/DD/YYYY)")
    print("Enter q to go back to main menu")
    start_date = get_date()
    if start_date is None:
        return
    print("Enter an end date (MM/DD/YYYY)")
    print("Enter q to go back to main menu")
    end_date = get_date()
    if end_date is None:
        return
    end_date += datetime.timedelta(days=1)
    matched_entries = entries.where(Entry.timestamp.between(start_date,
                                                            end_date))
    browse_through(matched_entries)
    return matched_entries


def find_by_spent_minutes():
    """Find by time spent on task"""
    clear_screen()
    print("Enter time spent in minutes")
    print("Enter q to go back")
    while True:
        spent_minutes = get_input()
        if spent_minutes == 'q':
            return None
        try:
            spent_minutes = int(spent_minutes)
            assert spent_minutes >= 0
        except ValueError:
            print("Invalid minutes. Please enter again.")
        except AssertionError:
            print("Spent minutes must be positive. Please enter again.")
        else:
            matched_entries = Entry.select().where(Entry.spent_minutes ==
                                                   int(spent_minutes))
            browse_through(matched_entries)
            return matched_entries


def find_by_search_term():
    """Find by a search term"""
    clear_screen()
    print("Enter search term")
    while True:
        search_term = get_input()
        matched_entries = Entry.select().where(Entry.task.contains(
            search_term) | Entry.notes.contains(search_term))
        browse_through(matched_entries)
        return matched_entries


def lookup_entries():
    "Look up previous entries"
    lookup_options = OrderedDict([
        ('a', find_by_employee),
        ('b', find_by_date),
        ('c', find_by_date_range),
        ('d', find_by_spent_minutes),
        ('e', find_by_search_term)
    ])
    while True:
        clear_screen()
        print("Search Options:")
        for key, option in lookup_options.items():
            print('{}) {}'.format(key, option.__doc__))
        print("Enter q to go back (Default)")
        chosen = get_input().lower()
        if chosen in lookup_options:
            lookup_options[chosen]()
        else:
            break


# def foo():
#     print("Yo")


def main():
    initialize()
    actions = OrderedDict([
        ('a', add_entry),
        ('b', lookup_entries)
    ])
    while True:
        clear_screen()
        print("WORK LOG\n"
              "Which action do you want to take?")
        for key, action in actions.items():
            print("{}) {}".format(key, action.__doc__))
        print("Enter q to quit (Default)")
        chosen = get_input().lower()
        if chosen in actions:
            actions[chosen]()
        else:
            break

if __name__ == '__main__':
    main()
