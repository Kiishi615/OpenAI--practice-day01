import requests
import json
url = "https://opentdb.com/api.php"
params = {
    "amount": 10,
    "difficulty" : "medium",
    "type": "multiple"
}

r = requests.get(url=url, params=params)

data = r.json()


for trivia in data["results"]:
    print(f"{trivia["question"]}")
    print(f"{trivia["correct_answer"]}\n")

