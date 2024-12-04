from fileinput import filename 
from flask import *  
from werkzeug.utils import secure_filename
import os
import base64
import requests
import sqlite3
from init_db import reset
import re
from dotenv import load_dotenv
from datetime import date

app = Flask(__name__) 

UPLOAD_PATH = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# db_config = {
#     'user': 'new_user',
#     'password': 'test1',
#     'host': '35.237.230.58',  # Replace with Google Cloud SQL public IP
#     'database': 'my_sql_database'
# }

# def connect_to_database():
#     connection = mysql.connector.connect(**db_config)
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("select * from label;")
#     results = cursor.fetchall()
#     print(results,'connection successful')
#     cursor.close()
#     connection.close()
# def extract_value(pattern, text, default=0):
#     match = re.search(pattern, text)
#     if match:
#         return float(match.group(1))
#     else:
#         print(f"Warning: Could not find pattern '{pattern}' in text.")
#         return default

# def insert_to_label(image_path, file_name):
#     connection = mysql.connector.connect(**db_config)
#     cursor = connection.cursor(dictionary=True)
#     nutrition_facts, nutrition_text = extract_nutritional_facts(image_path)
#     serving_size_pattern = r"(?i)\bserving Size\b.*\((\d+)g\)"
#     calories_pattern = r"(?i)Calories\s*\|?\s*(\d+)"
#     total_fat_pattern = r"(?i)Total Fat\s+(\d+\.\d+|\d+)g"
#     cholesterol_pattern = r"(?i)Cholesterol\s+(\d+)mg"
#     sodium_pattern = r"(?i)Sodium\s+(\d+)mg"
#     total_carbohydrate_pattern = r"(?i)\b(?:Total\s+)?(?:Carbohydrate|Carb)\.?\b.*?(\d+)g"
#     protein_pattern = r"(?i)Protein\s+(\d+)g"

#     serving_size = re.search(serving_size_pattern, nutrition_text).group(1)
#     calories = int(extract_value(calories_pattern, nutrition_text, default=0))
#     total_fat = extract_value(total_fat_pattern, nutrition_text, default=0.0)
#     cholesterol = extract_value(cholesterol_pattern, nutrition_text, default=0.0)
#     sodium = extract_value(sodium_pattern, nutrition_text, default=0.0)
#     carbohydrates = extract_value(total_carbohydrate_pattern, nutrition_text, default=0.0)
#     protein = extract_value(protein_pattern, nutrition_text, default=0.0)
#     filename=file_name
#     insert_query = "INSERT INTO label (calories, total_fat, cholesterol, sodium, carbohydrates, protein, filename) VALUES (%s, %s, %s, %s, %s, %s, %s);"
#     cursor.execute(insert_query, (calories, total_fat, cholesterol, sodium, carbohydrates, protein, filename))
#     connection.commit()
#     print("Data inserted successfully.")
#     cursor.close()
#     connection.close()

def extract_nutritional_facts(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    API_URL = "https://vision.googleapis.com/v1/images:annotate"
    API_KEY = str(os.getenv('API_KEY'))  # Replace with your API key

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
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/goal")
def about():
    return render_template('settingsv3.html')

@app.route("/uploadv2")
def uploadv2():
    conn = get_db_connection()
    labels = conn.execute('SELECT * FROM label').fetchall()
    conn.close()
    return render_template('uploadV2.html', labels = labels)

# @app.route('/main')
# def index():
#     conn = get_db_connection()
#     labels = conn.execute('SELECT * FROM label').fetchall()
#     conn.close()
#     print(labels)
#     return render_template('main.html', labels=labels)

# @app.route('/resultv2', methods = ['POST'])
# def resultv2():
#     if request.method == 'POST':
#         f = request.files['file']
#         filename = request.form.get('fname')
#         filename = filename.replace(" ", "_")
#         extension = os.path.splitext(f.filename)[1]

#         # save the file to the static/uploads folder
#         f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
#         nutrition_facts = extract_nutritional_facts(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
#         print("\nExtracted Nutritional Facts:\n", nutrition_facts)
#         return render_template('uploadV2.html', name = f.filename, fileList = os.listdir(UPLOAD_PATH))

@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    labels = conn.execute('SELECT * FROM label').fetchall()

    # get all meals with the current date and add up all the macros to get the total for the day
    meals = conn.execute("SELECT * FROM meal WHERE date = ?", (date.today(),)).fetchall()
    total_calories = 0
    total_fat = 0
    total_carbs = 0
    total_protein = 0

    for meal in meals:
        label = conn.execute("SELECT * FROM label WHERE id = ?", (meal['label_id'],)).fetchone()
        total_calories += label['calories'] * meal['servings']
        total_fat += label['fat'] * meal['servings']
        total_carbs += label['carbs'] * meal['servings']
        total_protein += label['protein'] * meal['servings']
    conn.close()
    
    if(len(meals) == 0):
        return render_template('dashboard.html', labels=labels)
    else:
        return render_template('dashboard.html', labels=labels, meals = meals, total_calories=total_calories, total_fat=total_fat, total_carbs=total_carbs, total_protein=total_protein)

# @app.route("/home")
# def contact():
#     button = request.args.get('btn')
#     filename = request.args.get('fname')
#     if button == "Delete":
#         if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
#             os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         else:
#             print("could not find file")
#     elif button == "Submit":
#         filename = UPLOAD_PATH + '/' + filename
#         return render_template('index.html', fileList = os.listdir(UPLOAD_PATH), filePreview = filename)
#     return render_template('index.html', fileList = os.listdir(UPLOAD_PATH))

# @app.route("/settings")
# def settings():
#     return render_template('settings.html')

# @app.route("/upload")
# def upload():
#     return render_template('upload.html', fileList = os.listdir(UPLOAD_PATH))

# @app.route("/result", methods = ['POST'])
# def result():
#     if request.method == 'POST':
#         f = request.files['file']
#         filename = request.form.get('fname')
#         filename = filename.replace(" ", "_")
#         extension = os.path.splitext(f.filename)[1]
#         f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
#         nutrition_facts = extract_nutritional_facts(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
#         print("\nExtracted Nutritional Facts:\n", nutrition_facts)
#         return render_template('upload.html', name = f.filename, fileList = os.listdir(UPLOAD_PATH)) 

@app.route('/addlabel', methods = ['POST'])
def addlabel():
    if request.method == 'POST':
        f = request.files['file']
        filename = request.form.get('fname')
        filename = filename.replace(" ", "_")

        # save the file to the static/uploads folder
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))

        # extract nutritional facts from the image
        nutritional_label = extract_nutritional_facts(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))

        # check if the nutritional facts are complete
        if(len(nutritional_label) != 4):
            # go through and fill in the missing values with 0
            nutritional_label['Calories'] = nutritional_label.get('Calories', 0)
            nutritional_label['Total Fat'] = nutritional_label.get('Total Fat', 0)
            nutritional_label['Total Carbohydrate'] = nutritional_label.get('Total Carbohydrate', 0)
            nutritional_label['Protein'] = nutritional_label.get('Protein', 0)

        # connect to the database and insert the nutritional facts
        conn = get_db_connection()
        conn.execute("INSERT INTO label (name, file_name, calories, fat, carbs, protein) VALUES (?, ?, ?, ?, ?, ?)",
                    (filename, f.filename, nutritional_label['Calories'], nutritional_label['Total Fat'], nutritional_label['Total Carbohydrate'], nutritional_label['Protein'])
                    )
        conn.commit()
        labels = conn.execute('SELECT * FROM label').fetchall()
        conn.close()

        return redirect(url_for('uploadv2'))

@app.route("/addmeal", methods = ['POST'])
def addmeal():
    if request.method == 'POST':
        servings = request.form.get('servings')
        label = request.form.get('label')
        labelStrip = label.split('%')[0]

        # connect to the database and insert the meal association
        conn = get_db_connection()
        conn.execute("INSERT INTO meal (label_id, servings, date) VALUES (?, ?, ?)",
                    (labelStrip, servings, date.today())
                    )
        conn.commit()

        # # get all meals with the current date and add up all the macros to get the total for the day
        # meals = conn.execute("SELECT * FROM meal WHERE date = ?", (date.today(),)).fetchall()
        # total_calories = 0
        # total_fat = 0
        # total_carbs = 0
        # total_protein = 0

        # for meal in meals:
        #     label = conn.execute("SELECT * FROM label WHERE id = ?", (meal['label_id'],)).fetchone()
        #     total_calories += label['calories'] * meal['servings']
        #     total_fat += label['fat'] * meal['servings']
        #     total_carbs += label['carbs'] * meal['servings']
        #     total_protein += label['protein'] * meal['servings']
        # conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/updatelabel/<int:label_id>', methods=['POST'])
def updatelabel(label_id):
    if request.method == 'POST':
        calories = request.form.get('calories')
        fat = request.form.get('fat')
        carbs = request.form.get('carbs')
        protein = request.form.get('protein')

        conn = get_db_connection()
        conn.execute("UPDATE label SET calories = ?, fat = ?, carbs = ?, protein = ? WHERE id = ?",
                        (calories, fat, carbs, protein, label_id))
        conn.commit()
        conn.close()

        return redirect(url_for('uploadv2'))
if __name__ == '__main__':
    reset()
    app.run()
