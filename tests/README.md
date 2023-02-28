# Run the unit tests

```sh
$ git clone https://github.com/angely-dev/diffplus.git
$ cd diffplus/
$ python -m unittest tests/test.py
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

For measuring code coverage:

```sh
$ coverage run -m unittest tests/test.py 
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK

$ coverage report
Name                           Stmts   Miss  Cover
--------------------------------------------------
diffplus/__init__.py               2      0   100%
diffplus/incremental_diff.py      32      0   100%
diffplus/indented_config.py       37      0   100%
tests/expected.py                  8      0   100%
tests/test.py                     26      0   100%
--------------------------------------------------
TOTAL                            105      0   100%
```
