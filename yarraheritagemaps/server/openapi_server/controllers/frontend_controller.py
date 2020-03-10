import connexion
import six
from openapi_server import util
import flask
from flask import Flask, send_from_directory
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
  app.app.logger.info('frontend_controller.py:PATH')
  return send_from_directory('./app', path)

@app.route('/')
def root():
  app.app.logger.info('frontend_controller.py:INDEX')
  return send_from_directory('./app', 'index.html')

@app.errorhandler(500)
def server_error(e):
  app.app.logger.info('frontend_controller.py:ErrorHandler')
  return 'An internal error occurred [main.py] %s' % e, 500

def go_home():  # noqa: E501
    """home page.
    Displays the index html page # noqa: E501
    :rtype: str
    """
    app.logger.error('frontend_controller.py:INDEX.HTML')
    response = flask.send_from_directory('app', 'index.html')
    response.direct_passthrough = False
    return response

def go_home_terms():  # noqa: E501
    """home page.
    Displays the index html page # noqa: E501
    :rtype: str
    """
    app.logger.error('INDEX.HTML')
    response = flask.send_from_directory('app', 'index.html')
    response.direct_passthrough = False
    return response

def serve_assets(filename):  # noqa: E501
    """angular assets.
    Serve app assets # noqa: E501
    :param filename: 
    :type filename: str
    :rtype: str
    """
    response = flask.send_from_directory('app/assets', filename)
    response.direct_passthrough = False
    return response



def serve_file(filename):  # noqa: E501
    """home page.

    Displays the index html page # noqa: E501

    :param filename: 
    :type filename: str

    :rtype: str
    """
    response = flask.send_from_directory('app', filename)
    response.direct_passthrough = False
    return response

