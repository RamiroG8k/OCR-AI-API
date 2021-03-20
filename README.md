# OCR handwriting detection

## Begin with 🚀

_Install required packages before run any of the available scripts._

Using the python default package manager

### Pre-requisites 📋

_Tensorflow, Open CV and Imutils_

```
pip install tensorflow
pip install imutils
pip install opencv-python
```

## Testing with loaded model ⚙️

_To begin with, there are two initial required arguments, the model path and the image path_

```
python ocr_handwriting.py --model handwriting.model --image images/umbc_address.png
```
## Training model 🖇️

_To begin with, there are two initial required arguments, the model path and the training data(csv)_

```
python train_ocr_model.py --az a_z_handwritten_data.csv --model handwriting.model
```
