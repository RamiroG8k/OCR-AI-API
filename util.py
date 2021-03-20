from imutils.contours import sort_contours
import numpy as np
import imutils
import cv2

OUTPUT = "output.jpg"

def getContours(edged):
    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    # Sort the resulting contours from left-to-right
    contours = sort_contours(contours, method="left-to-right")[0]

    return contours

def getPredictions(image, preds, boxes):    
    # Define the list of label names
    labelNames = split("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    array = []
    # Loop over the predictions and bounding box locations together
    for (pred, (x, y, w, h)) in zip(preds, boxes):
        # Find the index of the label with the largest corresponding probability
        i = np.argmax(pred)
        # Extract the probability and label
        prob = pred[i]
        label = labelNames[i]
        predicted = round((prob * 100), 2)
        array.append({'letter': label, 'predicted': predicted, 'rate': predicted})

        # Draw the prediction on the image
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, label, (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    return image, array

def getCharacters(gray, cts):
    array = []

    # Loop over the contours
    for c in cts:
        # Compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)

        # Filter out bounding boxes
        # Ensuring they are neither too small nor too large
        if (w >= 5 and w <= 150) and (h >= 15 and h <= 120):
            # Extract the character and threshold it to make the character
            # appear as *white* (foreground) on a *black* background, then
            # grab the width and height of the thresholded image
            roi = gray[y:y + h, x:x + w]
            thresh = cv2.threshold(
                roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            (tH, tW) = thresh.shape

            # If the width is greater than the height, resize along the
            # width dimension
            if tW > tH:
                thresh = imutils.resize(thresh, width=32)

            # Otherwise, resize along the height
            else:
                thresh = imutils.resize(thresh, height=32)

            # re-grab the image dimensions (now that its been resized)
            # and then determine how much we need to pad the width and
            # height such that our image will be 32x32
            (tH, tW) = thresh.shape
            dX = int(max(0, 32 - tW) / 2.0)
            dY = int(max(0, 32 - tH) / 2.0)

            # Pad the image and force 32x32 dimensions
            padded = cv2.copyMakeBorder(thresh, top=dY, bottom=dY,
                                        left=dX, right=dX, borderType=cv2.BORDER_CONSTANT,
                                        value=(0, 0, 0))
            padded = cv2.resize(padded, (32, 32))

            # Prepare the padded image for classification via our
            # Handwriting OCR model
            padded = padded.astype("float32") / 255.0
            padded = np.expand_dims(padded, axis=-1)

            # Update our list of characters that will be OCR'd
            array.append((padded, (x, y, w, h)))
    
    # Extract the bounding box locations and padded characters
    boxes = [e[1] for e in array]
    
    array = np.array([e[0] for e in array], dtype="float32")
    return array, boxes


def optimize(filename):
    im = cv2.imread(filename)
    # smooth the image with alternative closing and opening
    # with an enlarging kernel
    morph = im.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

    # take morphological gradient
    # gradient_image = cv2.morphologyEx(morph, cv2.MORPH_GRADIENT, kernel)
    # split the gradient image into channels
    image_channels = np.split(np.asarray(morph), 3, axis=2)
    channel_height, channel_width, _ = image_channels[0].shape
    

    # apply Otsu threshold to each channel
    for i in range(0, 3):
        _, image_channels[i] = cv2.threshold(
            image_channels[i], 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
        image_channels[i] = np.reshape(
            image_channels[i], newshape=(channel_height, channel_width, 1))

    # merge the channels
    image_channels = np.concatenate(
        (image_channels[0], image_channels[1], image_channels[2]), axis=2)

    # save the denoised image
    cv2.imwrite(OUTPUT, image_channels)
    return cv2.imread(OUTPUT)

def split(word):
    return [char for char in word] 