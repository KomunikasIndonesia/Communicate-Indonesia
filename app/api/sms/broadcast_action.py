from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.user import User
from app.model.district import District

from app.i18n import _
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import json

TO_ALL = [
    'everyone',  # en
    'semua'      # in
]


class BroadcastAction(Action):
    """
    Execute a broadcast operation
    """
    QUEUE_URL = '/v1/sms/broadcast'
    QUEUE_NAME = 'broadcast'

    def __init__(self, command):
        super(BroadcastAction, self).__init__(command)

    def execute(self):
        cmd = self.command
        user = cmd.sms.user

        if user.role == User.ROLE_HUTAN_BIRU:
            if cmd.to == TO_ALL[0]:
                farmers = User.query(User.role == User.ROLE_FARMER).fetch()
            else:
                district = District.query(District.name == cmd.to).fetch()
                district_id = district[0].key.id()
                farmers = User.query(ndb.AND(
                    User.role == User.ROLE_FARMER,
                    User.district_id == district_id)
                ).fetch()

        if user.role == User.ROLE_FARMER:
            farmers = User.query(ndb.AND(
                User.role == User.ROLE_FARMER,
                User.district_id == cmd.to_id)
            ).fetch()

        phone_numbers = [farmer.phone_number for farmer in farmers]

        if phone_numbers:
            for phone_number in phone_numbers:
                taskqueue.add(
                    queue_name=self.QUEUE_NAME,
                    url=self.QUEUE_URL,
                    payload=json.dumps({'phone_number': phone_number,
                                        'message': cmd.msg})
                )
            return _('Message sent to {}').format(_(cmd.to))
        return _('Message delivery failed')


class BroadcastCommand(ThreeArgCommand):
    """
    Represents a broadcast command

    A broadcast command can take the form of:
    Hutan biru:
        <command> <district> <message>
        <command> <everyone> <message>
    Farmers (leader):
        <command> <district> <message>
        <command> <message>
    """
    VALID_CMDS = [
        'broadcast',  # en
        'kirim'       # in
    ]

    def __init__(self, sms):
        super(BroadcastCommand, self).__init__(sms)
        self.to = None
        self.msg = None
        district = []

        if self.args[0]:
            district = District.query(District.name == self.args[0]).fetch()

        if sms.user.role == User.ROLE_HUTAN_BIRU:
            if self.args[1] and self.args[0] in TO_ALL:
                self.to = TO_ALL[0]
                self.msg = self.args[1]

            if self.args[1] and district:
                self.to = self.args[0]
                self.msg = self.args[1]
                self.to_id = district[0].key.id()

        if sms.user.role == User.ROLE_FARMER:
            self.to_id = sms.user.district_id
            self.to = District.get_by_id(self.to_id).name

            if not self.args[1] and not district:
                self.msg = self.args[0]

            if self.args[1]:
                self.msg = ' '.join([self.args[0], self.args[1]])
                if district and district[0].key.id() == self.to_id:
                    self.msg = self.args[1]

        if self.message:
            self.msg = ' '.join([self.msg, self.message])

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.to and self.msg
