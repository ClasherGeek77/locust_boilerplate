#!/bin/bash
cd "$(dirname "$0")"

# the lean defaults, safe on a small laptop: 5 users, 1 spawn per second, 30 seconds,
# headless, csv summary into load/. raise them here or pass your own args
USERS=${USERS:-5}
SPAWN=${SPAWN:-1}
TIME=${TIME:-30s}
HOST_URL=${HOST_URL:-http://localhost:40000}

if [ ! -d .venv ]; then
    echo "No .venv yet, run ./first_setup.sh once first"
    exit 1
fi

# the target: the reqresin clone. normally it is up; if the port is dark,
# start it here the same way the test suites do, and leave it running
# (a load test should not stop the thing it loads)
if ! curl -s -m 2 "$HOST_URL/api" > /dev/null; then
    echo "starting the reqresin clone for the load run"
    (cd ../reqresin_clone && nohup python3 server.py \
        >> "${TMPDIR:-/tmp}/reqresin_clone.log" 2>&1 &)
    sleep 2
    curl -s -m 2 "$HOST_URL/api" > /dev/null || {
        echo "clone did not come up on $HOST_URL"
        exit 1
    }
fi

mkdir -p load
echo "load run: $USERS users, $SPAWN/s, $TIME against $HOST_URL"
.venv/bin/python -m locust -f locustfile.py --headless \
    -u "$USERS" -r "$SPAWN" -t "$TIME" \
    --csv load/run --host "$HOST_URL" "$@"

echo
# green means: the failures csv has only its header line
FAIL_ROWS=$(tail -n +2 load/run_failures.csv 2>/dev/null | grep -c . || true)
if [ "${FAIL_ROWS:-1}" -gt 0 ]; then
    echo "FAILURES FOUND:"
    cat load/run_failures.csv
    exit 1
fi
echo "GREEN: no failed requests"
