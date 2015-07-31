from flask import Flask, jsonify, request
from google.appengine.ext import ndb
from app.model.user import User
import time

app = Flask(__name__)


@app.route('/v1/users', methods=['PUT'])
def insert():
    resp = {}

    try:
        req = request.get_json(force=True)

        new = User()
        new = User(role=req['role'],
                   phone_number=req['phone_number'],
                   first_name=req['first_name'])

        if 'last_name' in req:
            new.last_name = req['last_name']

        new.put()

        resp['status'] = 'success'

    except Exception, e:
        resp['status'] = 'error'
        resp['message'] = str(e)

    return jsonify(**resp)


@app.route('/v1/users/<userid>', methods=['GET'])
def retrieve(userid):
    resp = {}

    try:
        user_key = ndb.Key('User', int(userid))
        data = user_key.get()

        resp['data'] = {
            'id': str(data.key.id()),
            'role': data.role,
            'phone_number': data.phone_number,
            'first_name': data.first_name,
            'last_name': data.last_name,
            'ts_created': time.mktime(data.ts_created.timetuple()) * 1000,
            'ts_updated': time.mktime(data.ts_updated.timetuple()) * 1000
        }                                           # Timestamp in epoch milis

        resp['status'] = 'success'

    except Exception, e:
        resp['data'] = None
        resp['success'] = 'error'
        resp['message'] = str(e)

    return jsonify(**resp)
