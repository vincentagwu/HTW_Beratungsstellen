from flask import Flask, render_template, abort, request, jsonify, render_template, send_file
from flask_restful import Api, Resource, abort, reqparse
from pydantic import BaseModel
from typing import Dict
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging


app = Flask(__name__)
api = Api(app)

# Old 
class SentimentRequest(BaseModel):
    text: str
class SentimentResponse(BaseModel):
    probabilities: Dict[str, float]
    sentiment: str
    confidence: float

mlmodel_put_args = reqparse.RequestParser()
mlmodel_put_args.add_argument("question", type=str, help="Wie lautet ihre Frage?", required=True)

questions= {}

def question_not_exist(question_id):
    if question_id not in questions:
        abort(404, message="Fragen konnte nicht beantwortet werden!")

def question_exist(question_id):
    if question_id in questions:
        abort(404, message="Fragen existiert schon !")

class MLModel(Resource):
    def get(self, question_id):
        question_not_exist(question_id)
        return questions[question_id]

    def put(self, question_id):
        question_exist(question_id)
        args = mlmodel_put_args.parse_args()
        questions[question_id]= args
        return questions[question_id], 201 

    def delete(self, question_id):
        question_not_exist(question_id)
        args = mlmodel_put_args.parse_args()
        questions[question_id]= args
        return '', 204 


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

# Old
api.add_resource(MLModel, "/question/<int:question_id>")
#api.add_resource(HelloWorld, "/helloworld")


@app.route('/', methods=['GET'])
@app.route('/question/<int:question_id>', methods=['GET'])
@app.route('/question/<int:question_id>', methods=['PUT'])



#New 
@app.route("/", methods = ["GET","POST"])
def sentimentRequest():
    if request.method == "POST":
        sentence = request.form['q']
        sent = sentiment(sentence)
        output['sentiment'] = sent
        return jsonify(output)
    else:
        sentence = request.args.get('q')
        sent = sentiment(sentence)
        print(sentence)
        output['sentiment'] = sent
        return jsonify(output)

# Old

def index():
    try:
        return  send_file('index.html')
    except Exception as e:
        logging.info(e.args[0])
if __name__ == "__main__":
    app.run(debug=True)



# import config
# import torch
# import flask
# import time
# from flask import Flask
# from flask import request
# from model import BERTBaseUncased
# import functools
# import torch.nn as nn


# app = Flask(__name__)

# MODEL = None
# DEVICE = config.DEVICE
# PREDICTION_DICT = dict()


# def sentence_prediction(sentence):
#     tokenizer = config.TOKENIZER
#     max_len = config.MAX_LEN
#     review = str(sentence)
#     review = " ".join(review.split())

#     inputs = tokenizer.encode_plus(
#         review, None, add_special_tokens=True, max_length=max_len
#     )

#     ids = inputs["input_ids"]
#     mask = inputs["attention_mask"]
#     token_type_ids = inputs["token_type_ids"]

#     padding_length = max_len - len(ids)
#     ids = ids + ([0] * padding_length)
#     mask = mask + ([0] * padding_length)
#     token_type_ids = token_type_ids + ([0] * padding_length)

#     ids = torch.tensor(ids, dtype=torch.long).unsqueeze(0)
#     mask = torch.tensor(mask, dtype=torch.long).unsqueeze(0)
#     token_type_ids = torch.tensor(token_type_ids, dtype=torch.long).unsqueeze(0)

#     ids = ids.to(DEVICE, dtype=torch.long)
#     token_type_ids = token_type_ids.to(DEVICE, dtype=torch.long)
#     mask = mask.to(DEVICE, dtype=torch.long)

#     outputs = MODEL(ids=ids, mask=mask, token_type_ids=token_type_ids)

#     outputs = torch.sigmoid(outputs).cpu().detach().numpy()
#     return outputs[0][0]


# @app.route("/predict")
# def predict():
#     sentence = request.args.get("sentence")
#     start_time = time.time()
#     positive_prediction = sentence_prediction(sentence)
#     negative_prediction = 1 - positive_prediction
#     response = {}
#     response["response"] = {
#         "positive": str(positive_prediction),
#         "negative": str(negative_prediction),
#         "sentence": str(sentence),
#         "time_taken": str(time.time() - start_time),
#     }
#     return flask.jsonify(response)


# if __name__ == "__main__":
#     MODEL = BERTBaseUncased()
#     MODEL.load_state_dict(torch.load(config.MODEL_PATH))
#     MODEL.to(DEVICE)
#     MODEL.eval()
#     app.run(host="0.0.0.0", port="9999")