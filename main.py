from fileinput import filename 
from flask import *  
from werkzeug.utils import secure_filename
import os

app = Flask(__name__) 

app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route("/")
def main():
    return render_template('index.html', fileList = os.listdir('uploads'))

@app.route("/result", methods = ['POST'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        filename = request.form.get('fname')
        extension = os.path.splitext(f.filename)[1]
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + extension))
        return render_template('index.html', name = f.filename, fileList = os.listdir('uploads'))

if __name__ == '__main__':
    app.run()
    