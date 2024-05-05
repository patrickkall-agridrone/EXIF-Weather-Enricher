import os
import sys
from PIL import Image, ExifTags
import requests
from datetime import datetime

# Replace this with your Azure Maps Weather Service subscription key
AZURE_MAPS_API_KEY = 'YOUR_AZURE_MAPS_API_KEY'

def get_gps_coordinates(exif_data):
    if 'GPSInfo' in exif_data:
        gps_info = exif_data['GPSInfo']
        gps_data = {}
        for key, val in ExifTags.GPSTAGS.items():
            if key in gps_info:
                gps_data[val] = gps_info[key]
        lat = gps_data.get('GPSLatitude')
        lat_ref = gps_data.get('GPSLatitudeRef')
        lon = gps_data.get('GPSLongitude')
        lon_ref = gps_data.get('GPSLongitudeRef')
        if lat and lon and lat_ref and lon_ref:
            lat = convert_to_degrees(lat)
            lon = convert_to_degrees(lon)
            if lat_ref != 'N':
                lat = -lat
            if lon_ref != 'E':
                lon = -lon
            return lat, lon
    return None, None

def convert_to_degrees(value):
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(img):
    exif_data = img._getexif()
    if not exif_data:
        return {}
    return {ExifTags.TAGS.get(tag, tag): value for tag, value in exif_data.items()}

def get_datetime_original(exif_data):
    date_str = exif_data.get('DateTimeOriginal')
    if date_str:
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    return None

def get_weather_data(lat, lon):
    # Adjust URL to retrieve current weather data
    url = f'https://atlas.microsoft.com/weather/currentConditions/json?api-version=1.1&query={lat},{lon}&subscription-key={AZURE_MAPS_API_KEY}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Error fetching weather data: {response.status_code} - {response.text}')
        return None
    weather_data = response.json()
    if 'results' in weather_data and len(weather_data['results']) > 0:
        current_weather = weather_data['results'][0]
        return {
            'temperature': current_weather.get('temperature', {}).get('value', 'N/A'),
            'humidity': current_weather.get('relativeHumidity', 'N/A'),
            'uvIndex': current_weather.get('uvIndex', 'N/A'),
            'phrase': current_weather.get('phrase', 'N/A'),
            'pressure': current_weather.get('pressure', {}).get('value', 'N/A')
        }
    print(f'No current weather data found for {lat}, {lon}')
    return None

def enrich_image_exif(image_path, weather_data):
    img = Image.open(image_path)
    exif_dict = img.getexif()

    description = f"Weather: {weather_data.get('phrase', '')}, Temperature: {weather_data.get('temperature', '')} °C, Humidity: {weather_data.get('humidity', '')}%, UV Index: {weather_data.get('uvIndex', '')}, Pressure: {weather_data.get('pressure', '')} hPa"
    exif_dict[270] = description

    print(f"Adding weather data to {image_path}: {description}")

    img.save(image_path, exif=exif_dict.tobytes())
    img.close()

def process_images(folder_path):
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.tiff')):
                file_path = os.path.join(root, filename)
                print(f"Processing {file_path}...")
                img = Image.open(file_path)
                exif_data = get_exif_data(img)
                lat, lon = get_gps_coordinates(exif_data)
                if lat is not None and lon is not None:
                    weather_data = get_weather_data(lat, lon)
                    if weather_data:
                        enrich_image_exif(file_path, weather_data)
                        print(f"Enriched {filename} with weather data")
                    else:
                        print(f"No weather data found for {filename}")
                else:
                    print(f"Missing GPS data for {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
    else:
        folder_path = sys.argv[1]
        process_images(folder_path)
