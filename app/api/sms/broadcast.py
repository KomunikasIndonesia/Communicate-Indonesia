from flask import Flask, request
from twilio.rest import TwilioRestClient
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    ensure_param
)

app = Flask(__name__)
enable_json_error(app)


# test credentials
ACCOUNT_SID = 'AC94da6f9c22530311d9fa507e236832b8'  # add in config?
AUTH_TOKEN = '359d1bd6ae49c09c3639dde72a79e072'  # add in config?


@app.route('/v1/sms/broadcast', methods=['POST'])
@ensure_param('phone_number')
@ensure_param('message')
@jsonify
def broadcast_sms():
    phone_number = request.form.get('phone_number')
    message = request.form.get('message')

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    msg = client.messages.create(
        body=message,
        to=phone_number,
        from_='+15005550006'  # add in config?
    )

    return {
        'sid': msg.sid,
        'from': msg.from_,
        'to': msg.to,
        'body': msg.body
    }
