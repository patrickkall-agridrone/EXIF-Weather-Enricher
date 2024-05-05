# EXIF Weather Enricher

This Python script enriches the EXIF metadata of images with weather information based on the GPS coordinates found in the EXIF data. It uses the Azure Maps Weather Service to fetch the current weather conditions and embeds them into the EXIF data of the images.

## Features
- Extracts GPS coordinates from image EXIF data.
- Fetches current weather conditions from the Azure Maps Weather Service.
- Enriches the EXIF metadata with weather data:
  - Temperature (°C)
  - Humidity (%)
  - UV Index
  - Weather Phrase (e.g., Cloudy, Sunny)
  - Pressure (hPa)

## Requirements
- Python 3.x
- The following Python packages:
  - `Pillow`: to manipulate image files and EXIF metadata.
  - `requests`: to make HTTP requests to the Azure Maps API.

## Installation
1. Clone or download this repository.
2. Install the required Python packages:
   ```bash
   pip install Pillow requests
