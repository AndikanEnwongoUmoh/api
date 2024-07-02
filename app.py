from flask import Flask, request, jsonify
import requests
from ip2geotools.databases.noncommercial import DbIpCity
import os

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Mark')
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
    try:
        response = DbIpCity.get(client_ip, api_key='free')
        city = response.city
        if city is None:
            raise ValueError("City not found")
        return city
    except Exception as e:
        print(f"Error fetching city for IP {client_ip}: {str(e)}")
        return "New York"  # Default city if fetching fails

def fetch_temperature(city):
    try:
        api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temperature = data['main']['temp']
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"Error fetching temperature for {city}: {str(e)}")
        raise Exception(f"Error fetching temperature for {city}: {str(e)}")
    except KeyError as e:
        print(f"Temperature data not found for {city}: {str(e)}")
        raise Exception(f"Temperature data not found for {city}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error while fetching temperature for {city}: {str(e)}")
        raise Exception(f"Unexpected error while fetching temperature for {city}: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
