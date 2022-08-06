import json
import sys
from configparser import ConfigParser
from urllib import error, request
import geopy.distance
from geopy.geocoders import Nominatim
import folium
import webbrowser


BASE_GEOLOCATION_API_URL = "https://api.ipgeolocation.io/ipgeo"
BASE_ISS_API_URL = "https://api.wheretheiss.at/v1/satellites"
URL = 'http://api.open-notify.org/iss-now.json'

# USER INFO
def _get_location_api_key():
    config = ConfigParser()
    config.read("hidden.ini")
    return config["ipgeolocation"]["api_key_geoloc"]


def build_location_query():
    api_key = _get_location_api_key()
    url = f"{BASE_GEOLOCATION_API_URL}?apiKey={api_key}"
    return url


def get_user_location_data(user_query_url):
    try:
        response = request.urlopen(user_query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_user_location_info(user_location_data):
    country = user_location_data["country_name"]
    latitude = user_location_data["latitude"]
    longitude = user_location_data["longitude"]

    print("YOUR LOCATION")
    print(f"Country: {country}")
    print(f"Longitude: {longitude}")
    print(f"Latitude: {latitude}")


# ISS INFO
def build_iss_query():
    iss_id = 25544
    url = f"{BASE_ISS_API_URL}/{iss_id}"
    return url


def get_iss_location_data(iss_query_url):
    try:
        response = request.urlopen(iss_query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_iss_location_info(iss_location_data):
    latitude = str(iss_location_data["latitude"])
    longitude = str(iss_location_data["longitude"])

    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(latitude + "," + longitude)
    try:
        address = location.raw['address']
        country = address.get('country', '')

        print("ISS LOCATION")
        print(f"Country: {country}")
        print(f"Longitude: {longitude}")
        print(f"Latitude: {latitude}")

    except AttributeError:
        print("ISS LOCATION")
        print(f"Longitude: {longitude}")
        print(f"Latitude: {latitude}")
        print("Impossible to detect the country")


def map_show(user_location_data, iss_location_data):
    user_latitude = float(user_location_data["latitude"])
    user_longitude = float(user_location_data["longitude"])
    user_coords = [user_latitude, user_longitude]

    iss_latitude = float(iss_location_data["latitude"])
    iss_longitude = float(iss_location_data["longitude"])
    iss_coords = [iss_latitude, iss_longitude]

    dist_map = folium.Map(location=user_coords, zoom_start=12)
    folium.Marker(location=user_coords, icon=folium.Icon(color='green'), popup='user').add_to(dist_map)
    folium.Marker(location=iss_coords, icon=folium.Icon(color='blue'), popup='iss').add_to(dist_map)

    folium.PolyLine(locations=[user_coords, iss_coords], color='red').add_to(dist_map)

    dist_map.save("map.html")
    webbrowser.open("map.html")

    return

def get_distance(user_location_data, iss_location_data):
    user_latitude = user_location_data["latitude"]
    user_longitude = user_location_data["longitude"]

    user_coords = (user_latitude, user_longitude)

    iss_latitude = iss_location_data["latitude"]
    iss_longitude = iss_location_data["longitude"]

    iss_coords = (iss_latitude, iss_longitude)

    distance = geopy.distance.geodesic(user_coords, iss_coords).km
    distance = str(round(distance, 2))

    print(f"You are {distance} km far from ISS!")
    print(f"")


# USER
user_query_url = build_location_query()
user_location_data = get_user_location_data(user_query_url)
display_user_location_info(user_location_data)
# ISS
iss_query_url = build_iss_query()
iss_location_data = get_iss_location_data(iss_query_url)
display_iss_location_info(iss_location_data)
# INFO
get_distance(user_location_data, iss_location_data)
map_show(user_location_data, iss_location_data)
