from . import HttpResponseChunk
from .exceptions import SSEEventIsEmpty


class SSEEvent(HttpResponseChunk):
    def __init__(self, *, event=None, event_id=None, full_data=None, retry=None, comments=None) -> None:
        payload = (f'event: {event}\n' if event else '')\
                + (f'id: {event_id}\n' if event_id else '')\
                + (''.join(f'data: {data}\n' for data in full_data) if full_data else '')\
                + (f'retry{retry}\n' if retry else '')\
                + (''.join(f': {comment}\n' for comment in comments) if comments else '')
        if not payload:
            raise SSEEventIsEmpty()
        super().__init__(payload=payload+'\n')
