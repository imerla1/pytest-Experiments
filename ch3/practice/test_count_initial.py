from pathlib import Path
from tempfile import TemporaryDirectory
import cards


def test_empty(cards_db: cards.CardsDB):
    assert cards_db.count() == 0


def test_two(cards_db):
    cards_db.add_card(cards.Card("first"))
    cards_db.add_card(cards.Card("second"))
    assert cards_db.count() == 2