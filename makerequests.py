import requests
import json

url_docker = "http://159.89.0.237:8100/friendslist/" #changed slash settings.py

url_local = "http://localhost:8000/auth/"

headers = {
    'Content-Type': 'application/json',
    }


data = {"username": "test4", "password":"test2"}

response = requests.post(url_local, headers=headers, json=data)
print(response.json())
if response.status_code == 200:
    token = response.json().get('key') 
    auth_test = requests.get("http://localhost:8000/authtest/", headers={"Content-Type": "application/json",'Authorization': f'Token {token}'}, json={"test4": "test2"})
    print(auth_test.json())

#759b464b0e214eadb999fa21b222c82e24cac365