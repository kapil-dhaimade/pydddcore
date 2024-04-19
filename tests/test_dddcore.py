import pytest
import uuid

from pydddcore import (
    Entity,
    ValueObject,
    EntityId,
    DomainEvent,
    DomainException,
    DomainEventPublisher,
    DomainEventSubscriber,
    AggregateRoot
)


class DummyEntity(Entity):
    def __init__(self, entity_id: EntityId):
        super().__init__(entity_id)
        self.intVal: int = 0


class DummyValueObject(ValueObject):
    def __init__(self, intVal: int, strVal: str):
        self.intVal = intVal
        self.strVal = strVal


def test_entity_id_equality():
    assert EntityId("1") == EntityId("1")
    assert EntityId("2") != EntityId("3")
    assert EntityId("1") != EntityId()
    assert EntityId() != EntityId()


def test_entity_id_str():
    assert str(EntityId("12345-ABCDE")) == "12345-ABCDE"
    assert str(EntityId()) != ""


def test_entity_id_uses_uuid(mocker):
    mocker.patch("uuid.uuid4", 
                 return_value=uuid.UUID("12345678123456781234567812345678"))
    id1 = EntityId()
    assert str(id1) == "12345678123456781234567812345678"


def test_entity_equality():
    entity1 = DummyEntity(EntityId("1"))
    entity1.intVal = 5
    assert entity1 == entity1  # Same instance should be equal
    assert not entity1 != entity1

    entity2 = DummyEntity(EntityId("1"))
    entity2.intVal = 6
    assert entity1 == entity2  # Different instance with same id should be equal

    entity3 = DummyEntity(EntityId("2"))
    entity3.intVal = 5
    assert entity1 != entity3  # Different instance with different id
                               # but same attributes should not be equal

    entity4 = DummyEntity(EntityId("2"))
    entity4.intVal = 5
    assert entity3 == entity4  # Different instance with same id 
                               #should be equal


def test_multiple_new_entities_have_unique_ids():
    entity1 = Entity()
    entity2 = Entity()
    entity3 = Entity()
    entity4 = Entity()
    assert entity1.id != entity2.id != entity3.id != entity4.id


def test_entity_id_prop():
    entity = Entity(EntityId("1"))
    assert entity.id == EntityId("1")


def test_value_object_equality():
    value1 = DummyValueObject(5, "Hello")
    value2 = DummyValueObject(5, "Hello")
    assert value1 == value1  # Same instance should be equal
    assert not value1 != value1

    assert value1 == value2  # Different instances with same values should be equal
    assert not value1 != value2

    value3 = DummyValueObject(5, "World")
    assert value1 != value3  # Different instances with different values should not be equal

    value4 = DummyValueObject(6, "Hello")
    assert value1 != value4  # Different instances with different values should not be equal


def test_ddd_abstract_classes():
    with pytest.raises(TypeError):
        DomainEventPublisher()
    with pytest.raises(TypeError):
        DomainEventSubscriber()


def test_domain_event_name():
    class DummyDomainEvent(DomainEvent):
        _evt_name = "DummyEvent"
    event = DummyDomainEvent()
    assert event.name() == "DummyEvent"


def test_aggregate_root_is_an_entity():
    entity = AggregateRoot()
    assert isinstance(entity, Entity)


def test_domain_exception():
    with pytest.raises(DomainException) as e:
        raise DomainException("Test exception")
    assert str(e.value) == "Test exception"


def test_domain_exception_is_an_exception():
    with pytest.raises(Exception):
        raise DomainException("Test exception")
