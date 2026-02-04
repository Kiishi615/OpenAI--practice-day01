import requests
import json
url = "https://opentdb.com/api.php"
params = {
    "amount": 10,
    "difficulty" : "medium",
    "type": "multiple"
}
try:
    r = requests.get(url=url, params=params)
    data = r.json()
    for trivia in data["results"]:
        print(f"{trivia["question"]}")
        print(f"{trivia["correct_answer"]}\n")

except requests.Timeout :
    print("Request timeout")
except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
except requests.RequestException as e:
    print(f"Network error: {e}")
except json.JSONDecodeError as e:
    print(f"Invalid JSON decode")