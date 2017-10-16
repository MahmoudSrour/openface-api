from flask import Flask, request, Response
from flask_jsonpify import jsonify

import logging
import datetime

from utils import image_helper as ih
from face_compare import FaceCompare

app = Flask(__name__)

port = 5000
host = '0.0.0.0'

# setup logging
logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.route('/test')
def test():
    logger.info('start test api')
    result = {'TestResult': image_helper.test()}
    return jsonify(result)


@app.route('/health-check')
def healthy_check():
    logger.info('Calling healthy-check api')
    resp = {'message': 'Service up on: %s' % str(datetime.datetime.now())}
    return jsonify(resp)


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    logger.info('Calling compare api')
    if 'img1' not in request.files:
        return "Img1 param missing", 400
    if 'img2' not in request.files:
        return "Img2 param missing", 400
    logger.info('Compare api validatoin: both images found')

    # Define face compare object
    logger.info('Intitiate face comapre object')
    face_compare = FaceCompare(logger)

    logger.info('Intitiate image helper object')
    imageHelper = ih.ImageHelper(logger)
    logger.info('End intitiate image helper object')

    logger.info('calling test method: result %s' % imageHelper.test())

    logger.info('Start reading images from request')

    img1 = imageHelper.get_rgb_img_from_req_file(request.files['img1'])
    img2 = imageHelper.get_rgb_img_from_req_file(request.files['img2'])
    distance = face_compare.compare(img1, img2)
    logger.info("End getting comapre result: {}".format(distance))
    #dat = jsonify({"distance": distance})
    #resp = Response(response=dat, status=200, mimetype="application/json")
    #return resp
    resp = {"distance": distance}
    return jsonify(resp)



if __name__ == '__main__':
    logger.info('start listening on: http://%s:%d ...' % (host, port))
    app.run(host=host, port=port)
