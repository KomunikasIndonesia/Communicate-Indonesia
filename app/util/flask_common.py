from functools import wraps
from flask import json, request, abort
from app.model.config import Config


def enable_json_error(app):
    """Convert errors into json responses"""
    def generic_error_handler(error):
        if hasattr(error, 'code') and error.code == 404:
            error.description = 'The uri "{}" was not found'.format(request.path)

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
        config = Config.query().fetch()[0]
        auth = request.authorization

        if not auth \
            or auth.username != config.admin_username \
                or auth.password != config.admin_apikey:
                    abort(400, "unauthorized access")

        return func(*args, **kwargs)

    return inner
