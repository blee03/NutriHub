from fileinput import filename 
from flask import *  
app = Flask(__name__) 

@app.route("/")
def main():
    return render_template('upload.html')

@app.route("/result", methods = ['POST'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        print(f.filename)
        print(f)
        f.save(f.filename)
        return render_template('result.html', name = f.filename)

if __name__ == '__main__':
    app.run()