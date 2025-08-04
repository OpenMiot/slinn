class Handle:
    def __init__(self, _filter, function, args=lambda *args, **kwargs: {}):
        self.filter = _filter
        self.function = function
        self.args = args
