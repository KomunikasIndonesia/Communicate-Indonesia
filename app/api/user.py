from flask import Flask, jsonify, request
from google.appengine.ext import ndb
import time

app = Flask(__name__)

ROLES = ['hutan_biru', 'farmer']


class User(ndb.Model):
    id = ndb.StringProperty(required=True)
    role = ndb.StringProperty(required=True, choices=set(ROLES))
    phone_number = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty()
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)


@app.route('/v1/users', methods=['PUT'])
def insert():
    try:
        req = request.get_json(force=True)

        new = User()
        new = User(id = req['phone_number'],
                   role = req['role'],
                   phone_number = req['phone_number'],
                   first_name = req['first_name'])

        if 'last_name' in req:
            new.last_name = req['last_name']

        new.key = ndb.Key(User, req['phone_number'])
        new.put()

        msg = 'Successful PUT request'

    except Exception:
        msg = 'Bad PUT request'

    return jsonify({'response': msg})


@app.route('/v1/users/<userid>', methods=['GET'])
def retrieve(userid):
    resp = {'result': {}}

    try:
        user_key = ndb.Key(User, userid)
        data = user_key.get()

        resp['result'] = {
            'id': data.id,
            'role': data.role,
            'phone_number': data.phone_number,
            'first_name': data.first_name,
            'last_name': data.last_name,
            'ts_created': time.mktime(data.ts_created.timetuple()) * 1000,
            'ts_updated': time.mktime(data.ts_updated.timetuple()) * 1000
        }                                           # Timestamp in epoch milis

    except Exception:
        resp['result'] = None

    return jsonify(**resp)
