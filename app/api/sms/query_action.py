from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm
from app.model.district import District

from app.i18n import _
from google.appengine.ext import ndb


class QueryAction(Action):
    """
    Execute a query operation.
    """
    FILTER = {
        'panen': 'harvest',
        'tanam': 'plant',
        'jual': 'sell'
    }

    LIMIT = 8

    def __init__(self, command):
        super(QueryAction, self).__init__(command)

    def execute(self):
        place = self.command.district
        district = District.query(District.name == place).fetch()[0]
        district_id = district.key.id()

        filter = self.command.filter
        if filter in self.FILTER:
            filter = self.FILTER[self.command.filter]

        query = Farm.query(ndb.AND(Farm.action == filter,
                                   Farm.district_id == district_id))
        crops = query.order(-Farm.ts_updated).fetch(self.LIMIT)

        if len(crops) == 0:
            return _('{} data is none').format(_(filter))

        response = _('Total {} in {}:').format(_(filter), place.title())
        for crop in crops:
            response += '\n{} {}'.format(_(crop.crop_name).title(),
                                         crop.quantity)
        return response


class QueryCommand(ThreeArgCommand):
    """
    Represents a query command

    A query command takes the form of:
        <command> <district> <filter>
        <command> <filter> <district>
        <command> <district>

    eg.
        look lompoko sell/plant/harvest
        look sell/plant/harvest lompoko
        look lompoko (default harvest)
    """
    VALID_CMDS = [
        'look',  # en
        'lihat'  # in
    ]

    VALID_FILTER = [
        'harvest', 'panen',
        'plant', 'tanam',
        'sell', 'jual'
    ]

    DEFAULT = 'harvest'

    def __init__(self, sms):
        super(QueryCommand, self).__init__(sms)
        self.district = None
        self.filter = self.DEFAULT

        if not self.args[1] \
                and self.args[0] not in self.VALID_FILTER:
            self.district = self.args[0]

        if self.args[1] \
                and self.args[0] in self.VALID_FILTER:
            self.district = self.args[1]
            self.filter = self.args[0]

        if self.args[1] in self.VALID_FILTER:
            self.district = self.args[0]
            self.filter = self.args[1]

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.district and self.filter
