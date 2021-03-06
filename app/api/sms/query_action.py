import logging
from app.api.sms.base_action import OneArgCommand
from app.command.base import Action
from app.model.farm import Farm
from app.model.district import District

from app.i18n import _
from google.appengine.ext import ndb
from app.model.permission import RETRIEVE_ALL_DISTRICT


class QueryAction(Action):
    """
    Execute a query operation.
    """

    def __init__(self, command):
        super(QueryAction, self).__init__(command)

    def execute(self):
        filter = self.command.filter
        user = self.command.sms.user

        if RETRIEVE_ALL_DISTRICT not in user.permissions:
            logging.info('{} - User {} does not have permission {}'.format(
                self.command.sms.key.id(), user.key.id(), RETRIEVE_ALL_DISTRICT))
            return _('Command not allowed')

        district_name = self.command.district
        slug = district_name.lower()
        district = District.query(District.slug == slug).get()

        if not district:
            logging.info('{} - District {} is unknown'.format(
                self.command.sms.key.id(), district_name))
            return _('District {} is unknown').format(district_name)

        query = Farm.query(ndb.AND(Farm.action == filter,
                                   Farm.district_id == district.key.id()))
        crops = query.order(-Farm.ts_updated).fetch()

        if not crops:
            return _('{} data is none').format(_(filter))

        response = _('Total {} in {}:').format(_(filter), district.name)
        for crop in crops:
            response += '\n{} {}'.format(_(crop.crop_name).title(),
                                         crop.quantity)
        return response


class QueryCommand(OneArgCommand):
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

    FILTER_MAPPING = {
        'panen': 'harvest',
        'tanam': 'plant',
        'jual': 'sell'
    }

    DEFAULT = 'harvest'

    def __init__(self, sms):
        super(QueryCommand, self).__init__(sms)
        self.district = None
        self.filter = self.DEFAULT

        words = self.message.split()
        for filter in self.VALID_FILTER:
            if filter in words:
                self.filter = filter
                words.remove(filter)
                break

        self.district = ' '.join(words)

        if self.filter in self.FILTER_MAPPING:
            self.filter = self.FILTER_MAPPING[self.filter]

    def valid(self):
        return super(QueryCommand, self).valid() \
            and self.district and self.filter
