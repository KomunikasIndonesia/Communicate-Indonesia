from datetime import datetime

from flask import Flask, request, abort
from twilio import twiml
from app.api.sms.broadcast_action import BroadcastAction, BroadcastCommand

from app.api.sms.plant_action import PlantCommand, PlantAction
from app.api.sms.harvest_action import HarvestCommand, HarvestAction
from app.api.sms.sell_action import SellCommand, SellAction
from app.api.sms.query_action import QueryCommand, QueryAction
from app.command.base import Dispatcher, NoRouteError, MultipleRouteError
from app.i18n import _
from app.model.config import Config
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.util.flask_common import enable_json_error, log_request


app = Flask(__name__)
enable_json_error(app)


@app.before_request
def log():
    log_request(app)


dispatcher = Dispatcher()
dispatcher.route(PlantCommand, PlantAction)
dispatcher.route(HarvestCommand, HarvestAction)
dispatcher.route(SellCommand, SellAction)
dispatcher.route(QueryCommand, QueryAction)
dispatcher.route(BroadcastCommand, BroadcastAction)


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
    user = User.query(User.phone_number == sms.from_number).fetch()
    if not user:
        abort(400, 'The phone number {} does not belong to a user'.format(sms.from_number))

    sms.user = user[0]

    response_twiml = twiml.Response()
    response_message = None

    # dispatch sms request
    try:
        response_message = dispatcher.dispatch(sms)
    except (NoRouteError, MultipleRouteError):
        response_message = _('Unknown command, valid format below:\n'
                             'PLANT [qty] [type]\n'
                             'HARVEST [qty] [type]\n'
                             'SELL [qty] [type]\n'
                             'BROADCAST [msg]')

    if response_message:
        config = Config.query().get()
        response_twiml.sms(to=sms.from_number,
                           sender=config.twilio_phone_number,
                           msg=response_message)

    # update sms processed state
    sms.processed = True
    sms.ts_processed = datetime.now()
    sms.put()

    return str(response_twiml)
