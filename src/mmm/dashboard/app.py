import json
import logging
import socket

from flask import Flask, request

from mmm.config import settings


logger = logging.getLogger(__name__)
application = Flask(__name__)


def encode_bot_command(bot_id, command):
    return bytes(json.dumps({'bot_id': bot_id, 'command': command}), encoding="utf-8")


@application.route('/control-bot', methods=['POST'])
def index():
    data = request.json
    command, bot_id = data.get('command'), data.get('bot_id')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = settings.STRATEGY_SERVER['HOST']
    port = settings.STRATEGY_SERVER['PORT']
    try:
        sock.connect((host, port))
        sock.sendall(encode_bot_command(bot_id, int(command)))
    except Exception as e:
        logger.exception(e)
    else:
        return 'success.'
