#!/bin/bash
python -m venv roadscout_env
source roadscout_env/bin/activate
pip install -r requirements.txt --timeout 120
python main.py
