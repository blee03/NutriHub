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
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('index.html', name = f.filename, fileList = os.listdir('uploads'))

if __name__ == '__main__':
    app.run()