import connexion
from flask import Flask, send_from_directory
from flask_cors import CORS
import logging
import os

logging.basicConfig(level=logging.INFO)

# ... other import statements ...

# creating the Flask application

def post_greeting(name: str) -> str:
    return 'Hello {name}'.format(name=name)


app = connexion.FlaskApp(__name__, specification_dir='openapi_server/')

#connexion_app = connexion.App(__name__)

app.add_api('openapi/openapi.yaml', arguments={'title': 'Hello World Example'})
CORS(app.app)


if __name__ == '__main__':
  # This code only runs when running locally. 
  # When deployed to cloud, A webserver process serves the app.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
    "C:/yarrascrapy/yarraplanning/yarraheritagemaps/server/secrets/yarrascrape-b30815080477.json"
    app.run(host='127.0.0.1', port=8080, debug=True)

'''    
@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
  app.app.logger.error('Index.HTML')
  return send_from_directory('./app', path)

@app.route('/')
def root():
  assert('here')
  return send_from_directory('./app', 'index.html')
@app.errorhandler(500)
def server_error(e):
  return 'An internal error occurred [main.py] %s' % e, 500
'''