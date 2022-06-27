from cards import Card, CardsDB
import pytest


def assert_identical(c1: Card, c2: Card):
    __tracebackhide__ = True
    assert c1 == c2
    if c1.id != c2.id:
        pytest.fail(f"id's don't match. {c1.id} != {c2.id}")


def test_field_access():
    card = Card(
        summary="todo",
        owner="george",
        state="done",
        id=530
    )

    assert card.summary == "todo"
    assert card.owner == "george"
    assert card.state == "done"
    assert card.id == 530


def test_default_values():
    card = Card()
    assert card.summary is None
    assert card.owner is None
    assert card.state == "todo"
    assert card.id is None


def test_assert_identical_cards():
    "Compares two Cards"
    c1 = Card(
        "todo", "george", "finished", 123
    )
    c2 = Card(
        "todo", "george", "finished", 123
    )

    assert_identical(c1, c2)


def test_from_dict():
    c1 = Card(
        "todo", "george", "finished", 123
    )

    c1_dict = {
        "summary": "todo",
        "owner": "george",
        "state": "finished",
        "id": 123
    }
    assert c1 == Card.from_dict(c1_dict)


def test_to_dict():
    c1 = Card(
        "todo", "george", "finished", 123
    )

    c1_dict = {
        "summary": "todo",
        "owner": "george",
        "state": "finished",
        "id": 123
    }

    assert c1_dict == Card.to_dict(c1)


def test_no_path_fail():
    with pytest.raises(TypeError):
        CardsDB()


def test_assert_identical_cards_fail():
    c1 = Card(
        "todo", "george", "finished", 123
    )
    c2 = Card(
        "todo", "george", "finished", 124
    )

    assert_identical(c1, c2)
