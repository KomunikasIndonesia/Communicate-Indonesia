from flask import Flask, request
from app.model.config import Config
from app.util.flask_common import (
    jsonify,
    enable_json_error
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/config', methods=['GET'])
@jsonify
def config():
    update = request.args.get('update')

    config = Config()
    existing_configs = Config.query().fetch()
    if existing_configs:
        config = existing_configs[0]

    if update == 'true':
        admin_username = request.args.get('admin_username')
        admin_apikey = request.args.get('admin_apikey')
        twilio_account_sid = request.args.get('twilio_account_sid')
        twilio_auth_token = request.args.get('twilio_auth_token')
        twilio_phone_number = request.args.get('twilio_phone_number')

        if admin_username:
            config.admin_username = admin_username
        if admin_apikey:
            config.admin_apikey = admin_apikey
        if twilio_account_sid:
            config.twilio_account_sid = twilio_account_sid
        if twilio_auth_token:
            config.twilio_auth_token = twilio_auth_token
        if twilio_phone_number:
            config.twilio_phone_number = twilio_phone_number

        config.put()

    return config.toJson()
