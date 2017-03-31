#####################################
A Command-Line User Experience (CLUX)
#####################################

This is an implementation of some of the features
of the Sunos/Solaris "ck..." commands

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

This requires Python 3.

All of functions lean heavily on ``print()`` and ``input()``.

Usage
=====

::

    from clux import *
    def demo():
        v1 = ckint(prompt="Enter a value")
        v2 = ckint(prompt="Enter another value")
        print("{} * {} = {}".format(v1, v2, v1*v2))
        
The original functions returned canonical string values. This reflected
a limitation of the shell programming language. These functions return
Python objects of appropriate types.

Extension
=========

The ``ckpath()`` function often has extremely complex validation 
rules. The version provided here only validates that the input
path is absolute, which is rarely what you want.

The ``validate()`` method must return the canonical string value
if things are valid, or raise an clux.Invalid exception if things
are not.

::

    import clux
    class CKPATHABSDIR(clux.CKPATH):
        HELP = "Enter the absolute pathname for a directory"
        def validate(self, text):
            try:
                p = pathlib.Path(text)
                if p.root == '/' and p.is_dir():
                    return str(p.absolute())
                raise clux.Invalid
            except FileNotFoundError:
                raise clux.Invalid
                
    ckpathabsdir = CKPATHABSDIR()
            
In this example, the path must be absolute and a reference to a directory.
