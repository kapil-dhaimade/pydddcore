import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone


class ValueObject(ABC):
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other


class EntityId(ValueObject):
    def __init__(self, id: str = None):
        self._id: str = id if id is not None else uuid.uuid4().hex

    def __str__(self) -> str:
        return self._id


class Entity(ABC):
    def __init__(self, id: EntityId = None):
        self._id = id if id is not None else EntityId()

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
    def __init__(self, id: EntityId = None):
        super().__init__()


class DomainException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DomainEvent(ABC):
    _evt_name: str = ""

    def __init__(self, timestamp_utc: datetime = None) -> None:
        super().__init__()
        self._timestamp_utc: datetime = timestamp_utc if \
            timestamp_utc is not None else datetime.now(timezone.utc)

    @property
    def name(self) -> str:
        return self.__class__._evt_name

    @property
    def timestamp_utc(self) -> datetime:
        return self._timestamp_utc


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


class ApplicationService(ABC):
    pass


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, obj: object) -> bool:
        pass
