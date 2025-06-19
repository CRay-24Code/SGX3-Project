import requests

try:
    response = requests.get("http://35.206.76.195:8031/head?count=10")

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
