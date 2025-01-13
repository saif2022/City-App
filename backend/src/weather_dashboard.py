from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import boto3
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

API_KEY = os.getenv("OPENWEATHER_API_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
S3_CLIENT = boto3.client("s3")

def save_to_s3(city, weather_data, forecast_data):
    """Save weather and forecast data to S3."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_name = f"weather-data/{city}-{timestamp}.json"
    data_to_save = {
        "weather": weather_data,
        "forecast": forecast_data,
        "timestamp": timestamp
    }
    
    try:
        S3_CLIENT.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(data_to_save),
            ContentType="application/json"
        )
        print(f"Data for {city} saved to S3.")
    except Exception as e:
        print(f"Error saving to S3: {e}")

@app.route('/weather', methods=['POST'])
def get_weather():
    """Fetch weather and forecast data for a given city."""
    data = request.get_json()
    city = data.get('city')

    if not city:
        return jsonify({"error": "City name is required"}), 400

    try:
        # Fetch current weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "q": city,
            "appid": API_KEY,
            "units": "imperial"  # Change to "metric" if needed
        }
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Fetch forecast data
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {
            "q": city,
            "appid": API_KEY,
            "units": "imperial"
        }
        forecast_response = requests.get(forecast_url, params=forecast_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Save data to S3
        save_to_s3(city, weather_data, forecast_data)

        # Send response to frontend
        return jsonify({
            "weather": weather_data,
            "forecast": forecast_data
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
