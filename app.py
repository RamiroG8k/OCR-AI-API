from flask import Flask, request, jsonify
from ocr_handwriting import analyze
import requests
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://root:rootEdpPassword@edp-cluster.v8edx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["edp"]
collectionUsers = db["tokens"]
collectionPhrase = db["phrase"]
collectionUser = db["user"]


app = Flask(__name__)

# TODO
# - Almacenar la informacion en la base de datos
# - Aquellas letras con rate menor a 70%
# debe de retornar en el reponse la actividad para mejorar la calidad de esa letra.

@app.route('/image', methods=['GET'])
def image():
    token = request.headers.get('Authorization')
    # Expected phrase
    phraseId = request.form.get('phraseid')
    phrase = getPhrase(phraseId);
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
    

if __name__ == '__main__':
    app.run(debug=True, port=8080)
