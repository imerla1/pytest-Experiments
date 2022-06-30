# pytest fixtures
Fixtures are functions that are run by pytest before (and sometimes after) the actual test functions. The code in the fixture can do whatever you want it to. You can use fixtures to get a data set for the tests to work on. You can use fixtures to get a system into a known state before running a test. Fixtures are also used to get data ready for multiple tests.


# Getting Started with Fixtures
`ch3/test_fixtures.py`
```python3
import pytest

@pytest.fixture():
def some_data()
    """return answer to ultiamte question."""
    return 42

def test_some_data():
    """Use fixture return value in a test."""
    assert some_data == 42
```
The `@pytest.ﬁxture()` decorator is used to tell pytest that a function is a fixture. When you include the fixture name in the parameter list of a test function, pytest knows to run it before running the test. Fixtures can do work, and can also return data to the test function.

The test, `test_some_data()` , has the name of the fixture, `some_data` , as a parameter. pytest will see this and look for a fixture with this name.

# Using Fixtures for Setup and Teardown


```python3
@pytest.fixture()
def cards_db():
    with TemporaryDirectory() as db_dir:
        # Setup
        db_path = Path(db_dir)
        db = cards.CardsDB(db_path)
        yield db
        # Teardown
        db.close()


def test_empty(cards_db: cards.CardsDB):
    assert cards_db.count() == 0
```

Right off the bat we can see that the test function itself is way easier to read,
as we’ve pushed all the database initialization into a fixture called `cards_db`.

The `cards_db` **fixture** is “setting up” for the test by getting the database ready.
It’s then `yield` -ing the database object. That’s when the test gets to run. And
then after the test runs, it closes the database.

Fixture functions run before the tests that use them. If there is a `yield` in the function, it stops there, passes control to the tests, and picks up on the next line after the tests are done. The code above the `yield` is “setup” and the code after yield is **“teardown**.” The code after the yield , the teardown, is guaranteed to run regardless of what happens during the tests.

> **Remember**: pytest looks at the specific name of the arguments to our test
and then looks for a fixture with the same name. We never call fixture
functions directly. pytest does that for us.

You can use fixtures in multiple tests. Here’s another one:
```python3
def test_two(cards_db:cards .CardsDB):
    cards_db.add_card(cards.Card("first"))
    cards_db.add_card(cards.Card("first"))
    assert cards_db.count() == 2
```

The individual tests, such as `test_empty()` and `test_two()` can be kept smaller and focus on
what we are testing, and not the setup and teardown bits `fixtures` will handle those.
# Tracing Fixture Execution with –setup-show
for debugging it’s frequently helpful to visualize when the setup and teardown portions of fixtures run with respect the tests using them.

Fortunately, `pytest` provides the command-line flag, `--setup-show`
which shows us the order of operations of tests and fixtures, including the setup
and teardown phases of the fixtures:

`pytest --setup-show test_count.py`
```
collected 2 items                                                      

test_count_initial.py 
SETUP    S _session_faker
        SETUP    F cards_db
        test_count_initial.py::test_empty (fixtures used: _session_faker, cards_db, request).
        TEARDOWN F cards_db
        SETUP    F cards_db
        test_count_initial.py::test_two (fixtures used: _session_faker, cards_db, request).
        TEARDOWN F cards_db
TEARDOWN S _session_faker

```

We can see that our test runs, surrounded by the SETUP and TEARDOWN
portions of the cards_db fixture. 

The `F` in front of the fixture name indicates that the fixture is using function scope, meaning the fixture is called before each test function that uses it, and torn down after each function that uses it.
Let’s take a look at scope next.
# Specifying Fixture Scope

Each fixture has a specific scope, which defines the order of when the setup
and teardown run relative to running of all the test function using the fixture.
The scope dictates how often the setup and teardown get run when it’s used
by multiple test functions. The Default scope is `function` scope. that means the setup portion of the fixture will run before each test that needs it runs. Likewise, the teardown portion runs after the test is done, for each test.

## scopes

scope="**function**"
- >Run once per test function. The setup portion is run before each test
using the fixture. The teardown portion is run after each test using the
fixture. This is the default scope used when no scope parameter is
specified.

scope="**class**"
- > Run once per test class, regardless of how many test methods are in the
class.

scope="**module**"
- > Run once per module, regardless of how many test functions or
methods or other fixtures in the module use it.

scope="**package**"
- > Run once per package, or test directory, regardless of how many test
functions or methods or other fixtures in the package use it.

scope="**session**"

- > Run once per session. All test methods and functions using a fixture of
session scope share one setup and teardown call.


With a fixture defined within a test module, the session and package scopes
act just like module scope. In order to make use of these other scopes, we
need to put them in a `conftest.py` file

# Sharing Fixtures through conftest.py

You can put fixtures into individual test files, but to share fixtures among
multiple test files, you need to use a `conftest.py` file either in the same
directory as the test file that’s using it or in some parent directory.
```python3
#conftest.py
import pytest
from tempfile import TemporaryDirectory
import cards
from pathlib import Path


@pytest.fixture(scope="module")
def cards_db():
    """CardsDB object connected to a temporary database"""
    with TemporaryDirectory() as db_dir:
        # Setup
        db_path = Path(db_dir)
        db = cards.CardsDB(db_path)
        yield db
        # Teardown
        db.close()
```

Fixtures can only depend on other fixtures of their same scope or wider. So a
function-scope fixture can depend on other function-scope fixtures (the
default, and used in the Cards project so far). A function-scope fixture can
also depend on class-, module-, and session-scope fixtures, but you can’t go
in the reverse order.

> **Don't import conftest.py**: Although conftest.py is a Python module, it should not be
imported by test files. The conftest.py file gets read by pytest
automatically, so you don’t have import conftest anywhere.


# Finding Where Fixtures Are Defined
We’ve moved a fixture out of the test module and into a conftest.py file. We
can have conftest.py files at really every level of our test directory. Tests can
use any fixture that is in the same test module as a test function, or in a
conftest.py file in the same directory, or in any level of parent directory up to
the root of the tests.

That brings up a problem if we can’t remember where a particular fixture is
located and we want to see the source code. Of course, pytest has our back.
Just use `--ﬁxtures` and we are good to go.

You can also use `--ﬁxtures-per-test` to see what fixtures are used by each test
and where the fixtures are defined:

`pytest --fixtures-per-test test_count.py::test_empty`

# Using Multiple Fixture Levels
There’s a little bit of a problem with our test code right now. The problem is
the tests both depend on the database being empty to start with, but they use
the same database instance in the module-scope and session-scope versions.

The problem becomes very clear if we add a third test:

```python3
#test_three.py
import cards

def test_three(cards_db):
    cards_db.add_card(cards.Card("first"))
    cards_db.add_card(cards.Card("second"))
    cards_db.add_card(cards.Card("third"))
    assert cards_db.count() == 3

```

It works fine by itself, but not when it’s run after `test_count.py::test_two` :
```
$ pytest -v test_three.py
========================== test session starts ==========================
collected 1 item
test_three.py::test_three PASSED
[100%]
=========================== 1 passed in 0.01s ===========================
$ pytest -v --tb=line test_count.py test_three.py
========================== test session starts ==========================
collected 3 items
test_count.py::test_empty PASSED
test_count.py::test_two PASSED
test_three.py::test_three FAILED
[ 33%]
[ 66%]
[100%]
=============================== FAILURES ================================
/path/to/code/ch3/a/test_three.py:8: assert 5 == 3
======================== short test summary info ========================
FAILED test_three.py::test_three - assert 5 == 3
====================== 1 failed, 2 passed in 0.01s ======================
```

There are five elements in the database because the previous test added two
items before test_three ran. There’s a time-honored rule of thumb that says
tests shouldn’t rely on the run order. And clearly, this does. `test_three` passes
just fine if we run it by itself, but fails if it is run after `test_two`.

```python3
import pytest
from tempfile import TemporaryDirectory
import cards
from pathlib import Path


@pytest.fixture(scope="session")
def db():
    """CardsDB object connected to a temporary database"""
    with TemporaryDirectory() as db_dir:
        # Setup
        db_path = Path(db_dir)
        db = cards.CardsDB(db_path)
        yield db
        # Teardown
        db.close()

@pytest.fixture(scope="function")
def cards_db(db):
    """CardsDB object that's empty"""
    db.delete_all()
    return db
```

I’ve renamed the old cards_db to db and made it session scope.
The cards_db fixture has db named in its parameter list, which means it
depends on the db fixture. Also, cards_db is function scoped, which is a more
narrow scope than db . When fixtures depend on other fixtures, they can only
use fixtures that have equal or wider scope.

# Using Multiple Fixtures per Test or Fixture

Another way we can use multiple fixtures is just to use more than one in
either a function or a fixture. As an example, we can put some pre-canned
tasks together to test with as a fixture:


```python3
#conftest.py
@pytest.fixture(scope="session")
def some_cards():
    """List of different Card objects"""
    return [
        cards.Card("write book", "Brian", "done"),
        cards.Card("edit book", "Katie", "done"),
        cards.Card("write 2nd edition", "Brian", "todo"),
        cards.Card("edit 2nd edition", "Katie", "todo"),
    ]


```
Then we can use both `empty_db` and `some_cards` in a test:
```python3
# test_some.py
import cards

def test_add_some(cards_db, some_cards):
    expected_count = len(some_cards)
    for card in some_cards:
        cards_db.add_card(card)
    assert expected_count == cards_db.count()
        

```

Fixtures can also use multiple other fixtures:

```python3
@pytest.fixture(scope= "function" )
def non_empty_db (cards_db, some_cards):
    """CardsDB object that's been populated with 'some_cards'"""
    for c in some_cards:
    cards_db.add_card(c)
    return cards_db
```

The fixture `non_empty_db` has to be `function scope` because it uses `cards_db` ,
which is `function scope`.  If you try to make non_empty_db module scope or
wider, pytest will throw an error. Remember that if you don’t specify a
scope, you get function-scope fixtures.

And now, tests that need a database with stuff in it can do that easily:

```python3
# test_some.py
def test_non_empty (non_empty_db):
    assert non_empty_db.count() > 0
```

# Using autouse for Fixtures That Always Get Used
So far in this chapter, all of the fixtures used by tests were named by the tests or another fixture in a parameter list. However, you can use
`autouse=True` to get a fixture to run all of the time. This works well for code you want to run at certain times, but tests don’t really depend on any system state or data from the fixture.

```python3
import pytest
import time


@pytest.fixture(autouse=True, scope="session")
def footer_session_scope():
    """Report the time at the end of a session"""
    yield
    now = time.time()
    print(
        "finished : {}" .format(
            time.strftime("%d %b %X", time.localtime(now))
        )
    )
    print("---------------")


@pytest.fixture(autouse=True)
def footer_function_scope():
    """Report test durations after each function."""
    start = time.time()
    yield
    stop = time.time()
    delta = stop - start
    print("\ntest duration : {:0.3} seconds" .format(delta))


def test_1():
    """Simulate long-ish running test."""
    time.sleep(1)


def test_2():
    """Simulate slightly longer test."""
    time.sleep(1.23)

```

We want to add test times after each test, and the date and current time at the
end of the session. Here’s what these look like:
`pytest -v -s test_autouse.py`

```sh
===================== test session starts ======================
collected 2 items
test_autouse.py::test_1 PASSED
test duration : 1.0 seconds
test_autouse.py::test_2 PASSED
test duration : 1.24 seconds
--
finished : 25 Jul 16:18:27
-----------------
=================== 2 passed in 2.25 seconds ===================
```

I used the `-s` flag in this example. It’s a shortcut flag for `--capture=no` that tells pytest to turn off output capture. I used it because the new fixtures have print
functions in them, and I wanted to see the output. Without turning off output
capture, pytest only prints the output of tests that fail.

# Renaming Fixtures
The name of a fixture, listed in the parameter list of tests and other fixtures
using it, is usually the same as the function name of the fixture. However,
pytest allows you to rename fixtures with a name parameter to
```python3
#test_rename_fixture.py
import pytest

@pytest.fixture(name="ultimate_answer")
def ultimate_answer_fixture():
    return 42

def test_everything(ultimate_answer):
    assert ultimate_answer == 42


```

# review
- Fixtures are `@pytest.ﬁxture()` decorated functions.
- Test functions or other fixtures depend on a fixture by putting its name in their parameter list.
- Fixtures can return data using return or yield .
- Code before the `yield` is the **setup code**. Code after the yield is the **teardown** code.
- Fixtures can be set to function, class, module, package, or session
scope. The default is function scope. You can even define the scope dynamically.
- Multiple test functions can use the same fixture.
- Multiple test modules can use the same fixture if it’s in a `conftest.py` file.
- Multiple fixtures at different scope can speed up test suites while maintaining test isolation.
- Tests and fixtures can use multiple fixtures.
- Autouse fixtures don’t have to be named by the test function.
- You can have the name of a fixture be different than the fixture function name.
- `pytest --setup-show` is used to see the order of execution.
- `pytest --ﬁxtures` is used to list available fixtures and where the fixture is located.
- -s and --capture=no allow print statements to be seen even in passing tests.