# Python Packages
from util import *
from tensorflow.keras.models import load_model
import cv2
import os

OUTPUT = "output.jpg"

def analyze(filename, sentence):
    # Load the handwriting OCR model
    print("[INFO] loading handwriting OCR model...")
    model = load_model('handwriting.model')

    # Load the input image from disk
    print("[INFO] loading image...")
    # image = cv2.imread(image) # PNG
    image = optimize(filename) #JPEG

    # Perform image to grayscale, blur(reduce the noise), and edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 150)

    # Find contours in the edge map
    contours = getContours(edged)

    # Initialize the list of contour bounding boxes and associated
    # Characters that will be OCR'ing
    chars, boxes = getCharacters(gray, contours)

    # OCR the characters using our handwriting recognition model
    preds = model.predict(chars)

    # Get predictions and new image
    image, predictions = getPredictions(image, preds, boxes)

    # Show the final image
    # cv2.imshow("Image prediction", image)
    # cv2.waitKey(0)

    # Remove image in local, Raw imread | Optimize imread 
    os.remove(filename)
    os.remove(OUTPUT)

    # Splits in chars the expected sentence
    expected = split(sentence)

    # Evaluates if prediction is above 70% expected char
    # Otherwise assigns the expected char and rates to 0 the prediction
    for i in range(len(expected)):
        if expected[i] != predictions[i]['letter'] or predictions[i]['rate'] < 70:
            predictions[i]['letter'] = expected[i]
            predictions[i]['rate'] = 0

    # Array of objects with expected char and rate
    return predictions
