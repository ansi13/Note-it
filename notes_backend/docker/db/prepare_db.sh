#!/bin/sh
set -e

/opt/code/db/start_postgres.sh

echo 'Creating Schema'
flask db init
flask db migrate
flask db upgrade

/opt/code/db/stop_postgres.sh
