from flask import Flask
from twilio import twiml
from app.api.sms.plant_action import PlantCommand, PlantAction
from app.api.sms.sms_request import SmsRequest
from app.command.base import Dispatcher

app = Flask(__name__)
app.debug = True


dispatcher = Dispatcher()
dispatcher.route(PlantCommand, PlantAction)


@app.route('/v1/sms/twilio')
def twilio():
    sms = SmsRequest()
    sms.from_ = '111'
    sms.to = '222'
    sms.body = 'plant 20 potato'

    response = dispatcher.dispatch(sms)
    if response:
        # TODO - send sms response to the from_ number
        pass

    return str(twiml.Response())
