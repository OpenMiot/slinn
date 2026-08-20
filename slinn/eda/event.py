class BaseEvent:
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return f'<Event {self.name}>'

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return type(self) is type(other)
