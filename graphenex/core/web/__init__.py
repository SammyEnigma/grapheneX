import socket
import secrets
import logging
import webbrowser

from flask import Flask
from flask_socketio import SocketIO

from graphenex.core.utils.helpers import is_valid_port, is_valid_address
from graphenex.core.cli.shell import Shell
from graphenex.core.utils.logcl import GraphenexLogger

logger = GraphenexLogger(__name__)
logging.getLogger('werkzeug').disabled = True
app = Flask(__name__)
app.config['SECRET_KEY'] = '77a98d7971ec94c8aae6dd2d'
app.config['ACCESS_TOKEN'] = secrets.token_urlsafe(6)
socketio = SocketIO(app)
default_addr = ('0.0.0.0', '8080')

from graphenex.core.web.views import *  # noqa
from graphenex.core.web.providers import *  # noqa


def run_server(args=None, exit_shell=True):
    """Run the web server"""

    if args:
        server_params = args.get('host_port', '').split(':') or default_addr
    else:
        server_params = default_addr

    try:
        server_addr, server_port = server_params
        server_port = int(server_port)
    except (ValueError, IndexError):
        logger.error(f"Invalid server parameters: {server_params}")
        return

    if not is_valid_port(server_port):
        logger.error(f"Invalid port specified: {server_port}")
        return

    if not is_valid_address(server_addr):
        logger.error(f"Invalid address specified: {server_addr}")
        return

    logger.info(f"Starting server on http://{server_addr}:{server_port}")

    try:
        if args and args.get('open', False):
            webbrowser.open(f"http://{server_addr}:{server_port}")

        logger.info(f"Your access token: {app.config['ACCESS_TOKEN']}")
        socketio.run(app, host=server_addr, port=server_port, debug=False)
    except socket.error as e:
        if e.errno == 98:
            logger.error(f"{server_addr}:{server_port} is already in use!")
            return
    except KeyboardInterrupt:
        socketio.stop()
        if exit_shell:
            Shell().do_exit(None)
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return
