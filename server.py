from io import BytesIO

from flask import Flask, jsonify, request, redirect, url_for
from PIL import Image
import cv2
import requests
import numpy
import os
import pandas as pd
from werkzeug.utils import secure_filename

#from Classification.classification import classify
from Treatment.sift import sift_descriptor
from Treatment.sift import predict_class
from Treatment.sift import predict_bof
from Treatment.sift import bof_train_extract_features
from Treatment.sift import bof_model_descriptor

##CONSTANTS pour le redimmensionnement par défaut des images
HEIGHT = 100
WIDTH = 100
############
detect, bow_extract = bof_train_extract_features()
print("DOOOOOOOOOOOOOONNNNNNNNNNNNNNEEEEEEEEEEEE")
#train = bof_model_descriptor(detect,bow_extract)

def setter(d, b):
    detect = d
    bow_extract = b

UPLOAD_FOLDER = './Image/BD_test/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
#train = pd.read_csv('descriptor_bof.csv')
train = pd.read_json('descriptor_bof.json')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Route vers la documentation
@app.route('/')
def index():
    payload = {
        'confiance': 0.8,
        'tag': 'meuble'
    }
    return jsonify(payload)

@app.route('/train/')
def train_data():
    detect, bow_extract = bof_train_extract_features()
    train = bof_model_descriptor(detect,bow_extract)
    setter(detect, bow_extract)
    payload = {"size" : detect.descriptorSize() , "vocabulary" : bow_extract.descriptorSize()}
    return jsonify(payload)

#Entrée en url: <adresse ip>:5000/classify/url_de_l'image_en_question
#Route pour effectuer une classification
#Sortie: Liste de catégorie ordonnée du plus probable au moin probable
@app.route('/classify/<path:url>')
def classifier_image(url):
    response = requests.get(url)
    payload = {
        'url': url
    }
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img = numpy.array(img)
        prediction = predict_class(img,0.8)
        result = { 'prediction': prediction }
        #payload = { **payload , **image_descriptor }
    return jsonify(prediction)
@app.route('/classify2/<path:url>')
def classifier_image2(url):
    response = requests.get(url)
    payload = {
        'url': url
    }
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img = numpy.array(img)
        img = cv2.resize(img, (WIDTH,HEIGHT), interpolation = cv2.INTER_AREA)
        prediction = predict_bof(img,train,detect,bow_extract)
        result = { 'prediction': prediction }
        #payload = { **payload , **image_descriptor }
    return jsonify(prediction)
@app.route('/classify/',methods=['POST'])
def classifier_image_bytes():
    #print(request.headers)
    #print(request.content)
    print(request.status_code)
    if request.method == 'POST':
        img = Image.open(BytesIO(response.content))
        img = numpy.array(img)
        prediction = predict_class(img,0.8)
        result = { 'prediction': prediction }

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/check/')
def check():
    payload = {"size" : detect.descriptorSize() , "vocabulary" : bow_extract.descriptorSize()}
    return jsonify(bow_extract.getVocabulary().tolist())

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('ok')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            prediction = predict_class(img,0.8)
            result = { 'prediction': prediction }
            return jsonify(prediction);
            #payload = { **payload , **image_descriptor }
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
# @app.route('/descriptor')
# def hello():
#     return 'HELLO'
# @app.route('/descriptor/<path:url>')
# def descriptor_image(url):
#     response = requests.get(url)
#     payload = {
#         'url': url
#     }
#     if response.status_code == 200:
#         img = Image.open(BytesIO(response.content))
#         img = numpy.array(img)
#         image_descriptor = sift_descriptor(img)
#         payload = { **payload , **image_descriptor }
#     return jsonify(payload)

if __name__ == '__main__':
    app.run(debug=True)
