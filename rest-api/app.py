from flask import Flask, render_template, abort, request, jsonify, render_template, send_file, make_response, flash, redirect, url_for
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import desc
from datetime import datetime, date
from flask_cors import CORS, cross_origin
from pydantic import BaseModel
from typing import Dict
import nltk
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import requests
import os
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.sqlite3'
db = SQLAlchemy(app)

class Ratings(db.Model):
   id = db.Column('id', db.Integer, primary_key = True)
   custom_id = db.Column(db.String(), nullable=False)
   question = db.Column(db.String(255))
   result = db.Column(db.String(255))
   rating = db.Column(db.String(2))  
   date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def get_last_id():

    qry = Ratings.query.order_by(Ratings.id.desc()).first()
    x = qry.id
    ym = date.today().strftime("%y%m")
    q_custom_id = "" + ym + str(x).zfill(3) + ""

    return q_custom_id

def __init__(self, custom_id, question, result, rating):
    self.custom_id = custom_id
    self.question = question
    self.result = result
    self.rating = rating

db.create_all()



IS_DEV = app.env == 'development'

CORS(app)
#migrate = Migrate(app, db)
api = Api(app)


#array =[{"asta": {"Kontakt":{"Öffnungszeiten":"Mo,Di,Do: 07:00 - 15:00 Uhr"}}}, {"bim", {""}}, {"fachschaften", {""}}, {"familienbuero", {""}}, {"frauen_und_gleichstellung", {""}}, {"international_office", {""}}, {"lanadema", {""}}, {"mathecafe", {""}}, {"pruefungsamt", {""}}, {"studienverlaufsberatung", {""}}, {"studieren_mit_behinderung", {""}}, {"studierendensekretariat", {""}}]

API_URL = "https://api-inference.huggingface.co/models/rodrigogelacio/autonlp-department-classification-534915130"
headers = {"Authorization": "Bearer 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"}


# New 
output = {}

def sentiment(sentence):

    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    score = sid.polarity_scores(sentence)['compound']
    if(score>0):
        return "Positive"
    else:
        return "Negative"

def question(sentence):
    translated = GoogleTranslator(source='auto', target='de').translate(sentence)
    print("translated: " + translated)
    output = query({"inputs": translated})
    print(output)
    
    return output

def addRating(question, result, rating):
    output = queryRating({"question": question, "result": result, "rating": rating})
    print(output)
    
    return output


def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def queryRating(payload):
	response = requests.post("http://127.0.0.1:5000/newRating", headers=headers, json=payload)
	return response.json()

def postRating(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

@app.route("/question", methods = ["GET","POST"])
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


def json_response(payload, status=200):
 return (json.dumps(payload), status, {'content-type': 'application/json'})

@app.route("/rating")
def show_all():
    return render_template('show_all.html', ratings = Ratings.query.all() )


@app.route('/new', methods = ['GET', 'POST'])
@cross_origin()
def new():

    try:
        get_id = Ratings.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            custom_id = "" + y + str(x).zfill(3) + ""
    except:
        custom_id = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            if not request.form['question'] or not request.form['rating'] or not request.form['result']:
                flash('Please enter all the fields', 'error')
            else:
                add_rating = Ratings(
                custom_id=custom_id,
                question = request.form['question'],
                result = request.form['result'],
                rating = request.form['rating'])
                db.session.add(add_rating)
                db.session.commit()
                
                flash('Record was successfully added')
                return redirect(url_for('show_all'))
        return render_template('new.html')


@app.route('/newRating', methods = ['GET','POST'])
def newRating():

    #print("TESSSSSSSSSSSSSSSSSSSSST: " + request.data.json)
    try:
        get_id = Ratings.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            custom_id = "" + y + str(x).zfill(3) + ""
    except:
        custom_id = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
       
        if request.method == 'POST':
            content = request.data
            data =  json.loads(content)

            for i in data:
                print(i['question'])
                question = i['question']
                result = i['result']
                rating = i['rating']
            
            add_rating = Ratings(
                custom_id=custom_id,
                question = question,
                result = result,
                rating = rating
            )
            db.session.add(add_rating)
            db.session.commit()
            return jsonify(message="POST request returned")
            flash('Record was successfully added')
            #return jsonify(add_rating)
            # flash('Record was successfully added')
            return redirect(url_for('show_all'))
        #return render_template('new.html')

@app.route('/')
def home():
    return  render_template('index.html')

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)