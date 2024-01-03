import requests
import json

url_docker = "http://159.89.0.237:8100/register/" #changed slash settings.py

url_local = "http://localhost:8000/login/"

headers = {'Content-Type': 'application/json',}

data = {"username": "user", "password":"123"}

resp = requests.get(url_docker, headers=headers, json=data)
print(resp.status_code)


try:
    response = resp.json()
    print(json.dumps(response, indent=4, sort_keys=True))
except:
    response = resp.text