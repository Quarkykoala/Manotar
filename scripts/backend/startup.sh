#!/bin/bash
python nltk_setup.py
python -m flask db upgrade
gunicorn app:app
