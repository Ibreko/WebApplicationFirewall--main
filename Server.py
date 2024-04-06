import sqlite3
from traceback import print_tb
from flask import Flask, render_template, request, flash, redirect, url_for, session, request, g
from flask_session import Session
from AttackTest import attack_tester
import time

# Function to create tables
def create_tables():
    connection = sqlite3.connect('waf.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attack_type TEXT,
            TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', ('admin', 'keystone'))

    connection.commit()
    connection.close()

# Create Flask app
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waf.db'
Session(app)

# Initialize tables
create_tables()

request_count = 0
last_reset = time.time()

def get_db_connection():
    conn = sqlite3.connect('waf.db',  check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():    
    return render_template('index.html')
  
def my_route():
    client_ip = request.remote_addr
    print(f"Client IP: {client_ip}")

@app.route("/login", methods=["GET"])
def get_login():
    return render_template('login.html')

DDOS = True
@app.before_request
def limit_requests():
    global request_count, last_reset
    
    # Check if a minute has passed since the last reset
    current_time = time.time()
    print(current_time)
    if current_time - last_reset > 60:
        # Reset the request count
        request_count = 0
        last_reset = current_time
      
    
    # Check if request count has reached 60, if not, process the request
    if request_count >= 20:
        print("Too many requests. Try again later.")  # HTTP status code for "Too Many Requests"
        DDOS = False
    else:
        request_count += 1


@app.route("/login", methods=["POST"])
def post_login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if len(username) > 0 and len(password) > 0:
        if attack_tester(username) or attack_tester(password):
            flash("Potential attack detected", "error")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and user['password'] == password:
            session["name"] = username
            return redirect("/home")
        else:
            flash("Incorrect username or password", "error")
    else:
        flash("Enter both username and password", "error")

    return render_template("login.html")


@app.route("/home")
def home():
    print(session.get("name"))
    if not session.get("name"):
        return redirect("/")
    conn = get_db_connection()
    attacks = conn.execute(f'SELECT * FROM attacks;').fetchall()
    conn.close()
    return render_template("home.html", username=session.get("name"), attacks=attacks)


def display_attack_info():
    # Get attack information
    attack_data = get_attack_info()
    
    # Pass the data to the HTML template
    return render_template('attacks.html', attack_data=attack_data)


def get_attack_info():
    conn = sqlite3.connect('waf.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Assuming your table structure has columns id, attack_type, TIMESTAMP, and ip_address
    cursor.execute('SELECT * FROM attacks;')
    attack_data = cursor.fetchall()
    
    conn.close()
    
    return attack_data

@app.route("/logout")
def logout():
    session["name"] = None 
    return redirect("/")

if __name__=="__main__":
   
    app.run(debug=True, host = 'localhost')
