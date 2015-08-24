# Communicate-Indonesia
This project attempts to connect farmers in Indonesia through sms allowing them to share information about farming patterns and optimize for higher overall gains.

## Setup
This project is currently configured for linux

### Requirements
- Google Appengine python SDK version 1.9.24
- Python version 2.7x

### Default Setup
1. make tool-install
2. make install

### Manual Setup
1. extract google appengine sdk into tmp/google_appengine
2. sudo pip install virtualenv
3. make install

## Common development tasks
- make install : install run + test dependencies
- make server : run appengine dev app server
- make test : run tests
- make flake8 : lint source code

## Configuring config
- Go to http://localhost:8080/v1/config to see configuration
- To set params go to http://localhost:8080/v1/config?update=true&p1=v1&p2=v2 where px and vx are config param and values.
Example http://localhost:8080/v1/config?update=true&admin_username=blah&admin_key=key
