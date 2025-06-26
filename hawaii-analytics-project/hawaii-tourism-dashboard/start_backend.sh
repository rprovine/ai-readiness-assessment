#!/bin/bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
../venv/bin/python app.py