import uuid

class ValueObject:
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
    
    def __ne__(self, other: object) -> bool:
        return not self == other
    
class EntityId(ValueObject):
    def __init__(self):
        self._id: str = uuid.uuid4().hex

    def __init__(self, id: str):
        self._id: str = id

    def __str__(self) -> str:
        return self._id
    
class Entity:
    def __init__(self):
        self._id: EntityId = EntityId()

    def __init__(self, id: EntityId):
        self._id: EntityId = id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._id == other._id
        return False
    
    def __ne__(self, other: object) -> bool:
        return not self == other

    @property
    def id(self) -> EntityId:
        return self._id

class AggregateRoot(Entity):
    def __init__(self, id: EntityId):
        super().__init__(id)

class DomainException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class DomainEvent:
    _evt_name: str = ""

    def name(self) -> str:
        return self.__class__._evt_name

class DomainEventPublisher:
    def publish(self, event: DomainEvent):
        pass

class DomainEventSubscriber:
    def handleEvent(self, event: DomainEvent):
        pass

class DomainService:
    pass

class Repository:
    pass