from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    # Example authentication logic
    if username == 'admin' and password == 'password':
        return "Welcome, Admin!"
    else:
        return "Invalid credentials. Please try again."

@app.route('/forgot-password')
def forgot_password():
    return "Forgot Password page under construction."

if __name__ == '__main__':
    app.run(debug=True)
