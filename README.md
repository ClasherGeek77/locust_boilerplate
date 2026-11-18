# locust_boilerplate

A starter for API load tests with Locust: simulated users call a REST API in weighted flows (read, write, auth), every response is checked against its documented status and a body fragment, and the run ends with a one-line verdict. The target is a local clone of the reqres.in API, so you can push it as hard as your machine allows without touching a public service.

## when to use it

Use it to learn how a Locust project is laid out, or as the starting point for your own load test: a `FastHttpUser`, task sets, one shared client wrapper, named stats per intent, CSV output.

Do not use it if:

- you want to check that each API answer is correct, one by one: use https://github.com/ClasherGeek77/pytest_api_boilerplate (Python) or https://github.com/ClasherGeek77/katalon_api_boilerplate (Katalon). This project measures throughput and latency, it is not a functional suite.
- you want a JMeter plan instead of Python: use https://github.com/ClasherGeek77/jmeter_performance_security_testing
- you need a staged ramp (spike, soak shape): not included yet, see "how to read the code"

## what you need

| need | detail |
|---|---|
| Python 3.11 | the minor version in `.python-version` (3.11.14). `first_setup.sh` looks for `python3.11` on your PATH; otherwise `TEST_PYTHON=/path/to/python3.11 ./first_setup.sh`. Download from https://www.python.org/downloads/. |
| `locust` 2.24.0 | installed by `first_setup.sh` from `requirements.pip`, together with black 24.2.0, bandit 1.7.9 and pylint 3.2.7 for `checks.sh` |
| the reqres clone | https://github.com/ClasherGeek77/reqresin_clone, Python 3.8+ standard library only, port 40000 |
| curl | `run_load.sh` uses it to see whether the target is up |
| git | to clone the repos |

Mac and Linux both work for Locust itself. `run_load.sh` can start the clone for you only on macOS (see "if it breaks"); on Linux start the clone yourself first.

## quick start

```bash
git clone https://github.com/ClasherGeek77/reqresin_clone.git
git clone https://github.com/ClasherGeek77/locust_boilerplate.git
cd locust_boilerplate
./first_setup.sh
```

You should see `Creating .venv from python3.11`, then `Setup done, next run ./run_load.sh`. Check the install:

```bash
.venv/bin/locust --version
```

You should see `locust 2.24.0 from .../site-packages/locust (python 3.11.x)`.

Start the target in a second terminal and leave it running:

```bash
cd reqresin_clone
python3 server.py            # http://localhost:40000/api
```

Check it: `curl -s http://localhost:40000/api/users/2` shows JSON with `janet.weaver@reqres.in`.

Run a short load test:

```bash
./run_load.sh                       # 5 users, 1 new user per second, 30 s, headless
USERS=20 TIME=60s ./run_load.sh     # more users, longer
./run_load.sh --only-summary        # any extra argument goes to locust (here: no periodic table)
```

Knobs, by environment variable: `USERS` (default 5), `SPAWN` (new users per second, default 1), `TIME` (default `30s`), `HOST_URL` (default `http://localhost:40000`).

What you should see: Locust prints a statistics table every few seconds, one row per request name (`list users`, `get user`, `get unknown user (404)`, `products`, `unknown colors`, `login`, `login refused (400)`, `register`, `create user`, `update user`, `delete user`, `list users with delay`), then a final table and percentiles, then the last line:

```
GREEN: no failed requests
```

A 10-second run with 2 users against the clone finished with 0 failures and about 5 ms average response time. If any request fails, the script prints `FAILURES FOUND:`, the contents of `load/run_failures.csv`, and exits 1. Green means the failures CSV holds only its header line.

Results are written to `load/run_stats.csv`, `load/run_stats_history.csv`, `load/run_failures.csv` and `load/run_exceptions.csv` (the folder is git-ignored).

The Locust web dashboard instead of headless mode:

```bash
.venv/bin/python -m locust -f locustfile.py --host http://localhost:40000
```

Then open http://localhost:8089.

Code checks (black, bandit, pylint) for this project:

```bash
./checks.sh          # you should see black "5 files would be left unchanged" and pylint 10.00/10
```

## how to read the code

```
locustfile.py             one user class: FastHttpUser, wait 0.2-0.8 s between tasks,
                          flows weighted {UsersReadFlow: 6, UsersWriteFlow: 2, AuthFlow: 2}
locust_files/
  __init__.py             get_locust_base_api(): the one place every task set gets its client wrapper from
  base_api.py             ReqResBaseApi: every call in its own catch_response block; it asserts the
                          documented status and a body fragment, and picks a stats name per intent
  api_users.py            UsersReadFlow (weighted tasks), UsersWriteFlow (sequential: create, update, delete, then a ?delay=1 probe)
  api_auth.py             AuthFlow: login, login without password (expected 400), register
run_load.sh               the headless run, the CSV output and the green/red verdict
first_setup.sh            builds .venv
checks.sh                 bandit, black, pylint
```

A task set line never checks anything itself. The contract check lives in `base_api.py`, at the call, so a changed expectation is edited in one file. `_verdict()` accepts exactly the documented status, which is what makes an intentional 404 or 400 count as a pass instead of polluting the failure table.

Each simulated user picks one flow at spawn, by the 6/2/2 weights, and stays in it: a task set never hands control back (no `interrupt()`), so with only a few users some flows can be absent from the report. In the 2-user run above only the read flow ran. Use at least 10 users, or run longer with more users, to exercise all three.

The target defaults to `http://localhost:40000` in `run_load.sh` (`HOST_URL`) and is passed to Locust with `--host`. To load another server of the same shape, set `HOST_URL`.

FastHttpUser is the lean client (gevent + a faster HTTP client), a good default when the load generator and the target share one machine. The 5-user default demonstrates the harness; it is not a load target. For a real run use 10-20 users for a minute or more and watch the `Max` column grow: the clone is a single-process stdlib Python server, so its latency is an honest signal of how far you can push it.

To add a staged ramp, define a `LoadTestShape` class in `locustfile.py` (Locust's `shape_class`). Not included here.

## if it breaks

| symptom | cause | fix |
|---|---|---|
| `no python 3.11 found` | no `python3.11` on PATH | install it, or `TEST_PYTHON=/path/to/python3.11 ./first_setup.sh` |
| `No .venv yet, run ./first_setup.sh once first` | setup not run | run it |
| `clone did not come up on http://localhost:40000` | `run_load.sh` could not start the clone | start it yourself (`python3 server.py` in `reqresin_clone`) and rerun |
| `run_load.sh` fails on Linux when it tries to start the clone | it starts `../reqresin_clone/server.py` with `/usr/bin/python3` and logs into `~/Library/Logs/`, a macOS folder | start the clone yourself first; the script then skips that step |
| the clone starts only if `reqresin_clone` is next to this repo | the script looks in `../reqresin_clone` | clone both repos into the same parent folder |
| many `FAILURES FOUND` rows with `status 0` or connection errors | the target stopped or is overloaded | restart the clone, lower `USERS` |
| `FAILURES FOUND` with `status 200 is not 201` style messages | you are not loading the reqres clone (another server answers differently) | point `HOST_URL` at the clone |
| some request names never appear in the report | too few users (each user stays in one flow) | raise `USERS`, or run longer |
| `ModuleNotFoundError` for `locust_files` | you started Locust from another folder | run from the repo root |

## next

- the same API checked call by call: https://github.com/ClasherGeek77/pytest_api_boilerplate
- the same API in Katalon: https://github.com/ClasherGeek77/katalon_api_boilerplate
- the target: https://github.com/ClasherGeek77/reqresin_clone
- load and security testing with JMeter: https://github.com/ClasherGeek77/jmeter_performance_security_testing
