# location_api.py

import requests

RAPIDAPI_KEY = "66ee36110fmsh97b6a23646d1125p1ee7d7jsn401b2ad1c922"
RAPIDAPI_HOST = "places-nearby-a-coordinates.p.rapidapi.com"

def get_nearby_places(latitude, longitude, category="adventure", radius=10000):
    url = f"https://{RAPIDAPI_HOST}/nearby"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    params = {
        "lat": latitude,
        "lng": longitude,
        "category": category,
        "radius": radius  # radius in meters (10000 = 10km)
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None
