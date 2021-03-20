from flask import Flask, request, jsonify
from ocr_handwriting import analyze

app = Flask(__name__)

# TODO
# - Almacenar la informacion en la base de datos
# - Aquellas letras con rate menor a 70%
# debe de retornar en el reponse la actividad para mejorar la calidad de esa letra.

@app.route('/image', methods=['GET'])
def image():
    # Store image, name and save it to local storage
    file = request.files['image']
    filename = file.filename
    file.save('./' + filename)

    # Expected phrase
    sentence = request.form.get('sentence')

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


if __name__ == '__main__':
    app.run(debug=True, port=8080)
