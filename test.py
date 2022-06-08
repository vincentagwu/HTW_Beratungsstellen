#Old
# import requests


# BASE_URL = "http://127.0.0.1:5000/"

# # response = requests.put(BASE_URL + "question/1", {"question": "Wie kann ich mich von Prüfungen abmelden?"})
# # print(response.json())

# #response = requests.get(BASE_URL + "question/1")
# response = requests.get(BASE_URL + "question?q='AAPLV $MA All 3 made nice PEG(Power Earnings Gap) candles on Friday. First brave soldiers to 'go over the top… https://t.co/iloZYVDj0w")
# print(response.json())


# new
# from transformers import AutoTokenizer, AutoModelForSequenceClassification


# tokenizer = AutoTokenizer.from_pretrained("rodrigogelacio/autonlp-department-classification-534915130")

# model = AutoModelForSequenceClassification.from_pretrained("rodrigogelacio/autonlp-department-classification-534915130")
# inputs = tokenizer("Ich bin schwanger, was soll ich tun?", return_tensors="pt")
# outputs = model(**inputs)
# print(outputs)



# from transformers import AutoModelForSequenceClassification, AutoTokenizer

# model = AutoModelForSequenceClassification.from_pretrained("rodrigogelacio/autonlp-department-classification-534915130", use_auth_token= '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')

# tokenizer = AutoTokenizer.from_pretrained("rodrigogelacio/autonlp-department-classification-534915130", use_auth_token= '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')

# inputs = tokenizer("Ich bin schwanger, was soll ich tun?", return_tensors="pt")

# outputs = model(**inputs)
# print(outputs)

import requests

API_URL = "https://api-inference.huggingface.co/models/rodrigogelacio/autonlp-department-classification-534915130"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

output = query({"inputs": "Ich bin schwanger, was soll ich tun?"})
print(output)