# Builtin Fixtures
Reusing common fixtures is such a good idea that the pytest developers
included some commonly used fixtures with pytest. The builtin fixtures that
come prepackaged with pytest can help you do some pretty useful things in
your tests easily and consistently. For example, pytest includes builtin
fixtures that can handle temporary directories and files, access command-
line options, communicate between test sessions, validate output streams,
modify environment variables, and interrogate warnings

We’ll take a look at a few of the builtin fixtures in this chapter:

- `tmp_path` and `tmp_path_factory` —for temporary directories
- `capsys` —for capturing output
- `monkeypatch` —for changing the environment or application code, like a
lightweight form of mocking

# Using tmp_path and tmp_path_factory

The tmp_path and tmp_path_factory fixtures are used to create temporary
directories. The tmp_path function-scope fixture returns a pathlib.Path
instance that points to a temporary directory that sticks around during your
test and a bit longer. The tmp_path_factory session-scope fixture returns a
TempPathFactory object. This object has a mktemp() function that returns Path
objects. You can use mktemp() to create multiple temporary directories.


```python3
def test_tmp_path(tmp_path):
    file = tmp_path / "file.txt"
    print(tmp_path)
    file.write_text("Hello")
    assert file.read_text() == "Hello"


def test_tmp_path_factory(tmp_path_factory):

    path = tmp_path_factory.mktemp("sub")
    file = path / "file.txt"
    file.write_text("Hello")
    assert file.read_text() == "Hello"
```

Their usage is almost identical except for the following:
- With `tmp_path_factory` , you have to call mktemp() to get a directory.
- `tmp_path_factory` is session scope.
- `tmp_path` is function scope.

In the previous chapter, we used the standard library
`tempﬁle.TemporaryDirectory` for our db fixture:
let's refactor it with pytest builtin `fixture`
```python3
import pytest
import cards

@pytest.fixture(scope="session")
def db(tmp_path_factory):
    """CardsDB object connected to a temporary database"""
    db_path = tmp_path_factory.mktemp("cards_db")
    db_ = cards.CardsDB(db_path)
    yield db_
    db_.close()
```

# Using capsys

Sometimes the application code is supposed to output something to stdout ,
stderr , and so on. As it happens, the Cards sample project has a command-
line interface that should be tested.

The command, `cards version` , is supposed to output the version:
```sh
cards version
1.0.0
```
The version is also available from the API:
```python
$ python -i
>>> import cards
>>> cards.__version__
'1.0.0'

```
One way to test this would be to actually run the command with
`subprocess.run() `, grab the output, and compare it to the version from the API:
```python3
import subprocess
import cards

def test_version_v1():
    process = subprocess.run(
        ["cards", "version"], capture_output=True, text=True
    )
    output = process.stdout.rstrip()
    assert output == cards.__version__
```

The `capsys` fixture enables the capturing of writes to stdout and stderr . We can
call the method that implements this in the CLI directly, and use capsys to
read the output:
```
def test_version_v2(capsys):
    cards.cli.version()
    output = capsys.readouterr().out.rstrip()
    assert output == cards.__version__
```