#!/bin/bash

# Set environment variables
export PORT=8080
export IPGEOLOCATION_API_KEY=5891dbc2678a42d89147271e902ac802


# Run Gunicorn server
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4

