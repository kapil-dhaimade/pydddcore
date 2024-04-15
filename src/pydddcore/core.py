import uuid
from abc import ABC, abstractmethod


class ValueObject(ABC):
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other


class EntityId(ValueObject):
    def __init__(self, id: str):
        self._id: str = id

    @staticmethod
    def create_new() -> 'EntityId':
        return EntityId(uuid.uuid4().hex)

    def __str__(self) -> str:
        return self._id


class Entity(ABC):
    def __init__(self, id: EntityId = EntityId.create_new()):
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


class DomainEvent(ABC):
    _evt_name: str = ""

    def name(self) -> str:
        return self.__class__._evt_name


class DomainEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent):
        pass


class DomainEventSubscriber(ABC):
    @abstractmethod
    def handleEvent(self, event: DomainEvent):
        pass


class DomainService(ABC):
    pass


class Repository(ABC):
    pass
