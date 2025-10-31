#!/usr/bin/env bash
set -e
PORT=${PORT:-8501}
exec streamlit run home.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
