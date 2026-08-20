from slinn.eda import BaseEvent


def on(event: BaseEvent):
    def decorator(func):
        if not hasattr(func, "_subscribed_events"):
            func._subscribed_events = []
        func._subscribed_events.append(event)
        return func
    return decorator
