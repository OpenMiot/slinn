from slinn.eda import BaseEvent
from collections.abc import Callable


class BaseBus:
    def __init__(self):
        self.events: dict[BaseEvent, Callable] = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_subscribed_events"):
                for event in attr._subscribed_events:
                    self.events[event] = attr
    
    async def dispatch(self, event: BaseEvent, *args, **kwargs):
        return await self.events[event](*args, **kwargs)
