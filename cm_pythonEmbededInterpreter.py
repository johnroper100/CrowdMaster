import code


class Interpreter(code.InteractiveConsole):
    """A python interpreter to run the code that is input by user to brains"""
    def __init__(self, *args):
        code.InteractiveConsole.__init__(self, *args)

    def enter(self, codesource):
        """Run code"""
        source = self.preprocess(codesource)
        self.runcode(source)

    @staticmethod
    def preprocess(codesource):
        """This could be used to add macros"""
        return codesource

    def setup(self, localvars):
        """Add pre-declared variables such as the channels"""
        self.locals = {'__name__': '__console__', '__doc__': None}
        for v in localvars:
            self.locals[v] = localvars[v]

    def getoutput(self):
        """Get the output of the scripts"""
        if "output" in self.locals:
            return self.locals["output"]
        else:
            print("Script must have out output")
