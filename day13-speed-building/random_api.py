import requests
import json
url = "https://randomuser.me/api/"
params = {
    "results": 5,
    "gender" : "female",
    "format": "json"
}

r = requests.get(url=url, params=params)

print(r.json())

data = r.json()

for person in data["results"]:
    print(f"Name:  {person["name"]["title"] +". " + person["name"]["first"]+ " " +person["name"]["last"]}"),
    print(f"Age: {person["dob"]["age"]}\n")

