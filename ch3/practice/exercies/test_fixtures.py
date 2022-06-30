import pytest
import time


@pytest.fixture(autouse=True, scope="session")
def runtime():
    """Calculates how long it take to complete all tests"""
    start = time.time()
    yield
    end = time.time()
    delta = end - start
    print("\ntest duration : {:0.3} seconds" .format(delta))


@pytest.fixture()
def dummy_list():
    """Return's list of integers"""
    return [1, 2, 3, 4]

@pytest.fixture()
def length_dummy_list(dummy_list: list):
    """Return's cleaned dummy list"""
    return len(dummy_list)

def test_dummy_list(dummy_list):
    expected_length = 4
    assert len(dummy_list) == expected_length

def test_list_length(length_dummy_list: len):
    assert isinstance(length_dummy_list, int)