import pytest
import uuid
from datetime import datetime
import sys

from pydddcore import (
    Entity,
    ValueObject,
    EntityId,
    DomainEvent,
    DomainException,
    DomainEventPublisher,
    DomainEventSubscriber,
    AggregateRoot,
    Specification,
    OrSpecification,
    AndSpecification,
    NotSpecification,
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


def test_entity_id_hash():
    assert hash(EntityId("1")) == hash(EntityId("1"))
    assert hash(EntityId("2")) != hash(EntityId("3"))
    assert hash(EntityId("1")) != hash(EntityId())
    assert hash(EntityId()) != hash(EntityId())


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
    # Different instance with same id should be equal
    assert entity1 == entity2

    entity3 = DummyEntity(EntityId("2"))
    entity3.intVal = 5
    # Different instance with different id
    # but same attributes should not be equal
    assert entity1 != entity3

    entity4 = DummyEntity(EntityId("2"))
    entity4.intVal = 5
    # Different instance with same id
    # should be equal
    assert entity3 == entity4


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

    # Different instances with same values should be equal
    assert value1 == value2
    assert not value1 != value2

    value3 = DummyValueObject(5, "World")
    # Different instances with different values should not be equal
    assert value1 != value3

    value4 = DummyValueObject(6, "Hello")
    # Different instances with different values should not be equal
    assert value1 != value4

    assert (value4 is None) is False


def test_ddd_abstract_classes():
    with pytest.raises(TypeError):
        DomainEventPublisher()
    with pytest.raises(TypeError):
        DomainEventSubscriber()


class DummyDomainEvent(DomainEvent):
    evt_name = "DummyEvent"

    def __init__(self, timestamp_utc: datetime = None):
        super().__init__(timestamp_utc)


def test_domain_event_name():
    event = DummyDomainEvent()
    assert event.name == "DummyEvent"


def test_domain_event_timestamp(mocker):
    # Need to patch datetime in core module for mocking to work.
    mocked_datetime = mocker.patch('pydddcore.core.datetime')

    mocked_datetime.now.return_value = \
        datetime.fromisoformat("2021-01-01T00:00:00+00:00")
    event = DummyDomainEvent()
    assert event.timestamp_utc == \
        datetime.fromisoformat("2021-01-01T00:00:00+00:00")

    if sys.version_info >= (3, 11):
        # Python 3.10 and below does not support 'Z' suffix in ISO 8601.
        mocked_datetime.now.return_value = \
            datetime.fromisoformat("2021-01-01T00:00:00Z")
        event2 = DummyDomainEvent()
        assert event2.timestamp_utc == \
            datetime.fromisoformat("2021-01-01T00:00:00Z")

    event3 = DummyDomainEvent(datetime.
                              fromisoformat("2023-02-03T00:00:00+00:00"))
    assert event3.timestamp_utc == datetime.\
        fromisoformat("2023-02-03T00:00:00+00:00")


def test_aggregate_root_is_an_entity():
    entity = AggregateRoot()
    assert isinstance(entity, Entity)


def test_aggregate_root_id():
    agg_root = AggregateRoot(EntityId("42"))
    assert agg_root.id == EntityId("42")


def test_domain_exception():
    with pytest.raises(DomainException) as e:
        raise DomainException("Test exception")
    assert str(e.value) == "Test exception"


def test_domain_exception_is_an_exception():
    with pytest.raises(Exception):
        raise DomainException("Test exception")


def test_base_specification_is_abstract():
    with pytest.raises(TypeError):
        Specification()


def test_dummy_specification():
    class DummySpec(Specification):
        def __init__(self, dummy_val: int):
            self._dummy_val = dummy_val

        def is_satisfied_by(self, candidate):
            return True
    spec = DummySpec(2)
    assert spec.is_satisfied_by(None) is True


class TrueSpec(Specification):
    def is_satisfied_by(self, candidate):
        return True


class FalseSpec(Specification):
    def is_satisfied_by(self, candidate):
        return False


def test_or_specification():
    true_spec = TrueSpec()
    false_spec = FalseSpec()

    or_spec = OrSpecification(true_spec, true_spec)
    assert or_spec.is_satisfied_by(None) is True

    or_spec = true_spec | true_spec
    assert or_spec.is_satisfied_by(None) is True

    or_spec = false_spec | false_spec
    assert or_spec.is_satisfied_by(None) is False

    or_spec = false_spec | true_spec
    assert or_spec.is_satisfied_by(None) is True

    or_spec = true_spec | false_spec
    assert or_spec.is_satisfied_by(None) is True


def test_and_specification():
    true_spec = TrueSpec()
    false_spec = FalseSpec()

    and_spec = AndSpecification(true_spec, true_spec)
    assert and_spec.is_satisfied_by(None) is True

    and_spec = true_spec & true_spec
    assert and_spec.is_satisfied_by(None) is True

    and_spec = false_spec & false_spec
    assert and_spec.is_satisfied_by(None) is False

    and_spec = false_spec & true_spec
    assert and_spec.is_satisfied_by(None) is False

    and_spec = true_spec & false_spec
    assert and_spec.is_satisfied_by(None) is False


def test_not_specification():
    true_spec = TrueSpec()
    false_spec = FalseSpec()

    not_spec = NotSpecification(true_spec)
    assert not_spec.is_satisfied_by(None) is False

    not_spec = ~true_spec
    assert not_spec.is_satisfied_by(None) is False

    not_spec = ~false_spec
    assert not_spec.is_satisfied_by(None) is True


def test_composite_specification():
    true_spec = TrueSpec()
    false_spec = FalseSpec()

    composite_spec = (true_spec & true_spec) | (false_spec & false_spec)
    assert composite_spec.is_satisfied_by(None) is True

    composite_spec = (~(false_spec & false_spec)) | (false_spec & true_spec)
    assert composite_spec.is_satisfied_by(None) is True

    composite_spec = (false_spec & false_spec) | (false_spec & true_spec)
    assert composite_spec.is_satisfied_by(None) is False

    composite_spec = (false_spec & false_spec) | (true_spec & true_spec)
    assert composite_spec.is_satisfied_by(None) is True

    composite_spec = (false_spec | false_spec) & (true_spec | false_spec)
    assert composite_spec.is_satisfied_by(None) is False
