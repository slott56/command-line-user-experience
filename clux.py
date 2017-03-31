"""
Command-Line UX.

SunOS/Solaris CK* Commands

See https://docs.oracle.com/cd/E19683-01/816-0210/6m6nb7m5d/index.html

ckdate(1)- prompts for and validates a date
ckgid(1)- prompts for and validates a group id
ckint(1)- display a prompt; verify and return an integer value
ckitem(1)- build a menu; prompt for and return a menu item
ckkeywd(1)- prompts for and validates a keyword
ckpath(1)- display a prompt; verify and return a pathname
ckrange(1)- prompts for and validates an integer
ckstr(1)- display a prompt; verify and return a string answer
cktime(1)- display a prompt; verify and return a time of day
ckuid(1)- prompts for and validates a user ID
ckyorn(1)- prompts for and validates yes/no

TODO: Several other features

    -   The NoQuit option
    
    -   A '~' in help, error, or prompt prompt includes the default text
    
    -   Multiple bases for ckint()
"""
import datetime
import os
import pathlib
import re
from collections import namedtuple
from enum import Enum

class UserQuit(Exception):
    """The user entered q to quit."""
    pass


class Invalid(Exception):
    """The user input was invalid."""
    pass


class CKUI:
    """Superclass for all of the CKUI classes.
    """
    DEBUG = False
    
    PROMPT = "Enter an appropriate value"
    HELP = """Please enter a string which contains no embedded,
leading or trailing spaces or tabs
"""
    ERROR = """ERROR: Please enter a string which contains no embedded,
leading or trailing spaces or tabs.
"""
    
    HINT = '?,q'
    
    def help(self):
        """Inject values into the help template."""
        return self.HELP.format_map(vars(self))
        
    def error(self):
        """Inject values into the error template."""
        return self.ERROR.format_map(vars(self))
        
    def hint(self):
        """Inject values into the hint template."""
        return self.HINT.format_map(vars(self))
    
    def validate(self, text):
        """Validate input, returns canonical form or raises Invalid"""
        return text
        
    def __call__(self, *, prompt=None, default=None, help=None, error=None):
        """Core interaction loop.
        
        Prompt for input.
        Repond to "?", "q", End-of-File, and other inputs.
        
        Returns canonical string answer.
        Raises UserQuit when the user quits.
        """
        if prompt is None:
            prompt = self.PROMPT
        if error is None:
            error = self.ERROR
        response = None
        while not response:
            try:
                a=input("{} [{}]: ".format(prompt, self.hint()))
            except EOFError:
                raise UserQuit
            if a.lower() in ['q', 'quit']:
                raise UserQuit
            elif a in ['?']:
                print(help if help is not None else self.help())
            elif a == '' and default is not None:
                response = default
            else:
                try:
                    response = self.validate(a)
                except Invalid:
                    print(self.error())
        return response


class CKDATE(CKUI):
    """Gets a date."""
    PROMPT = 'Enter the date'
    HELP = 'Please enter a date. Format is {format}.'
    ERROR = 'ERROR - Please enter a date.  Format is {format}.'
    
    def validate(self, text):
        """Validate input, returns date."""
        try:
            dt = datetime.datetime.strptime(text, self.format)
            return dt.date()
        except Exception as ex:
            if self.DEBUG: 
                print(ex)
            raise Invalid
        
    def __call__(self, *, format="%m/%d/%y", **kw):
        self.format = format
        return super().__call__(**kw)


class CKINT(CKUI):
    """Gets an integer."""
    PROMPT = 'Enter an integer'
    HELP = 'Please enter an integer.'
    ERROR = 'ERROR - Please enter an integer.'
    
    def validate(self, text):
        """Validate input, returns canonical string version of the integer."""
        try:
            return int(text)
        except Exception:
            raise Invalid


class InputType(int, Enum):
    NUMERIC = 1
    TEXT = 2
    
class CKITEM(CKUI):
    """Gets an item from a menu."""
    PROMPT = 'Enter selection'
    HELP = '''
Enter the number of the menu item you wish to select, the token
which is associated with the menu item, or a partial string which
uniquely identifies the token for the menu item. Enter ? to
reprint the menu.
'''
    NUM_ERROR = 'ERROR: Bad numeric choice specification'
    TXT_ERROR = '''
ERROR: Entry does not match available menu selection. Enter the number
of the menu item you wish to select, the token which is associated
with the menu item, or a partial string which uniquely identifies the
token for the menu item. Enter ?? to reprint the menu.
'''
    HINT = '?,??,q'
    
    def validate(self, text):
        """Validate input, returns canonical form or raise Invalid exception."""
        try:
            item_num = int(text)
            if 1 <= item_num <= len(self.items):
                return self.items[item_num-1]
            raise Invalid(InputType.NUMERIC)
        except ValueError:
            text_lower = text.lower()
            matches = []
            for item in self.items:
                if item.startswith(text_lower):
                    matches.append(item)
            if len(matches) == 1:
                return matches[0]
            raise Invalid(InputType.TEXT)
    
    def show_menu(self):
        """Show the menu of choices."""
        if self.label:
            print(self.label)
        for n, item in enumerate(self.menu, 1):
            print("{}: {}".format(n, item))
            
    def __call__(self, *, prompt=None, default=None, help=None, error=None,
        label=None, choices=None, invisible=None):
        if prompt is None:
            prompt = self.PROMPT
        if error is None:
            error = self.ERROR
        if choices is None:
            raise ValueError("No choices given")
        self.label = label
        self.menu = choices
        self.items = choices + (invisible if invisible is not None else [])
        self.show_menu()
        response = None
        while not response:
            try:
                a=input("{} [{}]: ".format(prompt, self.hint()))
            except EOFError:
                raise UserQuit
            if a.lower() in ['q', 'quit']:
                raise UserQuit
            elif a in ['?']:
                print(help if help is not None else self.help())
            elif a in ['??']:
                self.show_menu()
            elif a == '' and default is not None:
                response = default
            else:
                try:
                    response = self.validate(a)
                except Invalid:
                    print(self.error())
        return response


class CKKEYWD(CKUI):
    """Gets a keyword from a list of choices."""
    PROMPT = 'Enter appropriate value'
    HELP = '{keywords},q'
    ERROR = 'ERROR: Please enter one of the following keywords: {keywords},q'
    HINT = '{keywords},?,q'

    def validate(self, text):
        """Validate input, returns canonical string version of the keyword."""
        text_lower = text.lower()
        matches = []
        for item in self.items:
            if item.startswith(text_lower):
                matches.append(item)
        if len(matches) == 1:
            return matches[0]
        raise Invalid(InputType.TEXT)

    def __call__(self, *, keywords=None, **kw):
        self.format = format
        if keywords is None:
            raise ValueError("No keywords given")
        self.items = keywords
        self.keywords = ','.join(self.items)
        return super().__call__(**kw)


class CKPATH(CKUI):
    """Gets a path. This is abstract. A concrete subclass must implement
    the validation rule.
        
    - Absolute vs. Relative
    - New vs. Existing
    - Readable and/or Writable and/or Executable
    - Block v. Character
    - Regular file v. Directory
    - Non-zero Size
    
    This class validates absolute paths.
    """
    PROMPT = "Enter a pathname"
    HELP = "Enter a pathname"
    ERROR = "ERROR: Invalid pathname"
    
    def validate(self, text):
        """Validation which checks for an absolute path.
        Returns canonical string representation.
        """
        try:
            p = pathlib.Path(text)
            if p.root == '/':
                return p.absolute()
            raise Invalid
        except FileNotFoundError:
            raise Invalid
    
class CKRANGE(CKINT):
    """Gets an integer in a range."""
    PROMPT = 'Enter an integer'
    HELP = 'Please enter an integer between {lower} and {upper}.'
    ERROR = 'ERROR - Please enter an integer between {lower} and {upper}.'
    
    def validate(self, text):
        """Validate input, returns canonical string version of the integer."""
        try:
            v = int(text)
            if self.lower <= v <= self.upper:
                return v
            raise Invalid
        except Exception:
            raise Invalid
            
    def __call__(self, *, lower=-2**31, upper=2**31-1, **kw):
        self.lower = lower
        self.upper = upper
        return super().__call__(**kw)


class CKSTR(CKINT):
    """Gets an string that matches a regular expression."""
    
    def validate(self, text):
        """Validate input, returns canonical string."""
        if self.regexp is None:
            return text
        try:
            m = self.regexp.match(text)
            if m:
                return text
            raise Invalid
        except Exception:
            raise Invalid
            
    def __call__(self, *, regexp=None, **kw):
        if regexp is not None:
            self.regexp = re.compile(regexp)
            self.HELP = "Please enter a sptring that matches the following pattern:\n{}".format(regexp)
            self.ERROR = "ERROR: {}".format(self.HELP)
        return super().__call__(**kw)


class CKTIME(CKUI):
    """Gets a time."""
    PROMPT = 'Enter the time'
    HELP = 'Please enter a time. Format is {format}.'
    ERROR = 'ERROR - Please enter a time.  Format is {format}.'
    
    def validate(self, text):
        """Validate input, returns canonical string time."""
        try:
            dt = datetime.datetime.strptime(text, self.format)
            return dt.time()
        except Exception as ex:
            if self.DEBUG: 
                print(ex)
            raise Invalid
        
    def __call__(self, *, format="%H:%M:%S", **kw):
        self.format = format
        return super().__call__(**kw)


class CKYORN(CKUI):
    """Gets a Yes or No."""
    PROMPT = 'Yes or No'
    HELP = '''
To respond in the affirmative, enter y, yes, Y, or YES.
To respond in the negative, enter n, no, N, or NO.
'''
    ERROR = 'ERROR - Please enter yes or no.'
    HINT = 'y,n,?,q'
    CANONICAL = {'y': 'yes', 'n': 'no'}

    def validate(self, text):
        clean_text = text.lower()
        if clean_text in ['y', 'n']:
            return self.CANONICAL[clean_text]
        elif clean_text in ['yes', 'no']:
            return clean_text
        raise Invalid


class CKGID(CKUI):
    """Gets a group name.  Linux-specific
    
    Uses /etc/group. Filters leading _ group names.
    """
    PROMPT = 'Enter the name of an existing group'
    HELP = 'Please enter one of the following group names: {groups}'
    ERROR = 'ERROR - Please enter one of the following group names: {groups}'
    
    def validate(self, text):
        name = text.lower()
        if name in self.groups:
            return name
        raise Invalid
    
    @staticmethod
    def exclude(name):
        return name.startswith("_")
        
    def get_groups(self):
        Group = namedtuple('Group', ['group', 'passwd', 'gid', 'member'])
        lines = pathlib.Path("/etc/group").read_text().splitlines()
        no_comment = filter(None, (lines.partition('#')[0] for lines in lines))
        group_iter = (Group(*line.split(":")) for line in no_comment)
        return list(g.group.lower() for g in group_iter if not self.exclude(g.group))
        
    def __call__(self, **kw):
        self.groups = self.get_groups()
        return super().__call__(**kw)
        
        
class CKUID(CKUI):
    """Gets a user name.
    
    Uses /etc/passwd.
    """
    PROMPT = 'Enter the name of an existing user'
    HELP = 'Please enter one of the following user names: {users}'
    ERROR = 'ERROR - Please enter one of the following user names: {users}'
    
    def validate(self, text):
        name = text.lower()
        if name in self.users:
            return name
        raise Invalid
        
    def get_users(self):
        User = namedtuple('User', ['name', 'passwd', 'uid', 'gid', 'gecos', 'home', 'shell'])
        lines = pathlib.Path("/etc/passwd").read_text().splitlines()
        no_comment = filter(None, (lines.partition('#')[0] for lines in lines))
        user_iter = (User(*line.split(":")) for line in no_comment)
        return list(g.name.lower() for g in user_iter)
        
    def __call__(self, **kw):
        self.users = self.get_users()
        return super().__call__(**kw)


ckdate = CKDATE()
ckgid = CKGID()
ckint = CKINT()
ckitem = CKITEM()
ckkeywd = CKKEYWD()
ckpath = CKPATH()
ckrange = CKRANGE()
ckstr = CKSTR()
cktime = CKTIME()
ckuid = CKUID()
ckyorn = CKYORN()

def demo():
    v1 = int(ckint(prompt="Enter a value"))
    v2 = int(ckint(prompt="Enter another value"))
    print("{} * {} = {}".format(v1, v2, v1*v2))
    
if __name__ == "__main__":
    demo()
