import json
import logging
import os

import coloredlogs
import requests
from flask import Flask, Response

USERNAME = os.environ.get('ATOME_API_USERNAME')
PASSWORD = os.environ.get('ATOME_API_PASSWORD')
MOBILE_ID = '6c84a778-841f-4a8f-90eb-a979f8492cfd'
HEADERS = {
    'User-Agent': 'Atome/1.5.3 (com.directenergie.atome; build:0.0.1; iOS 12.4.0) Alamofire/4.8.2',
    'Content-Type': 'application/json',
    'Accept-Language': 'fr-FR;q=1.0, en-US;q=0.9',
    'Accept': '*/*'
}
BASE_URL = 'https://esoftlink.esoftthings.com/api'
CONNECTED = False
ID = None
REFERENCE = None
s = requests.session()

app = Flask(__name__)


@app.route('/live')
def live():
    result, status = get_live()
    return Response(json.dumps(result), mimetype='application/json', status=status)


@app.route('/consumption')
def consumption():
    result, status = get_consumption()
    return Response(json.dumps(result), mimetype='application/json', status=status)


def call_server(url):
    global CONNECTED

    if not CONNECTED and not login():
        return 'Error', 500

    request = s.get(url)

    if request.status_code == 401 or request.status_code == 403:
        CONNECTED = False
        return call_server(url)  # Reconnect

    if request.status_code != 200:
        return 'Error', requests.status_code

    try:
        result = json.loads(request.content)
    except:
        CONNECTED = False
        return call_server(url)  # Reconnect

    return result, 200


def get_live():
    return call_server(f'{BASE_URL}/subscription/{ID}/{REFERENCE}/measure/live.json?mobileId={MOBILE_ID}')


def get_consumption():
    return call_server(f'{BASE_URL}/subscription/{ID}/{REFERENCE}/consumption.json?period=sod')


def login():
    body = {
        'email': USERNAME,
        'plainPassword': PASSWORD,
        'mobileInformation': json.dumps({
            'version': '1.5.3',
            'phoneOS': 'iOs',
            'phoneOSVersion': '12.4',
            'phoneBrand': 'Android',
            'phoneModel': 'iPhone 7',
            'mobileId': MOBILE_ID,
        })  # Can be empty..., maybe good to keep all intact
    }

    request = s.post(f'{BASE_URL}/user/login.json', json=body, headers=HEADERS)

    if request.status_code != 200:
        return False

    result = json.loads(request.content)

    global ID, REFERENCE, CONNECTED
    CONNECTED = True
    ID = result['id']
    REFERENCE = result['subscriptions'][0]['reference']

    return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    coloredlogs.install()

    login()
    app.run(host='0.0.0.0')
