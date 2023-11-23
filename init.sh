#!/bin/sh
python3 project/manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "Error: makemigrations failed"
    exit 1
else
    python3 project/manage.py migrate
    echo "Ayağa kalkıyorue"
    python3 project/manage.py runserver 0.0.0.0:8000
fi