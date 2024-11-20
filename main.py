from fileinput import filename 
from flask import *  
from werkzeug.utils import secure_filename
import os
import base64
import requests

import pytesseract
from PIL import Image
import re

app = Flask(__name__) 

UPLOAD_PATH = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

def extract_nutritional_facts(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    API_URL = "https://vision.googleapis.com/v1/images:annotate"
    API_KEY = ""  # Replace with your API key

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "requests": [
            {
                "image": {
                    "content": encoded_string  # Replace this with your base64 encoded image
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION"
                    }
                ]
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, params={"key": API_KEY}, json=data)

    text = response.json()['responses'][0]['textAnnotations'][0]['description']

    patterns = {
        'Calories': r'Calories\s+(\d+)',
        'Total Fat': r'Total Fat\s+(\d+g)',
        'Sodium': r'Sodium\s+(\d+mg)',
        'Total Carbohydrate': r'Total Carbohydrate\s+(\d+g)',
        'Protein': r'Protein\s+(\d+g)'
    }
    
    nutrition_facts = {}

    for nutrient, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            nutrition_facts[nutrient] = match.group(1)

    for key, value in nutrition_facts.items():
        try:
            if 'g' in value:
                nutrition_facts[key] = float(value.replace('g', ''))
            elif 'mg' in value:
                nutrition_facts[key] = float(value.replace('mg', '')) / 1000
        except ValueError:
            print(f"Could not convert value for {key}: '{value}'")

    return nutrition_facts

@app.route("/")
def contact():
    button = request.args.get('btn')
    filename = request.args.get('fname')
    if button == "Delete":
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            print("could not find file")
    elif button == "Submit":
        filename = UPLOAD_PATH + '/' + filename
        print(filename)
        return render_template('index.html', fileList = os.listdir(UPLOAD_PATH), filePreview = filename)
    return render_template('index.html', fileList = os.listdir(UPLOAD_PATH))

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/upload")
def upload():
    return render_template('upload.html', fileList = os.listdir(UPLOAD_PATH))

@app.route("/result", methods = ['POST'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        filename = request.form.get('fname')
        filename = filename.replace(" ", "_")
        extension = os.path.splitext(f.filename)[1]
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
        nutrition_facts = extract_nutritional_facts(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
        print("\nExtracted Nutritional Facts:\n", nutrition_facts)
        return render_template('upload.html', name = f.filename, fileList = os.listdir(UPLOAD_PATH))

@app.route("/settings_calories", methods=['GET'])
def settings_calories():
    return "200"

if __name__ == '__main__':
    app.run()
