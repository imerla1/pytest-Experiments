"""
Testing for Expected Exceptions
We’ve looked at how any exception can cause a test to fail. But what if a bit
of code you are testing is supposed to raise an exception? How do you test
for that?
You use pytest.raises() to test for expected exceptions.
As an example, the cards API has a CardsDB class that requires a path
argument. What happens if we don’t pass in a path? Let’s try it:
"""

import cards
import pytest


def test_no_path_fail():
    with pytest.raises(TypeError):
        cards.CardsDB()


def test_raises_with_info():
    match_regex = "missing 1 .* positional argument"
    with pytest.raises(TypeError, match=match_regex):
        cards.CardsDB()


def test_raises_with_info_alt():
    with pytest.raises(TypeError) as exc_info:
        cards.CardsDB()
    expected = "missing 1 required positional argument"
    assert expected in str(exc_info.value)
