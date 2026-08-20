from slinn.eda import BaseEvent


class HttpRequestReceived(BaseEvent):
    def __init__(self):
        super().__init__('HttpRequestReceived')
