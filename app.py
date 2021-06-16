from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.message import insert
from ocr_handwriting import analyze
import requests
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://root:rootEdpPassword@edp-cluster.v8edx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["edp"]
collectionUsers = db["tokens"]
collectionPhrase = db["phrase"]
collectionUser = db["user"]
collectionPredictions = db["metric_data"]
collectionMetric = db["metric"]


app = Flask(__name__)
CORS(app)

# TODO
# debe de retornar en el reponse la actividad para mejorar la calidad de esa letra.
@app.route('/image', methods=['POST'])
def image():
    token = request.headers.get('Authorization')
    # Expected phrase
    phraseId = request.form.get('phraseId')
    phrase = getPhrase(phraseId)
    # User
    userId = request.form.get('userId')
    user = getUser(userId)
    
    if(not isValidToken(token)):
        return ('Unauthorized user'), 401
    elif(phrase == None):
        return ('Phrase not found'), 404
    elif(user == None):
        return ('User not found'), 404
    else:
        # Store image, name and save it to local storage
        file = request.files['image']
        filename = file.filename
        file.save('./' + filename)
        sentence = phrase["data"]
        # Main algorithm, Analize image characters
        preds = analyze(filename, sentence)
        

        # Calculates general rate
        average = sum(p['rate'] for p in preds) / len(preds)

        #Save metric_data and metric in mongo
        metric_dataArrray = saveMetricData(preds)
        saveMetric(metric_dataArrray,user, phrase, average)

        # Gets the chars to improve in
        c_list = []
        c_list.append([c['letter'] for c in preds if c['rate'] < 70])

        # Response
        return jsonify({
            "status": "ok",
            "predictions": preds,
            "chars": len(preds),
            "gral_rate": average,
            "to_improve": c_list,
        })
    
        

def isValidToken(token):
    response = requests.post("https://edp-api.herokuapp.com/auth/validate-token", headers={'Authorization': token})
    if(response.status_code == 200):
        return True
    return False

def getUser(userId):
    return collectionUser.find_one({"_id" : ObjectId(userId)})

def getPhrase(phraseId):
    return collectionPhrase.find_one({ "_id":  ObjectId(phraseId)})
    
def saveMetricData(predictions):
    insertedPredictions = []
    for prediction in predictions:
        metric_data = {"letter":prediction["letter"],"average":prediction["predicted"]}
        insertedPredictions.append(collectionPredictions.insert_one(metric_data).inserted_id)
    return insertedPredictions

def saveMetric(metricDataArray, user, phrase, generalAverage):
    metric = {"date":datetime.today(),"phrase": phrase["_id"], "user_id":user["_id"],"general_average":generalAverage, "metrics_data":metricDataArray}
    metricSaved = collectionMetric.insert_one(metric).inserted_id
    return metricSaved

if __name__ == '__main__':
    app.run(debug=True, port=8080)
