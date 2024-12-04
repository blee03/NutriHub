from fileinput import filename 
from flask import *  
from werkzeug.utils import secure_filename
import os
import mysql.connector

import pytesseract
from PIL import Image
import re

app = Flask(__name__) 

UPLOAD_PATH = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

db_config = {
    'user': 'new_user',
    'password': 'test1',
    'host': '35.237.230.58',  # Replace with Google Cloud SQL public IP
    'database': 'my_sql_database'
}

def connect_to_database():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("select * from label;")
    results = cursor.fetchall()
    print(results,'connection successful')
    cursor.close()
    connection.close()
def extract_value(pattern, text, default=0):
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    else:
        print(f"Warning: Could not find pattern '{pattern}' in text.")
        return default

def insert_to_label(image_path, file_name):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    nutrition_facts, nutrition_text = extract_nutritional_facts(image_path)
    serving_size_pattern = r"(?i)\bserving Size\b.*\((\d+)g\)"
    calories_pattern = r"(?i)Calories\s*\|?\s*(\d+)"
    total_fat_pattern = r"(?i)Total Fat\s+(\d+\.\d+|\d+)g"
    cholesterol_pattern = r"(?i)Cholesterol\s+(\d+)mg"
    sodium_pattern = r"(?i)Sodium\s+(\d+)mg"
    total_carbohydrate_pattern = r"(?i)\b(?:Total\s+)?(?:Carbohydrate|Carb)\.?\b.*?(\d+)g"
    protein_pattern = r"(?i)Protein\s+(\d+)g"

    serving_size = re.search(serving_size_pattern, nutrition_text).group(1)
    calories = int(extract_value(calories_pattern, nutrition_text, default=0))
    total_fat = extract_value(total_fat_pattern, nutrition_text, default=0.0)
    cholesterol = extract_value(cholesterol_pattern, nutrition_text, default=0.0)
    sodium = extract_value(sodium_pattern, nutrition_text, default=0.0)
    carbohydrates = extract_value(total_carbohydrate_pattern, nutrition_text, default=0.0)
    protein = extract_value(protein_pattern, nutrition_text, default=0.0)
    filename=file_name
    insert_query = "INSERT INTO label (calories, total_fat, cholesterol, sodium, carbohydrates, protein, filename) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(insert_query, (calories, total_fat, cholesterol, sodium, carbohydrates, protein, filename))
    connection.commit()
    print("Data inserted successfully.")
    cursor.close()
    connection.close()

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
    nutrition_text = text
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

    return nutrition_facts, nutrition_text

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

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        db_result = connect_to_database()

        if 'file' not in request.files:
            return render_template('upload.html', error="No file part")

        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error="No selected file")

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('upload.html', message=f'File "{filename}" uploaded successfully! {db_result}')

    return render_template('upload.html', fileList = os.listdir(UPLOAD_PATH))

@app.route("/result", methods = ['POST'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        filename = request.form.get('fname')
        filename = filename.replace(" ", "_")
        extension = os.path.splitext(f.filename)[1]

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
        nutrition_facts, nutrition_text = extract_nutritional_facts(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
        print("\nExtracted Nutritional Facts:\n", nutrition_facts)
        insert_to_label(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension), ''.join(os.path.splitext(f.filename)))
        connect_to_database()

        return render_template('upload.html', name = f.filename, fileList = os.listdir(UPLOAD_PATH))

@app.route("/settings_calories", methods=['GET'])
def settings_calories():
    return "200"    

if __name__ == '__main__':
    app.run()
