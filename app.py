from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Used for session management

# Dummy in-memory "database" for user data
users_db = {}

# Dummy in-memory "wallet" (in a real app, you'd store this in a database)
user_wallet_balance = {}

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for the homepage
@app.route("/")
def home():
    # Check if user is logged in
    if 'username' in session:
        username = session['username']
        return render_template("upload.html", wallet_balance=user_wallet_balance.get(username, 0.0), username=username)
    else:
        return redirect(url_for('signin'))

# Route for Sign Up page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username already exists
        if username in users_db:
            return "Username already exists! Please choose a different one."
        
        # Store the new user in the dummy database
        users_db[username] = {"username": username, "password": password}
        user_wallet_balance[username] = 100.0  # Default wallet balance
        
        # After sign-up, automatically sign in the user
        session['username'] = username
        return redirect(url_for('home'))

    return render_template("signup.html")

# Route for Sign In page
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username exists and password matches
        if username in users_db and users_db[username]["password"] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid username or password. Please try again."

    return render_template("signin.html")

# Route for uploading files
@app.route("/upload", methods=["POST"])
def upload_files():
    if 'username' not in session:
        return redirect(url_for('signin'))

    username = session['username']
    files = [request.files.get(f'file{i}') for i in range(1, 6)]
    file_names = []
    
    for file in files:
        if file and file.filename.endswith(('.xls', '.xlsx')):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            file_names.append(file.filename)
        else:
            return "Invalid file format. Only Excel files are allowed.", 400
    
    return f"Files uploaded successfully: {', '.join(file_names)}"

# Route to handle adding funds to the wallet
@app.route("/add_funds", methods=["POST"])
def add_funds():
    if 'username' not in session:
        return redirect(url_for('signin'))
    
    username = session['username']
    amount = float(request.form['amount'])
    user_wallet_balance[username] += amount
    return jsonify({"message": f"Funds added. New balance: ${user_wallet_balance[username]}"})

# Route to handle making payments from the wallet
@app.route("/make_payment", methods=["POST"])
def make_payment():
    if 'username' not in session:
        return redirect(url_for('signin'))
    
    username = session['username']
    payment_amount = float(request.form['payment_amount'])

    if payment_amount <= user_wallet_balance[username]:
        user_wallet_balance[username] -= payment_amount
        return jsonify({"message": f"Payment successful. New balance: ${user_wallet_balance[username]}"})
    else:
        return jsonify({"error": "Insufficient balance."}), 400

# Route to handle sign out
@app.route("/signout")
def signout():
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == "__main__":
    app.run(debug=True)
