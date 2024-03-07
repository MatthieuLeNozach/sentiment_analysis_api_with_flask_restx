#!/bin/bash

DB_FILE="instance/db.sqlite3"

if [ ! -f $DB_FILE ]; then
    python /app/bin/initialize.py
fi



CREATOR_EXISTS=$(sqlite3 $DB_FILE "SELECT username FROM users WHERE username='creator';")

if [ -z "$CREATOR_EXISTS" ]; then
    python /app/bin/confidential/add_creator.py
fi


flask run --host 0.0.0.0