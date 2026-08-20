from slinn.eda import BaseEvent


class Accepted(BaseEvent):
    def __init__(self):
        super().__init__('Accepted')


class DataReceived(BaseEvent):
    def __init__(self):
        super().__init__('DataReceived')
