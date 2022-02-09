from flask import Flask, render_template, abort, request, jsonify, render_template, send_file, make_response
from flask_restful import Api, Resource, abort, reqparse
from flask_cors import CORS, cross_origin
from pydantic import BaseModel
from typing import Dict
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import requests
#import translators as ts
#from googletrans import Translator
from deep_translator import (GoogleTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             DeepL,
                             QCRI,
                             single_detection,
                             batch_detection)



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)



logging.basicConfig(filename="hello.log", level=logging.INFO)

#array =[{"asta": {"Kontakt":{"Öffnungszeiten":"Mo,Di,Do: 07:00 - 15:00 Uhr"}}}, {"bim", {""}}, {"fachschaften", {""}}, {"familienbuero", {""}}, {"frauen_und_gleichstellung", {""}}, {"international_office", {""}}, {"lanadema", {""}}, {"mathecafe", {""}}, {"pruefungsamt", {""}}, {"studienverlaufsberatung", {""}}, {"studieren_mit_behinderung", {""}}, {"studierendensekretariat", {""}}]

API_URL = "https://api-inference.huggingface.co/models/rodrigogelacio/autonlp-department-classification-534915130"
headers = {"Authorization": "Bearer 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"}


# New 
output = {}

def sentiment(sentence):

    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    score = sid.polarity_scores(sentence)['compound']
    logging.debug('Debuggggggg' + str(score))  # will not print anything
    if(score>0):
        return "Positive"
    else:
        return "Negative"

def question(sentence):
    translated = GoogleTranslator(source='auto', target='de').translate(sentence)
    print("translated: " + translated)
    output = query({"inputs": translated})
    print(output)
    
    logging.debug('Debuggggggg' + str(output))  # will not print anything
    return output

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


@app.route("/question", methods = ["GET","POST"])
@cross_origin()
def sentimentRequest():
    if request.method == "POST":
        sentence = request.form['q']
        sent = question(sentence)
        output['answers'] = sent
        return jsonify(output)
    else:
        sentence = request.args.get('q')
        sent = question(sentence)
        output['answers'] = sent
        return jsonify(output)

@app.route('/')
@cross_origin()
def index():
    try:
        return  send_file('index.html')
    except Exception as e:
        logging.info(e.args[0])

if __name__ == "__main__":
    app.run(debug=True)