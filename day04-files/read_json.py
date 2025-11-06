import json

with open('data.json' , 'r') as f:
    file=json.load(f)
    print(file)