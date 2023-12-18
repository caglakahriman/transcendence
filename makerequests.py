import requests

url = "http://localhost:8000/api/users/"
headers = {'Content-Type': 'application/json'}
data = {"username": "test", "password": "hm"}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
print(response.json())