from flask import Flask, jsonify, request, abort
from google.appengine.ext import ndb
from app.model.user import User, roles
import time

app = Flask(__name__)


def generic_error_handler(error):
    if not hasattr(error, 'description'):
        return error
    return jsonify(error.description), error.code

for error in range(400, 420) + range(500, 506):
    app.error_handler_spec[None][error] = generic_error_handler


def validate(req):
    if not req:
        abort(400, {'error': 'missing request data'})

    props = User._properties
    keys = props.keys()

    for key in keys:
        if props[key]._required:
            if key not in req:
                abort(400, {'error': '{0} is required'.format(key)})

            if isinstance(props[key], ndb.StringProperty) and \
               type(req[key]) not in [str, unicode]:
                    abort(400, {'error': '{0} is not string'.format(key)})

    if req['role'] not in roles:
        abort(400, {'error': 'invalid role, '
                             'should be: {0}'.format(' or '.join(roles))})


@app.route('/v1/users', methods=['PUT'])
def insert():
    req = request.get_json(force=True)
    validate(req)

    new = User(role=req['role'],
               phone_number=req['phone_number'],
               first_name=req['first_name'])

    if 'last_name' in req:
        new.last_name = req['last_name']
    else:
        new.last_name = None

    new.put()
    return jsonify(new.toJson())


@app.route('/v1/users', methods=['GET'])
def fetch():
    phone = request.args.get('phone_number')

    if not phone:
        users = User.query().order(-User.ts_created).fetch()
    else:
        users = User.query(User.phone_number == phone).order(-User.ts_created)

    res = {
        'users': [u.toJson() for u in users] if users else []
    }

    return jsonify(res)


def get_user(userid):
    if not userid or userid == '':
        abort(400, {'error': 'userid is required'})

    userid = int(userid)
    user = User.get_by_id(userid)
    if not user:
        abort(400, {'error': 'user not found'})

    return user


@app.route('/v1/users/<userid>', methods=['GET'])
def retrieve(userid):
    data = get_user(userid)

    res = {
        'id': str(data.key.id()),
        'role': data.role,
        'phone_number': data.phone_number,
        'first_name': data.first_name,
        'last_name': data.last_name,
        'ts_created': int(time.mktime(data.ts_created.timetuple()) * 1000),
        'ts_updated': int(time.mktime(data.ts_updated.timetuple()) * 1000)
    }                                           # Timestamp in epoch milis

    return jsonify(**res)
