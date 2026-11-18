#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "No .venv yet, run ./first_setup.sh once first"
    exit 1
fi

export PATH="$PWD/.venv/bin:$PATH"

echo "Security check (bandit)"
bandit --recursive locust_files locustfile.py --ini .bandit --quiet

echo "Format check (black)"
black --check locust_files locustfile.py

echo "Lint check (pylint)"
pylint --rcfile=.pylintrc locust_files locustfile.py
