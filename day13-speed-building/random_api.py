import requests
import json
url = "https://randomuser.me/api/"
params = {
    "results": 5,
    "gender" : "female",
    "format": "json"
}
try: 
    r = requests.get(url=url, params=params)

    data = r.json()

    for person in data["results"]:
        print(f"Name:  {person['name']['title'] +'. ' + person['name']['first']+ ' ' +person['name']['last']}"),
        print(f"Age: {person['dob']['age']}\n")
except requests.Timeout :
    print("Request timeout")
except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
except requests.RequestException as e:
    print(f"Network error: {e}")
except json.JSONDecodeError as e:
    print(f"Invalid JSON decode")


