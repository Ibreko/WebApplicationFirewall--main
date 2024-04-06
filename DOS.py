from flask import Flask, request
import time

app = Flask(__name__)

request_count = 0
last_reset = time.time()

@app.before_request
def limit_requests():
    global request_count, last_reset
    
    # Check if a minute has passed since the last reset
    current_time = time.time()
    if current_time - last_reset > 60:
        # Reset the request count
        request_count = 0
        last_reset = current_time
    
    # Check if request count has reached 60, if not, process the request
    if request_count >= 60:
        return "Too many requests. Try again later.", 429  # HTTP status code for "Too Many Requests"
    else:
        request_count += 1

if __name__ == '__main__':
    app.run(debug=True)
