from flask import Flask, jsonify
import time

app = Flask(__name__)

# To be done:
# - This code is not tested
# - Add authentication
# - Add yaml config
# - Required/optional validation
# - Fetching get response by phone number
# - Add test script for insert/retrieve API
# - Replace dummy with real data/function
# - Generate epoch time for ts_created/updated not required on insert()?
# - Generated id on insert()?

# Dummy data
USERS = [{
    'id': 'ci1',
    'role': 'hutan_biru',
    'phone_number': '1234567',
    'first_name': 'Thomas',
    'last_name': None,
    'ts_created' : 1438141613370,
    'ts_updated' : 1438141613370
},
{
    'id': 'ci2',
    'role': 'farmers',
    'phone_number': '531531',
    'first_name': 'Siti',
    'last_name': 'Nurbaya',
    'ts_created' : 1438141741970,
    'ts_updated' : 1438141741970
},
{
    'id': 'ci3',
    'role': 'hutan_biru',
    'phone_number': '23452345',
    'first_name': 'Ratna',
    'last_name': 'Fadilah',
    'ts_created' : 1438141750730,
    'ts_updated' : 1438141750730
}]


@app.route('v1/users', methods=['PUT'])
def insert():
    data = {
        'role': request.values.get('role'),
        'phone_number': request.values.get('phone_number'),
        'first_name': request.values.get('first_name'),
        'last_name': request.values.get('last_name') or None
    }

    # Store data
    # insert_funct()
    msg = 'Successful PUT request'

    return jsonify({'code':201, 'response':msg})

@app.route('v1/users/<userid>', methods=['GET'])
def retrieve(userid):
    # Getting dummy data
    users = USERS

    response = None

    for user in users:
        if userid in user['id']:
            response = user

    return jsonify({'response':response})
