from flask import Flask
from twilio import twiml


app = Flask(__name__)
app.debug = True



@app.route('/v1/sms/twilio')
def twilio():
    return str(twiml.Response())
