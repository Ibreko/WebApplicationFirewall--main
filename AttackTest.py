import sqlite3
from SQLi import detect_sql_injection, cur, connection
from XSS import detect_xss
import socket

def attack_tester(user_input):
    ip_address = socket.gethostbyname(socket.gethostname())
    attack_type = ""

    if detect_sql_injection(user_input):
        attack_type = "SQL Injection"
        print("SQLi")
    elif detect_xss(user_input):
        attack_type = "XSS Attack"

    if attack_type:
        print("Hello")
        log_attack(ip_address, attack_type)
        return True

def log_attack(ip_address, attack_type):
    try:
        cur.execute("INSERT INTO attacks (attack_type, ip_address) VALUES (?, ?)", (attack_type, ip_address))
        connection.commit()
        print(f"Attack detected: {attack_type} from IP {ip_address}")
        
        # Print current database content
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM attacks;")
        rows = cursor.fetchall()
        print("Current database content:")
        for row in rows:
            print(row)
        cursor.close()

        # Print database file name and path
        db_filename = connection.execute("PRAGMA database_list;").fetchone()[2]
        print(f"Database file name and path: {db_filename}")
    except sqlite3.Error as e:
        print(f"SQLite error when logging attack: {e}")
    except Exception as e:
        print(f"Error logging attack: {e}")

# Example usage
user_in = "'<p><script>'"
attack_tester(user_in)
