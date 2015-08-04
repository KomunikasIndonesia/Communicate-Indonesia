from functools import wraps
from flask import json, request, abort
from app.model.config import Config


def enable_json_error(app):
    """Convert errors into json responses"""
    def generic_error_handler(error):
        if not hasattr(error, 'description'):
            return error
        return json.jsonify({'error': error.description}), error.code

    for error in range(400, 420) + range(500, 506):
        app.error_handler_spec[None][error] = generic_error_handler


def jsonify(func):
    """Convert response into json object"""
    @wraps(func)
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        return json.jsonify(response)

    return inner


def ensure_param(name, enums=None):
    """Verify that param is specified"""
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            values = request.args
            if request.method != 'GET':
                values = request.form

            if name not in values:
                abort(400, "{} is required".format(name))

            if enums and not any([values[name] == enum for enum in enums]):
                abort(400, "{} is an invalid {}".format(values[name], name))

            return func(*args, **kwargs)

        return inner

    return decorator


def require_apikey(func):
    """Require an API key to store and get data"""
    @wraps(func)
    def inner(*args, **kwargs):
        keys = Config.query().fetch()
        apikeys = [k.toJson()['apikey'] for k in keys]

        auth = request.authorization

        if not auth or auth.username != 'admin':
            abort(400, "unauthorized access")

        if auth.password not in apikeys:
            abort(400, "invalid apikey")

        return func(*args, **kwargs)

    return inner
