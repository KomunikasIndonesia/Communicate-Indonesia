import logging
from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.user import User
from app.model.district import District
from app.model.permission import BROADCAST_ALL, BROADCAST_OWN_DISTRICT

from app.i18n import _
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import json

EVERYONE = 'everyone'


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
        district = None

        if cmd.send_to != EVERYONE:
            district_name = cmd.send_to
            slug = district_name.lower()
            district = District.query(District.slug == slug).get()

        if BROADCAST_OWN_DISTRICT in user.permissions:
            # send_to as part of message
            if not district or \
                    (district and district.key.id() != user.district_id):
                cmd.msg = ' '.join([cmd.send_to, cmd.msg])

            farmers = User.query(ndb.AND(
                User.role == User.ROLE_FARMER,
                User.district_id == user.district_id)).fetch()

        if BROADCAST_ALL in user.permissions:
            if cmd.send_to != EVERYONE and not district:
                logging.info('{} - District {} is unknown'.format(
                    self.command.sms.id, district_name))
                return _('District {} is unknown').format(district_name)

            if cmd.send_to == EVERYONE:
                farmers = User.query(User.role == User.ROLE_FARMER).fetch()

            if district:
                farmers = User.query(ndb.AND(
                    User.role == User.ROLE_FARMER,
                    User.district_id == district.key.id())).fetch()

        phone_numbers = [farmer.phone_number for farmer in farmers]

        if phone_numbers:
            taskqueue.add(
                queue_name=self.QUEUE_NAME,
                url=self.QUEUE_URL,
                payload=json.dumps({'phone_number': phone_numbers,
                                    'message': cmd.msg}))
            return _('Message sent to {}').format(_(cmd.send_to))
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

    TO_ALL = [
        'everyone',  # en
        'semua'      # in
    ]

    def __init__(self, sms):
        super(BroadcastCommand, self).__init__(sms)
        self.send_to = None  # send_to can be part of message for leader
        self.msg = None

        if self.args[0]:
            self.send_to = self.args[0]
            if self.args[0].lower() in self.TO_ALL:
                self.send_to = EVERYONE

        if self.args[1]:
            self.msg = self.args[1]

        if not self.args[1] and sms.user.role == User.ROLE_DISTRICT_LEADER:
            self.msg = ' '

        if self.message:
            self.msg = ' '.join([self.msg, self.message])

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.send_to and self.msg
