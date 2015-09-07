import logging
from app.api.sms.base_action import OneArgCommand
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
    MULTI_DISTRICT_LIMIT = 5

    def __init__(self, command):
        super(BroadcastAction, self).__init__(command)

    def execute(self):
        user = self.command.sms.user
        words = self.command.msg.split()
        message = self.command.msg
        district = None

        for i in range(self.MULTI_DISTRICT_LIMIT):
            if district:
                message = ' '.join(words[i-1:])
                break
            district_name = ' '.join(words[:i])
            slug = district_name.lower()
            district = District.query(District.slug == slug).get()

        if BROADCAST_ALL in user.permissions:
            # district must be specified
            if self.command.district != EVERYONE and not district:
                logging.info('{} - District {} is unknown'.format(
                    self.command.sms.id, words[0]))
                return _('District {} is unknown').format(words[0])

            if self.command.district == EVERYONE:
                farmers = User.query(User.role == User.ROLE_FARMER).fetch()

            if district:
                farmers = User.query(ndb.AND(
                    User.role == User.ROLE_FARMER,
                    User.district_id == district.key.id())).fetch()

        if BROADCAST_OWN_DISTRICT in user.permissions:
            if self.command.district == EVERYONE:
                words.insert(0, EVERYONE)

            # own district is not specified but valid
            if not district or \
                    (district and district.key.id() != user.district_id):
                message = ' '.join(words)

            farmers = User.query(ndb.AND(
                User.role == User.ROLE_FARMER,
                User.district_id == user.district_id)).fetch()

        phone_numbers = [farmer.phone_number for farmer in farmers]

        if phone_numbers:
            taskqueue.add(
                queue_name=self.QUEUE_NAME,
                url=self.QUEUE_URL,
                payload=json.dumps({'task': {'phone_number': phone_numbers,
                                             'message': message}}))
            return _('Message delivered')
        return _('Message delivery failed')


class BroadcastCommand(OneArgCommand):
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
        EVERYONE,  # en
        'semua'    # in
    ]

    def __init__(self, sms):
        super(BroadcastCommand, self).__init__(sms)
        self.district = None
        self.msg = None

        words = self.message.split()
        if words:
            self.msg = ' '.join(words)

        if words and words[0] in self.TO_ALL:
            self.district = EVERYONE
            self.msg = ' '.join(words[1:])

    def valid(self):
        valid_cmd = super(BroadcastCommand, self).valid()
        return valid_cmd and self.msg
