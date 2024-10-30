from fileinput import filename 
from flask import *  
from werkzeug.utils import secure_filename
import os

app = Flask(__name__) 

app.config['UPLOAD_FOLDER'] = 'uploads'

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
        print("submit")
    return render_template('index.html', fileList = os.listdir('uploads'))

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/upload")
def upload():
    return render_template('upload.html', fileList = os.listdir('uploads'))

@app.route("/result", methods = ['POST'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        filename = request.form.get('fname')
        extension = os.path.splitext(f.filename)[1]
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
        return render_template('upload.html', name = f.filename, fileList = os.listdir('uploads'))

@app.route("/settings_calories", methods=['GET'])
def settings_calories():
    return "200"

if __name__ == '__main__':
    app.run()
