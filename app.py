from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Set your API keys here
os.environ['IPGEOLOCATION_API_KEY'] = '5891dbc2678a42d89147271e902ac802'
os.environ['OPENWEATHERMAP_API_KEY'] = '82b6601fa9a99176b3c29f354114207b'

# Function to fetch public IP address
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip = response.json().get('ip')
        return ip
    except requests.exceptions.RequestException as e:
        print(f"Error fetching public IP address: {str(e)}")
        return None

# Function to fetch IP geolocation using ipgeolocation.io
def fetch_geolocation(client_ip):
    try:
        api_key = os.getenv('IPGEOLOCATION_API_KEY')
        url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={client_ip}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        lat = data.get('latitude')
        lon = data.get('longitude')
        city = data.get('city', 'Unknown')
        return lat, lon, city
    except requests.exceptions.RequestException as e:
        print(f"Error fetching geolocation for IP {client_ip}: {str(e)}")
        return None, None, 'Unknown'

# Function to fetch temperature based on coordinates using Open-Meteo API
def fetch_temperature(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temperature = data['current_weather']['temperature']
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"Error fetching temperature for coordinates {lat}, {lon}: {str(e)}")
        return 'Unknown'
    except KeyError as e:
        print(f"Temperature data not found for coordinates {lat}, {lon}: {str(e)}")
        return 'Unknown'

# Route to handle API requests
@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Unknown')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # If the IP is a private IP, use the public IP instead
    if client_ip.startswith('192.168.') or client_ip.startswith('10.') or client_ip.startswith('172.'):
        client_ip = get_public_ip()

    # Fetch geolocation based on IP
    lat, lon, city = fetch_geolocation(client_ip)

    if lat and lon:
        # Fetch temperature based on coordinates
        temperature = fetch_temperature(lat, lon)

        greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"
        location = city
    else:
        greeting = f"Hello, {visitor_name}!, unable to determine location."
        location = "Unknown"

    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": greeting
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)