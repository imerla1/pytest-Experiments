# Writing Knowledge-Building Tests

The Cards source code is split into three layers: CLI, API, and DB.
- CLI handles the interaction with use
- API handles most logic of the application, calls into db layer for saving and retreving data
- DB Handling database operations 

`cards_proj/src/cards/api.py`
```python3
@dataclass
class Card:
    summary: str = None
    owner: str = None
    state: str = "todo"
    id: int = field(default=None, compare=False)
    @classmethod
    def from_dict (cls, d):
        return Card(**d)
    def to_dict (self):
        return asdict(self)
```

the `Card` structure has three String fields. summary, owner, and state and one integer field `id`.

# Using assert statements
When you write test functions, the normal Python assert statement is your
primary tool to communicate test failure. The simplicity of this within pytest
is brilliant. It’s what drives a lot of developers to use pytest over other
frameworks.
If you’ve used any other testing framework, you’ve probably seen various
assert helper functions. For example, following is a list of a few of the assert
forms and assert helper functions from unittest:
| pytest               | unittest               |
| -------------------- | ---------------------- |
| assert something     | assertTrue(something)  |
| assert not something | assertFalse(something) |
| assert a == b        | assertEqual(a, b)      |
| assert a != b        | assertNotEqual(a, b)   |
| assert a is None     | assertIsNone(a)        |


With pytest, you can use assert `expression` with any expression. If the
expression would evaluate to False if converted to a bool , the test would fail.

#assert rewriting 
pytest includes a feature called “assert rewriting” that intercepts assert calls
and replaces them with something that can tell you more about why your
assertions failed. Let’s see how helpful this rewriting is by looking at an
assertion failure:
`ch2/test_card_fail.py`
```python3
def test_equality_fail ():
    c1 = Card( "sit there" , "brian" )
    c2 = Card( "do something" , "okken" )
    assert c1 == c2
```
This test will fail, but what’s interesting is the traceback information:
```sh 
pytest test_card_fail.py
```
```
===================== test session starts ======================
collected 1 item
test_card_fail.py F
[100%]
=========================== FAILURES ===========================
______________________ test_equality_fail ______________________

def test_equality_fail():
c1 = Card("sit there", "brian")
c2 = Card("do something", "okken")
assert c1 == c2
AssertionError: assert Card(summary=...odo', id=None) ==
Card(summary=...odo', id=None)
Omitting 1 identical items, use -vv to show
Differing attributes:
['summary', 'owner']
Drill down into differing attribute summary:
summary: 'sit there' != 'do something'...
...Full output truncated (8 lines hidden),
use '-vv' to show
test_card_fail.py:7: AssertionError
=================== short test summary info ====================
FAILED test_card_fail.py::test_equality_fail - AssertionError...
====================== 1 failed in 0.07s =======================
```

# Failing with pytest.fail() and Exceptions
A test will fail if there is any uncaught exception. This can happen if
- an `assert` statement fails, which will raise an AssertionError exception
- the test code calls `pytest.fail()` , which will raise an exception
- any other exception is raised.

# Using pytest.fail() to explicitly fail a test
```python3
import pytest
from cards import Card
def test_with_fail():
    c1 = Card()
    c2 = Card(state="finished")
    if c1 != c2 :
        pytest.fail("they don't match")
```
When calling `pytest.fail()` or raising an exception directly, we don’t get the
wonderful assert rewriting provided by pytest. However, there are
reasonable times to use pytest.fail() , such as in an assertion helper.

# Writing Assertion Helper Functions

An assertion helper is a function that is used to wrap up a complicated
assertion check. As an example, the Cards data class is set up such that two
cards with different IDs will still report equality. If we wanted to have a
stricter check, we could write a helper function called `assert_identical` like

`ch2/test_helper.py`
```python3
from cards import Card
import pytest

def assert_identical(c1: Card1, c2: Card2):
    __tracebackhide__ = True
    assert c1 == c2
    if c1.id != c2.id:
        pytest.fail(f"id's don't match. {c1.id} != {c2.id}")
```

The assert_identical function sets __tracebackhide__ = True . This is optional. The
effect will be that failing tests will not include this function in the traceback.
The normal assert c1 == c2 is then used to check everything except the ID for
equality.
Finally, the IDs are checked, and if they are not equal, pytest.fail() is used to
fail the test with a hopefully helpful message.

### difference between __tracebackhide__ = True and __tracebackhide__ =False
 
<img src="/assets/traceback.png" alt="traceback"/>
If we had not put in the __tracebackhide__ = True , the assert_identical code would
have been included in the traceback, which in this case, wouldn’t have
added any clarity

**Note** that assert rewriting is only applied to `conftest.py` files and test files.

# Testing for Expected Exceptions

You use `pytest.raises()` to test for expected exceptions.

As an example, the cards API has a `CardsDB` class that requires a path
argument. if we won't pass path argument it will Raise `TypeError`

We can write a test to make sure this exception is thrown
`ch2/test_exceptions.py`
```python3
import cards
import pytest

def test_no_path_raises():
    with pytest.raises(TypeError):
        cards.CardsDB()
```

The with `pytest.raises(TypeError)`: statement says that whatever is in the next
block of code should raise a TypeError exception. If no exception is raised,
the test fails. If the test raises a different exception, it fails.

# Structuring Test Functions
I recommend making sure you keep assertions at the end of test functions.
This is such a common recommendation that it has at least two names:
**Arrange-Act-Assert** and **Given-When-Then**.

## Given-When-Then
`ch2/test_structure.py`
```python3
def test_to_dict ():
    # GIVEN a Card object with known contents
    c1 = Card( "something" , "brian" , "todo" , 123)
    # WHEN we call to_dict() on the object
    c2 = c1.to_dict()
    # THEN the result will be a dictionary with known content
    c2_expected = {
    "summary" : "something" ,
    "owner" : "brian" ,
    "state" : "todo" ,
    "id" : 123,
    }
    assert c2 == c2_expected
```
- Given/Arrange—A starting state. This is where you set up data or the
environment to get ready for the action.
- When/Act—Some action is performed. This is the focus of the test—the
behavior we are trying to make sure is working right.
- then/Assert—Some expected result or end state should happen. At the
end of the test, we make sure the action resulted in the expected
behavior.

# Grouping Tests with Classes
`pytest` Allows us to group test Casses with clasesses
`ch/test_classes.py`
```python3
from cards import Card

class TestEquality:

    def test_equality(self):
        c1 = Card("something", "brian", "todo", 123)
        c2 = Card("something", "brian", "todo", 123)
        assert c1 == c2

    def test_equality_with_diff_ids(self):
        c1 = Card("something", "brian", "todo", 123)
        c2 = Card("something", "brian", "todo", 4567)
        assert c1 == c2

    def test_inequality(self):
        c1 = Card("something", "brian", "todo", 123)
        c2 = Card("completely different", "okken", "done", 123)
        assert c1 != c2

```

now we can run all of these tests together by specifying the class
`pytest -v test_classes.py::TestEquality`

We can still get at a single method:
`pytest -v test_classes.py::TestEquality::test_equality`

# Running a Subset of Tests
Running just a small batch of tests is handy while debugging or if you
want to limit the tests to a specific section of the code base you are working
on at the time.

pytest allows you to run a subset of tests in several ways:

| Subset                        | Syntax                                        |
| ----------------------------- | --------------------------------------------- |
| Single test method            | `path/test_module.py::TestClass::test_method` |
| All tests in a class          | `pytest path/test_module.py::TestClass`       |
| Single test function          | `pytest path/test_module.py::test_function`   |
| All tests in a module         | `pytest path/test_modeule.py`                 |
| All tests in a directory      | `pytest path/to/dir`                          |
| Tests matching a name pattern | `pytest -k pattern`                           |

We’ll start from the top-level code directory so that we can use ch2 to show the path in the command-line examples

Running a single test method, test class, or module:
run single method
`pytest ch2/test_classes.py::TestEquality::test_equality`
Run whole class
`pytest ch2/test_classes.py::TestEquality`
Run module
`pytest ch2/test_classes.py`

Running a single test function
`pytest ch2/test_card.py::test_defaults`
Running the whole directory
`pytest ch2`

The `-k` argument takes an expression, and tells pytest to run tests that
contain a substring that matches the expression. The substring can be part of
the test name or the test class name. Let’s take a look at using `-k` in action.

We know we can run the tests in the TestEquality class with:
`pytest ch2/test_classes.py::TestEquality`

We can also use `-k` and just specify the test class name:
`pytest -v -k TestEquality`

or even just part of the name:

`pytest -v -k TestEq`

Let’s run all the tests with **“equality”** in their name:
`pytest -v --tb=no -k equality`

The keywords and, not, or, and parentheses are allowed to create complex
expressions. Here’s a test run of all tests with “dict” or “ids” in the name,
but not ones in the “TestEquality” class:
`pytest -v --tb=no -k "(dict or ids) and not TestEquality"`

# Review
- pytest uses assert rewriting, which allows us to use standard Python
assert expressions.
- Tests can fail from assertion failures, from calls to `fail()` , or from any uncaught exception.
- `pytest.raises()` is used to test for expected exceptions.
- A great way to structure tests is called Given-When-Then or Arrange-
Act-Assert
- Classes can be used to group tests.
- Running small subsets of tests is handy while debugging, and pytest
allows you to run a small batch of tests in many ways.
- The -vv command-line flag shows even more information during test
failures.