from fileinput import filename 
from flask import *  
from werkzeug.utils import secure_filename
import os

import pytesseract
from PIL import Image
import re

app = Flask(__name__) 

UPLOAD_PATH = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

def extract_nutritional_facts(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    print("Raw OCR Output:\n", text)

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

# add a route for the landing page that u just created
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/goal")
def about():
    return render_template('settingsv3.html')

@app.route("/uploadv2")
def uploadv2():
    return render_template('uploadV2.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

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

if __name__ == '__main__':
    app.run()
