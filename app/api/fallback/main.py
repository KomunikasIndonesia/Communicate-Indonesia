from flask import Flask, request
from twilio import twiml

from app.api.fallback.mail import notify_admin
from app.i18n import _
from app.model.config import Config
from app.model.sms_request import SmsRequest
from app.util.flask_common import enable_json_error


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/fallback', methods=['POST'])
def fallback_url():
    notify_admin()

    sms = SmsRequest(from_number=request.form.get('From'))

    response_twiml = twiml.Response()
    response_message = _('Sorry, we are having some temporary server issues')

    config = Config.query().get()
    response_twiml.sms(to=sms.from_number,
                       sender=config.twilio_phone_number,
                       msg=response_message)

    return str(response_twiml)
