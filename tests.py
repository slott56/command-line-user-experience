#!/usr/bin/python3
"""Tests
"""

import clux
import unittest
from unittest.mock import Mock, patch, call
import datetime
import pathlib

class Test_CKDATE(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['9/10/11']))
    def test_good_y(self):
        response = clux.ckdate(prompt="date")
        self.assertEqual(datetime.date(2011,9,10), response)
        clux.input.assert_called_once_with('date [?,q]: ')
        clux.print.assert_not_called()

    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['bad', '1/2/03']))
    def test_bad(self):
        response = clux.ckdate(prompt="date")
        self.assertEqual(datetime.date(2003,1,2), response)
        clux.input.assert_has_calls([
            call('date [?,q]: '),
            call('date [?,q]: '),
        ])
        clux.print.assert_called_once_with('ERROR - Please enter a date.  Format is %m/%d/%y.')

class Test_CKGID(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['wheel']))
    @patch('clux.pathlib', Mock(Path=Mock(return_value=Mock(
        read_text=Mock(return_value='wheel:*:0:root\ndaemon:*:1:root\n')))))
    def test_good_group(self):
        response = clux.ckgid(prompt="group")
        self.assertEqual("wheel", response)
        clux.input.assert_called_once_with('group [?,q]: ')
        clux.print.assert_not_called()
        clux.pathlib.Path.assert_called_once_with('/etc/group')


class Test_CKINT(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['42']))
    def test_good_int(self):
        response = clux.ckint(prompt="int")
        self.assertEqual(42, response)
        clux.input.assert_called_once_with('int [?,q]: ')
        clux.print.assert_not_called()


class Test_CKITEM(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['1']))
    def test_good_num_item(self):
        response = clux.ckitem(prompt="menu", label="items", choices=["this", "that"])
        self.assertEqual("this", response)
        clux.input.assert_called_once_with('menu [?,??,q]: ')
        clux.print.assert_has_calls([
            call('items'),
            call("1: this"),
            call("2: that")
        ])
        
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['that']))
    def test_good_txt_item(self):
        response = clux.ckitem(prompt="menu", label="items", choices=["this", "that"])
        self.assertEqual("that", response)
        clux.input.assert_called_once_with('menu [?,??,q]: ')
        clux.print.assert_has_calls([
            call('items'),
            call("1: this"),
            call("2: that")
        ])


class Test_CKKEYWD(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['that']))
    def test_good_kw(self):
        response = clux.ckkeywd(prompt="kw", keywords=["this", "that"])
        self.assertEqual("that", response)
        clux.input.assert_called_once_with('kw [this,that,?,q]: ')
        clux.print.assert_not_called()


class Test_CKPATH(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['/etc/profile']))
    def test_good_abs_path(self):
        response = clux.ckpath(prompt="path")
        self.assertEqual(pathlib.PurePath("/etc/profile"), response)
        clux.input.assert_called_once_with('path [?,q]: ')
        clux.print.assert_not_called()


class Test_CKRANGE(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['4']))
    def test_good_int(self):
        response = clux.ckrange(prompt="int", lower=1, upper=10)
        self.assertEqual(4, response)
        clux.input.assert_called_once_with('int [?,q]: ')
        clux.print.assert_not_called()

    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['42', '5']))
    def test_bad_int(self):
        response = clux.ckrange(prompt="int", lower=1, upper=10)
        self.assertEqual(5, response)
        clux.input.assert_has_calls([call('int [?,q]: '), call('int [?,q]: ')])
        clux.print.assert_has_calls([call('ERROR - Please enter an integer between 1 and 10.')])


class Test_CKSTR(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['nope', 'word123']))
    def test_good_int(self):
        response = clux.ckstr(prompt="str", regexp=r"\w+\d+")
        self.assertEqual("word123", response)
        clux.input.assert_has_calls([call('str [?,q]: '), call('str [?,q]: ')])
        clux.print.assert_has_calls([call('ERROR: Please enter a sptring that matches the following pattern:\n\\w+\\d+')])
        

class Test_CKTIME(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['9:10:11']))
    def test_good_y(self):
        response = clux.cktime(prompt="time")
        self.assertEqual(datetime.time(9,10,11), response)
        clux.input.assert_called_once_with('time [?,q]: ')
        clux.print.assert_not_called()


class Test_CKUID(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['jsmith']))
    @patch('clux.pathlib', Mock(Path=Mock(return_value=Mock(
        read_text=Mock(return_value='jsmith:x:1001:1000:Joe Smith,Room 1007,(234)555-8910,(234)555-0044,email:/home/jsmith:/bin/sh\n')))))
    def test_good_group(self):
        response = clux.ckuid(prompt="user")
        self.assertEqual("jsmith", response)
        clux.input.assert_called_once_with('user [?,q]: ')
        clux.print.assert_not_called()
        clux.pathlib.Path.assert_called_once_with('/etc/passwd')


class Test_CKYORN(unittest.TestCase):
    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['y']))
    def test_good_y(self):
        response = clux.ckyorn(prompt="prompt")
        self.assertEqual("yes", response)
        clux.input.assert_called_once_with('prompt [y,n,?,q]: ')
        clux.print.assert_not_called()

    @patch('clux.print', Mock())
    @patch('clux.input', Mock(side_effect=['bad', 'n']))
    def test_bad(self):
        response = clux.ckyorn(prompt="prompt")
        self.assertEqual("no", response)
        clux.input.assert_has_calls([
            call('prompt [y,n,?,q]: '),
            call('prompt [y,n,?,q]: '),
        ])
        clux.print.assert_called_once_with('ERROR - Please enter yes or no.')
        
if __name__ == "__main__":
    unittest.main()
        
