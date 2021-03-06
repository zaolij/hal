import puka
import json
from datetime import datetime
import requests

import urllib
from socket import gaierror

from config import (
    RMQ_HOST, LECHBOT_EVENTS_QUEUE, LECHBOT_NOTIFS_QUEUE, STATUS_GET_URL,
    STATUS_CHANGE_URL, SENSORS_GRAPHITE
)


def get_lechbot_queue(queue_name):
    """
    Return a puka client connected to LechBot's RabbitMQ broker, with given
    queue name acquired
    """
    client = puka.Client(RMQ_HOST)
    client.wait(client.connect())
    client.wait(client.queue_declare(queue=queue_name))
    return client


def lechbot_event(name):
    """
    Emit given event name to LechBot's event queue. It will be translated to
    #urlab if necessary.
    See also: https://github.com/titouanc/lechbot/blob/master/plugins/HAL.rb
    """
    try:
        client = get_lechbot_queue(LECHBOT_EVENTS_QUEUE)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = {
            'time': now,
            'name': name
        }
        client.wait(client.basic_publish(
            exchange='',
            routing_key=LECHBOT_EVENTS_QUEUE,
            body=json.dumps(message)
        ))
    except gaierror:
        pass


def lechbot_notifications():
    client = get_lechbot_queue(LECHBOT_NOTIFS_QUEUE)
    promise = client.basic_consume(queue=LECHBOT_NOTIFS_QUEUE)
    while True:
        result = client.wait(promise)
        data = json.loads(result["body"])
        send_time = datetime.strptime(data['time'], "%Y-%m-%d %H:%M:%S")
        client.basic_ack(result)
        if (datetime.now() - send_time).total_seconds() < 120:
            yield data


def pamela():
    """
    Retrieve pamela data
    """
    try:
        return json.loads(requests.get("http://pamela.urlab.be/mac.json").content)
    except requests.ConnectionError:
        return {
            "color": [],
            "hidden": 0,
            "grey": []
        }


def spaceapi_open():
    try:
        return requests.get(STATUS_CHANGE_URL + "?status=open").status_code == 200
    except requests.ConnectionError:
        return False


def spaceapi_close():
    try:
        return requests.get(STATUS_CHANGE_URL + "?status=close").status_code == 200
    except requests.ConnectionError:
        return False


def spaceapi_isopen():
    try:
        resp = requests.get(STATUS_GET_URL)
        return resp.status_code == 200 and "open" in resp.content
    except:
        return False


class GraphiteEvents:
    def __init__(self, server, prefix=""):
        self.server = server if not server[-1] == "/" else server[:-1]
        self.prefix = prefix

    def send(self, what, tags=[], data=""):
        payload = {
            "what": self.prefix + " " + what,
            "tags": ",".join(tags),
            "data": data
        }

        try:
            r = requests.post("{}/events/".format(self.server), data=json.dumps(payload))
            return r
        except requests.ConnectionError:
            return False

events = GraphiteEvents("http://" + SENSORS_GRAPHITE, "hal")
