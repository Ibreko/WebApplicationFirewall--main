import re

def detect_xss(input_text):
    xss_pattern = re.compile(r'<script[\s\S]*?>|<\/script[\s\S]*?>', re.IGNORECASE)

    if xss_pattern.search(input_text):
        print(f'Potential XSS attack detected: {input_text}')
        return True
    else:
        print("No Potential XSS attack detected")
        return False
