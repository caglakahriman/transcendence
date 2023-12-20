import requests
import json

url = "http://159.89.0.237:8100/api/user_list/"
headers = {'Content-Type': 'application/json'}
data = {"id":2, "username": "testing", "password": "1234"}

resp = requests.get(url, headers=headers, json=data)
print(resp.status_code)


response = resp.json()
print(json.dumps(response, indent=4, sort_keys=True))