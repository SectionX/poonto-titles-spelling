class Operation:

    '''
    The TitleOperation Class defines operations that transform the original title to the corrected title.
    '''

    scope: str #word or title
    interrupt: bool #loop behavior


    def __init__(self, value):
        pass
    


class WordOperation(Operation):

    def __init__(self, interrupt=False):
        super().__init__()
        self.scope = 'word'
        self.interrupt =
