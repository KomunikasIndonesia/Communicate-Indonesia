from datetime import datetime

from flask import Flask, request, abort
from twilio import twiml

from app.api.sms.plant_action import PlantCommand, PlantAction
from app.model.sms_request import SmsRequest
from app.command.base import Dispatcher
from app.model.user import User
from app.util.flask_common import enable_json_error

app = Flask(__name__)
app.debug = True
enable_json_error(app)


dispatcher = Dispatcher()
dispatcher.route(PlantCommand, PlantAction)


@app.route('/v1/sms/twilio', methods=['POST'])
def incoming_twilio_sms():
    sms = SmsRequest(id=SmsRequest.id(),
                     from_number=request.form.get('From'),
                     to_number=request.form.get('To'),
                     body=request.form.get('Body'),
                     twilio_message_id=request.form.get('MessageSid'),
                     from_city=request.form.get('FromCity'),
                     from_state=request.form.get('FromState'),
                     from_zip=request.form.get('FromZip'),
                     from_country=request.form.get('FromCountry'),
                     to_city=request.form.get('ToCity'),
                     to_state=request.form.get('ToState'),
                     to_zip=request.form.get('ToZip'),
                     to_country=request.form.get('ToCountry'))

    if not sms.valid:
        app.logger.error(request)
        abort(400, 'invalid request')

    # store all sms for auditing
    sms.put()

    # load application data associated with the sms
    sms.user = User.query(User.phone_number == sms.from_number).fetch()
    if not sms.user:
        abort(400, 'The phone number {} does not belong to a user'.format(sms.from_number))

    response_twiml = twiml.Response()

    # dispatch sms request
    response_message = dispatcher.dispatch(sms)

    if response_message:
        response_twiml.sms(to=sms.from_number,
                           sender='123456',  # TODO - add this to configuration
                           msg=response_message)

    # update sms processed state
    sms.processed = True
    sms.ts_processed = datetime.now()
    sms.put()

    return str(response_twiml)
