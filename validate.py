
import re

def valid_name(name):
    name = str(name)
    if re.match(r'[a-zA-Z]*$', name):
        return True

def valid_password(password):
    if re.match(r'[a-zA-Z0-9]', password):
        return 'Valid Password'
       
def valid_email(email):
    if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email):
        return 'Valid Email'
       