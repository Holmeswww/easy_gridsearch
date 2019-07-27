import sys
from threading import Lock
import random
import time

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds, granularity=2):
    seconds=int(seconds)
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class Writer(object):
    """Create an object with a write method that writes to a
    specific place on the screen, defined at instantiation.
    This is the glue between blessings and progressbar.
    """
    def __init__(self, term, height):
        """
        Input: location - tuple of ints (x, y), the position
                          of the bar in the terminal
        """
        self.terminal = term
        self.height = height

    def write(self, string):
        with self.terminal.location(0, self.height):
            print(string.replace("\n", ""), end = "")
    
    def flush(self):
        sys.stdout.flush()

class EWriter(object):
    """Create an object with a write method that writes to a
    specific place on the screen, defined at instantiation.
    This is the glue between blessings and progressbar.
    """
    def __init__(self, term):
        """
        Input: location - tuple of ints (x, y), the position
                          of the bar in the terminal
        """
        self.terminal = term

    def write(self, string):
        with self.terminal.location(0, self.terminal.height - 2):
            print(string.replace("\n", ""), end = "")
    
    def flush(self):
        sys.stdout.flush()


class SafeList(object):

    def __init__(self):
        self.lock = Lock()
        self.list = []

    def __len__(self):
        return len(self.list)

    def append(self, item):
        self.lock.acquire()
        self.list.append(item)
        self.lock.release()
    
    def randpop(self):
        self.lock.acquire()
        if len(self.list)==0:
            self.lock.release()
            return None
        idx = random.randint(0, len(self.list)-1)
        res = self.list.pop(idx)
        self.lock.release()
        return res


class SafeValue(object):

    def __init__(self, init_val, comp):
        self.lock = Lock()
        self.msg = ""
        self.comp = comp
        self.val = init_val

    def update(self, val, msg):
        self.lock.acquire()
        if self.comp(val, self.val):
            self.val = val
            self.msg = msg
        self.lock.release()
    
    def get(self):
        return self.msg