#####################################################
# Unit Tests for Work Log program
# Author: Jay Li
#####################################################
import unittest
from io import StringIO
from unittest import mock
import random, string
import datetime

from entry import Entry
from peewee import *
import worklog_db


test_db = SqliteDatabase('test.db')
test_name = 'John Lennon'
test_task = 'Write a new song'
test_spent_minutes = 10
test_notes = 'Wonderful time'


#####################################################
# Helper Functions
#####################################################
def random_sentence(lower, upper):
    length = random.randint(lower, upper)
    return ''.join(random.choice(string.printable) for _ in range(length))


def add_entry():
    Entry.create(name=test_name, task=test_task,
                 spent_minutes=test_spent_minutes, notes=test_notes)


def create_random_entry():
    return {
        'name': random_sentence(1, 255),
        'task': random_sentence(1, 255),
        'spent_minutes': random.randint(1, 100),
        'notes': random_sentence(0, 1000)
    }


def create_random_date():
    year = random.randint(1950, 2017)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)


def add_random_entry():
    entry = create_random_entry()
    return Entry.create(name=entry['name'], task=entry['task'],
                 spent_minutes=entry['spent_minutes'],
                 notes=entry['notes'])


class WorklogTest(unittest.TestCase):
    def setUp(self):
        test_db.create_tables([Entry], safe=True)
        Entry._meta.database = test_db
        entries = Entry.select()
        for entry in entries:
            entry.delete_instance()

    @mock.patch('worklog_db.get_name', autospec=True)
    @mock.patch('worklog_db.get_task', autospec=True)
    @mock.patch('worklog_db.get_spent_minutes', autospec=True)
    @mock.patch('worklog_db.get_notes', autospec=True)
    def test_add_single_entry(self, mock_get_notes, mock_get_spent_minutes,
                       mock_get_task, mock_get_name):
        fake_entry = create_random_entry()
        mock_get_name.return_value = fake_entry['name']
        mock_get_task.return_value = fake_entry['task']
        mock_get_spent_minutes.return_value = fake_entry['spent_minutes']
        mock_get_notes.return_value = fake_entry['notes']
        worklog_db.add_entry()
        entries = Entry.select()
        self.assertEqual(len(entries), 1)
        entry = entries.get()
        self.assertEqual(entry.name, fake_entry['name'])
        self.assertEqual(entry.task, fake_entry['task'])
        self.assertEqual(entry.spent_minutes, int(fake_entry['spent_minutes']))
        self.assertEqual(entry.notes, fake_entry['notes'])

    @mock.patch('worklog_db.get_name', autospec=True)
    @mock.patch('worklog_db.get_task', autospec=True)
    @mock.patch('worklog_db.get_spent_minutes', autospec=True)
    @mock.patch('worklog_db.get_notes', autospec=True)
    def test_add_multiple_entries(self, mock_get_notes,
                                     mock_get_spent_minutes, mock_get_task,
                                     mock_get_name):
        iter_num = 10
        fake_entries = [create_random_entry() for _ in range(iter_num)]
        for i in range(iter_num):
            mock_get_name.return_value = fake_entries[i]['name']
            mock_get_task.return_value = fake_entries[i]['task']
            mock_get_spent_minutes.return_value = str(fake_entries[i][
                                                          'spent_minutes'])
            mock_get_notes.return_value = fake_entries[i]['notes']
            worklog_db.add_entry()
        entries = Entry.select()
        self.assertEqual(len(entries), iter_num)
        for fake_entry in fake_entries:
            entry = entries.where(
                Entry.name == fake_entry['name'],
                Entry.task == fake_entry['task'],
                Entry.spent_minutes == fake_entry['spent_minutes'],
                Entry.notes == fake_entry['notes']
            )
            self.assertTrue(entry.exists())

    @mock.patch('worklog_db.get_browse_input', return_value='')
    @mock.patch('worklog_db.get_input', autospec=True)
    def test_find_by_employee(self, mock_get_employee_name, _):
        iter_num = 5
        entries = [create_random_entry() for _ in range(iter_num)]
        for (index, entry) in enumerate(entries, start=1):
            for _ in range(index):
                Entry.create(name=entry['name'], task=entry['task'],
                             spent_minutes=entry['spent_minutes'],
                             notes=entry['notes'])

        for (index, entry) in enumerate(entries, start=1):
            mock_get_employee_name.return_value = entry['name']
            matched_entries = worklog_db.find_by_employee()
            self.assertGreaterEqual(len(matched_entries), index)
            for matched_entry in matched_entries:
                self.assertEqual(matched_entry.name, entry['name'])

    @mock.patch('worklog_db.get_browse_input', return_value='')
    @mock.patch('worklog_db.get_input', autospec=True)
    def test_find_by_spent_minutes(self, mock_get_spent_minutes, _):
        iter_num = 5
        entries = [create_random_entry() for _ in range(iter_num)]
        for (index, entry) in enumerate(entries, start=1):
            for _ in range(index):
                Entry.create(name=entry['name'], task=entry['task'],
                             spent_minutes=entry['spent_minutes'],
                             notes=entry['notes'])

        for (index, entry) in enumerate(entries, start=1):
            mock_get_spent_minutes.return_value = str(entry['spent_minutes'])
            matched_entries = worklog_db.find_by_spent_minutes()
            self.assertGreaterEqual(len(matched_entries), index)
            for matched_entry in matched_entries:
                self.assertEqual(matched_entry.spent_minutes, entry[
                    'spent_minutes'])

    @mock.patch('worklog_db.get_browse_input', return_value='')
    @mock.patch('worklog_db.get_input', autospec=True)
    def test_find_by_search_term(self, mock_get_search_term, _):
        iter_num = 5
        entries = [create_random_entry() for _ in range(iter_num)]
        for (index, entry) in enumerate(entries, start=1):
            for _ in range(index):
                Entry.create(name=entry['name'], task=entry['task'],
                             spent_minutes=entry['spent_minutes'],
                             notes=entry['notes'])

        for (index, entry) in enumerate(entries, start=1):
            search_term = random.choice([entry['task'], entry[
                'notes']]).lower()
            length = len(search_term)
            start = random.randint(0, length-1)
            end = random.randint(start+1, length)
            substring = search_term[start:end]
            mock_get_search_term.return_value = substring
            matched_entries = worklog_db.find_by_search_term()
            self.assertGreaterEqual(len(matched_entries), index)
            for matched_entry in matched_entries:
                self.assertTrue(
                    (substring in matched_entry.task.lower())
                    or
                    (substring in matched_entry.notes.lower())
                    , "{} not in {} or {}".format(substring,
                                                matched_entry.task,
                                                matched_entry.notes))

    @mock.patch('worklog_db.get_browse_input', return_value='')
    @mock.patch('worklog_db.get_input')
    def test_find_by_date(self, mock_get_date_string, _):
        iter_num = 5
        random_dates = [create_random_date() for _ in range(iter_num)]
        for (index, date) in enumerate(random_dates, start=1):
            for _ in range(index):
                entry = create_random_entry()
                Entry.create(name=entry['name'], task=entry['task'],
                             spent_minutes=entry['spent_minutes'],
                             notes=entry['notes'], timestamp=date)
        for (index, date) in enumerate(random_dates, start=1):
            mock_get_date_string.return_value = date.strftime('%m/%d/%Y')
            matched_entries = worklog_db.find_by_date()
            self.assertGreaterEqual(len(matched_entries), index)
            for matched_entry in matched_entries:
                self.assertEqual(matched_entry.timestamp.day, date.day)
                self.assertEqual(matched_entry.timestamp.month, date.month)
                self.assertEqual(matched_entry.timestamp.year, date.year)

    @mock.patch('worklog_db.enter_any_key', return_value='')
    @mock.patch('worklog_db.get_browse_input', return_value='')
    @mock.patch('worklog_db.get_input')
    def test_find_by_date_range(self, mock_get_date_string, _, ignore):
        iter_num = 20
        random_dates = [create_random_date() for _ in range(iter_num)]
        for date in random_dates:
            entry = create_random_entry()
            Entry.create(name=entry['name'], task=entry['task'],
                         spent_minutes=entry['spent_minutes'],
                         notes=entry['notes'], timestamp=date)
        for _ in range(iter_num):
            start_date = create_random_date()
            end_date = create_random_date()
            mock_get_date_string.side_effect = [start_date.strftime('%m/%d/%Y')
                                                ,
                                                end_date.strftime('%m/%d/%Y')]
            matched_entries = worklog_db.find_by_date_range()
            for matched_entry in matched_entries:
                self.assertGreaterEqual(matched_entry.timestamp, start_date)
                self.assertLessEqual(matched_entry.timestamp, end_date)

    def test_creation(self):
        Entry.create(name='Josh', task='Fix bug', spent_minutes=20,
                     notes='fun')
        entries = Entry.select()
        self.assertEqual(len(entries), 1)
        entry = entries.get()
        self.assertEqual(entry.name, 'Josh')
        self.assertEqual(entry.task, 'Fix bug')
        self.assertEqual(entry.spent_minutes, 20)
        self.assertEqual(entry.notes, 'fun')

    @mock.patch('worklog_db.find_by_search_term')
    @mock.patch('worklog_db.find_by_spent_minutes')
    @mock.patch('worklog_db.find_by_date_range')
    @mock.patch('worklog_db.find_by_date')
    @mock.patch('worklog_db.find_by_employee')
    @mock.patch('worklog_db.get_input', side_effect=['a', 'b', 'd', 'c',
                                                     'd', 'e', 'q'])
    def test_lookup_entries(self, mock_get_input, mock_a, mock_b, mock_c,
                            mock_d, mock_e):
        worklog_db.lookup_entries()
        mock_a.assert_called_once_with()
        mock_b.assert_called_once_with()
        mock_c.assert_called_once_with()
        self.assertTrue(mock_d.call_count == 2)
        mock_e.assert_called_once_with()

    @mock.patch('worklog_db.edit_notes')
    @mock.patch('worklog_db.edit_spent_minutes')
    @mock.patch('worklog_db.edit_task')
    @mock.patch('worklog_db.edit_name')
    @mock.patch('worklog_db.get_input', side_effect=['a', 'b', 'c', 'd'])
    def test_edit_entry(self, mock_get_input, mock_a, mock_b, mock_c, mock_d):
        entry = add_random_entry()
        worklog_db.edit_entry(entry)
        mock_a.assert_called_once_with(entry)
        worklog_db.edit_entry(entry)
        mock_b.assert_called_once_with(entry)
        worklog_db.edit_entry(entry)
        mock_c.assert_called_once_with(entry)
        worklog_db.edit_entry(entry)
        mock_d.assert_called_once_with(entry)

    # @mock.patch('sys.stdout', new_callable=StringIO)
    # def test_foo(self, mock_stdout):
    #     worklog_db.foo()
    #     self.assertEqual(mock_stdout.getvalue(), "Yo\n")

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch("worklog_db.get_spent_minutes_string")
    def test_get_spent_minutes(self, mock_spent_minutes_string, mock_stdout):
        mock_spent_minutes_string.return_value = '10'
        self.assertEqual(worklog_db.get_spent_minutes(), 10)
        mock_spent_minutes_string.side_effects = ['Not a number', 10]
        value = worklog_db.get_spent_minutes()
        self.assertEqual(value, 10)
        mock_spent_minutes_string.side_effects = ['-10', 10]
        self.assertEqual(worklog_db.get_spent_minutes(), 10)

    @mock.patch('worklog_db.initialize')
    @mock.patch('worklog_db.lookup_entries')
    @mock.patch('worklog_db.add_entry')
    @mock.patch('worklog_db.get_input', side_effect=['a', 'q', 'b', 'q'])
    def test_main(self, mock_get_input, mock_a, mock_b, _):
        worklog_db.main()
        mock_a.assert_called_once_with()
        worklog_db.main()
        mock_b.assert_called_once_with()

    @mock.patch('worklog_db.db.create_tables')
    @mock.patch('worklog_db.db.connect')
    def test_initalize(self, mock_connect, mock_create_tables):
        worklog_db.initialize()
        mock_connect.assert_called_once_with()
        mock_create_tables.assert_called_once_with([Entry], safe=True)

    @mock.patch('worklog_db.get_input', return_value="yo")
    def test_get_browse_input(self, _):
        self.assertEqual(worklog_db.get_browse_input(), 'yo')

    @mock.patch("worklog_db.Entry.delete_instance")
    @mock.patch("worklog_db.edit_entry", return_value=True)
    @mock.patch('worklog_db.get_browse_input', side_effect=['p', 'd',
                                                            'e'])
    def test_browse_through(self, _, mock_edit_entry, mock_delete):
        add_random_entry()
        entries = Entry.select()
        worklog_db.browse_through(entries)


    @mock.patch("worklog_db.get_name")
    def test_edit_name(self, mock_get):
        add_random_entry()
        entry = Entry.select().get()
        worklog_db.edit_name(entry)
        mock_get.assert_called_once()
        entry.delete_instance()

    @mock.patch("worklog_db.get_task")
    def test_edit_task(self, mock_get):
        add_random_entry()
        entry = Entry.select().get()
        worklog_db.edit_task(entry)
        mock_get.assert_called_once()
        entry.delete_instance()

    @mock.patch("worklog_db.get_notes")
    def test_edit_notes(self, mock_get):
        add_random_entry()
        entry = Entry.select().get()
        worklog_db.edit_notes(entry)
        mock_get.assert_called_once()
        entry.delete_instance()

    @mock.patch("worklog_db.get_spent_minutes")
    def test_edit_time(self, mock_get):
        add_random_entry()
        entry = Entry.select().get()
        worklog_db.edit_spent_minutes(entry)
        mock_get.assert_called_once()
        entry.delete_instance()

    @mock.patch('sys.stdin.read', return_value = 'foo')
    def test_get_notes(self, _):
        self.assertEqual(worklog_db.get_notes(), 'foo')

    @mock.patch('worklog_db.input', return_value='name')
    def test_get_name(self, _):
        self.assertEqual(worklog_db.get_name(), 'name')

    @mock.patch('worklog_db.input', return_value='task')
    def test_get_task(self, _):
        self.assertEqual(worklog_db.get_task(), 'task')

if __name__ == '__main__':
    test_db.connect()
    unittest.main()
