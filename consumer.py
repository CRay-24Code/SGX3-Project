import requests

# Parameters for query
lat = 30.2895
lon = -97.7368
year = 2024

try:
    # Make request to /rush_hour_nearby endpoint
    url = "http://35.206.76.195:8031/rush_hour_nearby"
    params = {"lat": lat, "lon": lon, "year": year}
    response = requests.get(url, params=params)

    #Check to see if the requests worked
    print(f"Status Code: {response.status_code}")
    print("Headers:", response.headers)

    #View our JSON data

    data = response.json()
    print ("Response Type:", type(data))
    print ("Response Data:", data)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except ValueError as e:
    print(f"Failed to parse JSON: {e}")
