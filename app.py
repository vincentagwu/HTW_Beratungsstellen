from flask import Flask, render_template, abort, request, jsonify, render_template, send_file, make_response, flash, redirect, url_for
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
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
import logging
from datetime import datetime
from deep_translator import (GoogleTranslator)
import torch


app = Flask(__name__)
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#logging.basicConfig(filename=datetime.now().strftime('logs/logfile_%H_%M_%d_%m_%Y.log'), level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.sqlite3'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/htw_beratungsstelle_api/ratings.sqlite3'
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
api = Api(app)

API_URL = "https://api-inference.huggingface.co/models/rodrigogelacio/autonlp-department-classification-534915130"
headers = {"Authorization": "Bearer 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"}


# New 
output = {}

def question(sentence):
    # Translate and fetch model prediction
    translated = GoogleTranslator(source='auto', target='de').translate(sentence)
    print("translated:", translated)
    
    # Use model and tokenizer for classification
    tokenizer = AutoTokenizer.from_pretrained("rodrigogelacio/autonlp-department-classification-534915130")
    model = AutoModelForSequenceClassification.from_pretrained("rodrigogelacio/autonlp-department-classification-534915130")
    
    inputs = tokenizer(translated, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    print(f"Predicted class: {predicted_class}")
    
    # Structure output
    # model_output = query({"inputs": translated})
    # output = {"model_output": model_output, "predicted_class": predicted_class}
    # print("Output:", json.dumps(output))
    
    return predicted_class

def addRating(question, result, rating):
    #app.logger.info('Add rating')
    output = queryRating({"question": question, "result": result, "rating": rating})
    #app.logger.info('question: ' + question + ', result: ' + result + ', rating: ' + rating)
    print(output)
    logging.info('New rating: ' + output)
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
        logging.info('Successfully requested question - question: ' + sentence )
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
        x = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            custom_id = "" + y + str(x).zfill(3) + ""
    except:
        custom_id = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            if not request.form['question'] or not request.form['rating'] or not request.form['result']:
                logging.error('Entered not all needed fields for rating - question: ' + request.form['question'] + ', result: ' + request.form['result'] + ', rating: ' + request.form['rating'])
                flash('Please enter all the fields', 'error')
            else:
                add_rating = Ratings(
                custom_id=custom_id,
                question = request.form['question'],
                result = request.form['result'],
                rating = request.form['rating'])
                db.session.add(add_rating)
                db.session.commit()
                logging.info('Successfully added rating - question: ' + request.form['question'] + ', result: ' + request.form['result'] + ', rating: ' + request.form['rating'])
                flash('Record was successfully added')
                return redirect(url_for('show_all'))
        return render_template('new.html')


@app.route('/newRating', methods = ['GET','POST'])
def newRating():
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
            logging.info('Added new rating: ' + 'custom_id: ' + custom_id + 'question: ' + question + 'result: ' + result + 'rating: ' + rating)
            return jsonify(message="POST request returned")
            flash('Record was successfully added')
            return redirect(url_for('show_all'))

@app.route('/')
def home():
    logging.info('Back at homescreen of the HTW-Beratungsstellen-API')
    return  render_template('index.html')

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
    logging.info('Flask-API started: Started HTW-Beratungsstellen-API')