#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
python3 -m pip install -r requirements.txt
python3 check_setup.py
python3 -m streamlit run ui/app.py
