class Action(object):
    """
    Actions perform operations on command
    """
    def __init__(self, command):
        self.command = command

    def execute(self):
        """
        Do work on the command

        This operation has side effects
        :param Command command: The command
        :return: Each action returns a different response
        """
        pass


class Command(object):
    """
    Command parses raw data into action specific data
    """
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def valid(self):
        """Return true if the raw data is a valid command"""
        pass


class DispatcherError(Exception):
    """
    Generic dispatcher error
    """
    pass


class NoRouteError(DispatcherError):
    """
    Dispatcher could not find a valid route
    """
    pass


class MultipleRouteError(DispatcherError):
    """
    Dispatcher found multiple valid routes
    """
    pass


class Dispatcher(object):
    """
    Dispatcher dispatches actions that match raw data
    """
    def __init__(self):
        self.routes = []

    def route(self, command_class, action_class):
        self.routes.append({
            'command_class': command_class,
            'action_class': action_class
        })

    def dispatch(self, data):
        """
        Executes the action associated to this command.
        :param data: Raw data
        :raises NoRouteError: No route could be found
        :raises MultipleRouteError: Multiple routes were matched
        :return: The return value of the action
        """
        valid_routes = []
        command = None

        for route in self.routes:
            command = route['command_class'](data)
            if command.valid():
                valid_routes.append(route)

        if not valid_routes:
            raise NoRouteError('no routes matched')

        if len(valid_routes) > 1:
            names = [
                '{} : {}'.format(route['command_class'], route['action_class'])
                for route in valid_routes
            ]
            raise MultipleRouteError('multiple routes were matched:\n{}',
                                     '\n'.join(names))

        command = valid_routes[0]['command_class'](data)

        return valid_routes[0]['action_class'](command).execute()
