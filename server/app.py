from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify

import logging

app = Flask(__name__)
api = Api(app)

# setup logging
logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

'''
class Test(Resource):
    def get(self):
        logger.info('start get api')
        result = {'TestResult': 'This is just test, Hello from Python API (Flask_RESTFUL)'}
        return jsonify(result)


api.add_resource(Test, '/test')
'''

@app.route('/')
def index():
    return "hello, world!"

if __name__ == '__main__':
    logger.info('start services....')
    app.run(port=5003)