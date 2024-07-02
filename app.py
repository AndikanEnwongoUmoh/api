from flask import Flask, request, jsonify
import requests
from ip2geotools.databases.noncommercial import DbIpCity
import os

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Guest')
    client_ip = request.remote_addr

    try:
        city = fetch_city(client_ip)
    except Exception as e:
        city = "New York"

    try:

        temperature = fetch_temperature(city)
    except Exception as e:
        temperature = 11

    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"

    response = {
        "client_ip": client_ip,
        "location": city,
        "greeting": greeting
    }

    return jsonify(response)

def fetch_city(client_ip):
    # Fetch city based on client IP using ip2geotools
    try:
        response = DbIpCity.get(client_ip, api_key='free')
        return response.city
    except Exception as e:
        raise Exception(f"Error fetching city for IP {client_ip}: {str(e)}")

def fetch_temperature(city):
    # Fetch temperature based on city using OpenWeatherMap API
    try:
        api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        temperature = data['main']['temp']
        return temperature
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching temperature for {city}: {str(e)}")
    except KeyError as e:
        raise Exception(f"Temperature data not found for {city}: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error while fetching temperature for {city}: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
