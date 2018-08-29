from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import time
import warnings

from recipyCommon.config import set_notebook_mode

# The class MUST call this class decorator at creation time
@magics_class
class RecipyMagic(Magics):
    def __init__(self, shell):
        super(RecipyMagic, self).__init__(shell)
        self.recipyModule = None
        self.run_in_progress = False

    def loadNotebookName_js(self):
        cell = '''
%%javascript

var kernel = IPython.notebook.kernel;
var attribs = document.body.attributes;
var command = "recipyNotebookName = " + "'"+attribs['data-notebook-name'].value+"'";
console.log("Load notebook name...")
kernel.execute(command);
'''
        r = self.shell.run_cell(cell)
        return r

    def getNotebookName(self):
        retries = 5
        while retries > 0:
            if 'recipyNotebookName' in self.shell.user_ns:
                return self.shell.user_ns['recipyNotebookName']
            else:
                retries -= 1
                time.sleep(1)

        return None


    @line_magic
    def loadNotebookName(self, line):
        "my line magic"
        # print("Full access to the main IPython object:", self.shell)
        # print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
        self.loadNotebookName_js()
        return None

    @line_magic
    def recipyOn(self, line):
        "my line magic"
        # print("Full access to the main IPython object:", self.shell)
        # print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
        set_notebook_mode(True)

        notebookName = self.getNotebookName()
        if notebookName is None:
            print("[Recipy] Warning! Unable to get notebook name! Try running notebook step by step")
            notebookName = "<unknown-notebook>"
        import recipy
        recipy.log_init(notebookName=notebookName)
        self.run_in_progress = True
        self.recipyModule = recipy
        return None

    @line_magic
    def recipyOff(self, line):
        "my line magic"
        # print("Full access to the main IPython object:", self.shell)
        # print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
        if self.run_in_progress:
            self.recipyModule.log_flush()
            self.run_in_progress = False
        else:
            warnings.warn('Please run %recipyOn before running %recipyOff.',
                          RuntimeWarning)
        return None

def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    ipython.register_magics(RecipyMagic)

def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass
