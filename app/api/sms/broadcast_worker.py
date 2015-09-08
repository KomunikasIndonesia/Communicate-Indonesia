from flask import Flask, request
from twilio.rest import TwilioRestClient
from app.model.config import Config
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    ensure_param
)
import json

app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/sms/broadcast', methods=['POST'])
@ensure_param('task')
@jsonify
def broadcast_sms():
    config = Config.query().get()
    data = request.form.get('task')

    d = json.loads(data)
    phone_numbers = d['phone_numbers']
    message = d['message']

    client = TwilioRestClient(
        config.twilio_account_sid,
        config.twilio_auth_token)

    for phone_number in phone_numbers:
        client.messages.create(
            body=message,
            to=phone_number,
            from_=config.twilio_phone_number)

    return {
        'farmers_sent': len(phone_numbers),
        'body': message
    }
