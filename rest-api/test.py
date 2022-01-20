import requests

BASE_URL = "http://127.0.0.1:5000/"

# response = requests.put(BASE_URL + "question/1", {"question": "Wie kann ich mich von Prüfungen abmelden?"})
# print(response.json())

response = requests.get(BASE_URL + "question/1")
print(response.json())