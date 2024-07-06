#!/bin/bash

# Set environment variables
export PORT=8080
os.environ['IPGEOLOCATION_API_KEY'] = '5891dbc2678a42d89147271e902ac802'
os.environ['OPENWEATHERMAP_API_KEY'] = '82b6601fa9a99176b3c29f354114207b'

# Run Gunicorn server
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
