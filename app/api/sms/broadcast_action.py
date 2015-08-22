from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action


class BroadcastAction(Action):
    """
    Execute a broadcast operation
    """
    TO_ALL = [
        'everyone',  # en
        'semua'      # in
    ]

    def __init__(self, command):
        super(BroadcastAction, self).__init__(command)

    def execute(self):
        pass


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

        if sms.user.role == 'hutan_biru':
            self.to = self.args[0]
            self.msg = self.args[1] + self.message

        if sms.user.role == 'farmers':
            if self.args[1]:
                self.to = self.args[0]
                self.msg = self.args[1] + self.message
            else:
                self.to = sms.user.district_id
                self.msg = self.args[0]

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.to and self.msg
