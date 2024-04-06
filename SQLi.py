import re
import sqlite3
import socket

connection = sqlite3.connect('waf.db', check_same_thread=False)
cur = connection.cursor()
ip_address = socket.gethostbyname(socket.gethostname())


def detect_sql_injection(input_string):
    sql_injection_pattern = r'\b(?:OR\s*\d*\s*=\s*\d*|--|;|\b(?:AND|OR)\b\s*[\w\s][=<>]+\s[\w\s\']|UNION\s[\w\s]*\b(?:SELECT|ALL)\b)\b'
    sql_pattern = r'\b(?:SELECT|UNION|INSERT|UPDATE|DELETE|FROM|WHERE)\b'

    if re.search(sql_injection_pattern, input_string, re.IGNORECASE) or re.search(sql_pattern, input_string,
                                                                                  re.IGNORECASE):
        print ("SQL injection")
        return True
  
