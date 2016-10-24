"""
Base class for recipy test cases.
"""

# Copyright (c) 2016 University of Edinburgh.

import os
import sys
import collections


class Base:
    """
    Base class for recipy test cases.
    """

    def __init__(self):
        """
        Constructor. Set current_dir attribute with path to directory
        in which this file lives.
        """
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        print(("Current directory: ", self.current_dir))

    def invoke(self, arguments):
        """
        Invoke a function on a sub-class.

        * arguments must be at least of length 2 (the first element
          being a script name).
        * The second element is assumed to be a function name of
          a sub-class of this class.
        * The function is assumed to take zero arguments and
          return nothing.
        * Other elements in arguments are ignored.

        :param arguments: Arguments, typically from command-line.
        :type arguments: list of str or unicode.
        """
        print(("Arguments: ", arguments))
        if len(arguments) < 2:
            sys.stderr.write("Missing function name")
            sys.exit(1)
        function_name = arguments[1]
        print(("Function: ", function_name))
        if not hasattr(self, function_name):
            sys.stderr.write((str(self.__class__.__name__) +
                              " has no function " + function_name + "\n"))
            sys.stderr.write("Functions:\n")
            for value in dir(self):
                if not value.startswith("__") and\
                  isinstance(getattr(self, value), collections.Callable):
                    sys.stderr.write((value + "\n"))
            sys.exit(1)
        function = getattr(self, function_name)
        print(("Invoking: ", function))
        function()
